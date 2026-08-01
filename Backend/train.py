try:
    from unsloth import FastLanguageModel
    HAS_UNSLOTH = True
except ImportError:
    HAS_UNSLOTH = False

import os
import torch
from datasets import load_from_disk
from trl import SFTTrainer, SFTConfig

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_PATH = os.path.join(BASE_DIR, "agritwin_dataset")
OUTPUT_PATH = os.path.join(BASE_DIR, "agritwin_finetuned")


def train():
    if not os.path.exists(DATASET_PATH):
        raise FileNotFoundError(f"Dataset path '{DATASET_PATH}' not found. Run prepare_data.py first!")

    print("[Training] Loading cached dataset...")
    dataset = load_from_disk(DATASET_PATH)
    print(f"[Training] Loaded {len(dataset)} examples.")
    print("[Training] Sample example:\n", dataset[0]["text"][:500])

    print("[Training] Initializing Qwen/Qwen2.5-3B-Instruct model...")
    is_unsloth_model = False

    try:
        model, tokenizer = FastLanguageModel.from_pretrained(
            model_name="Qwen/Qwen2.5-3B-Instruct",
            max_seq_length=2048,
            load_in_4bit=True
        )
        model = FastLanguageModel.get_peft_model(
            model,
            r=16,
            target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
            lora_alpha=16,
            lora_dropout=0,
            bias="none",
            use_gradient_checkpointing="unsloth",
        )
        is_unsloth_model = True
        print("[Training] Loaded successfully using Unsloth acceleration.")
    except Exception as e:
        print(f"[Training Notice] Unsloth load skipped ({e}). Falling back to standard PeftModel...")
        from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
        from peft import LoraConfig, get_peft_model

        bnb_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=torch.float16
        )
        base_model = AutoModelForCausalLM.from_pretrained(
            "Qwen/Qwen2.5-3B-Instruct",
            quantization_config=bnb_config,
            device_map="auto"
        )
        tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen2.5-3B-Instruct")
        lora_config = LoraConfig(
            r=16, lora_alpha=16,
            target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
            lora_dropout=0, bias="none", task_type="CAUSAL_LM"
        )
        model = get_peft_model(base_model, lora_config)
        is_unsloth_model = False

    if tokenizer.pad_token is None:
        print("[Training] pad_token was None -- setting pad_token = eos_token")
        tokenizer.pad_token = tokenizer.eos_token
        model.config.pad_token_id = tokenizer.pad_token_id

    im_end_id = tokenizer.convert_tokens_to_ids("<|im_end|>")
    print(f"[Training] <|im_end|> token id: {im_end_id} (should NOT be unk_token_id={tokenizer.unk_token_id})")
    if im_end_id == tokenizer.unk_token_id:
        raise ValueError(
            "<|im_end|> is not recognized as a special token. Training text formatting "
            "will not match how the model expects chat turns to end."
        )

    sft_config = SFTConfig(
        dataset_text_field="text",
        max_seq_length=2048,
        dataset_num_proc=2,
        per_device_train_batch_size=2,
        gradient_accumulation_steps=4,
        warmup_steps=10,
        num_train_epochs=1,
        learning_rate=2e-4,
        fp16=not torch.cuda.is_bf16_supported(),
        bf16=torch.cuda.is_bf16_supported(),
        logging_steps=10,
        output_dir=os.path.join(BASE_DIR, "training_outputs"),
        save_strategy="no",
        save_total_limit=0,
        optim="adamw_8bit"
    )

    trainer = SFTTrainer(
        model=model,
        processing_class=tokenizer,
        train_dataset=dataset,
        args=sft_config,
    )

    print("[Training] Training in progress...")
    trainer.train()

    print(f"[Training] Merging LoRA weights and saving full model to '{OUTPUT_PATH}'...")
    os.makedirs(OUTPUT_PATH, exist_ok=True)

    if is_unsloth_model:
        model.save_pretrained_merged(OUTPUT_PATH, tokenizer, save_method="merged_4bit")
    else:
        merged_model = model.merge_and_unload()
        merged_model.save_pretrained(OUTPUT_PATH)
        tokenizer.save_pretrained(OUTPUT_PATH)

    print("[Training] SUCCESS: Model fine-tuning complete and saved.")

    print("[Training] Running post-training sanity check...")
    _sanity_check(OUTPUT_PATH)


def _sanity_check(model_path: str):
    if HAS_UNSLOTH:
        test_model, test_tokenizer = FastLanguageModel.from_pretrained(
            model_name=model_path, max_seq_length=2048, load_in_4bit=True
        )
        FastLanguageModel.for_inference(test_model)
    else:
        from transformers import AutoModelForCausalLM, AutoTokenizer
        test_model = AutoModelForCausalLM.from_pretrained(model_path, device_map="auto")
        test_tokenizer = AutoTokenizer.from_pretrained(model_path)

    im_end_id = test_tokenizer.convert_tokens_to_ids("<|im_end|>")
    eos_ids = [test_tokenizer.eos_token_id]
    if im_end_id != test_tokenizer.unk_token_id:
        eos_ids.append(im_end_id)

    messages = [
        {"role": "system", "content": "You are an agricultural assistant for AgriTwin. Respond only in clear English."},
        {"role": "user", "content": "What is the recommended urea dosage for paddy?"}
    ]
    inputs = test_tokenizer.apply_chat_template(
        messages, tokenize=True, add_generation_prompt=True, return_tensors="pt", return_dict=True
    ).to("cuda")

    with torch.no_grad():
        outputs = test_model.generate(
            input_ids=inputs["input_ids"],
            attention_mask=inputs["attention_mask"],
            max_new_tokens=150,
            temperature=0.3,
            top_p=0.9,
            repetition_penalty=1.15,
            do_sample=True,
            pad_token_id=test_tokenizer.eos_token_id,
            eos_token_id=eos_ids,
        )
    result = test_tokenizer.decode(outputs[0][inputs["input_ids"].shape[1]:], skip_special_tokens=True)
    print("\n[Sanity Check] Model output for test question:")
    print(result)
    print("\n[Sanity Check] If this looks clean and stops naturally, training succeeded.")
    print("[Sanity Check] If you see '#' loops or garbled text, do NOT proceed to integration -- debug first.\n")


if __name__ == "__main__":
    train()