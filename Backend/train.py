import os
import torch
from datasets import load_from_disk
from trl import SFTTrainer
from transformers import TrainingArguments

DATASET_PATH = os.path.join("backend", "agritwin_dataset")
OUTPUT_PATH = os.path.join("backend", "agritwin_finetuned")

def train():
    if not os.path.exists(DATASET_PATH):
        raise FileNotFoundError(f"Dataset path '{DATASET_PATH}' not found. Run prepare_data.py first!")

    print("[Training] Loading cached dataset...")
    dataset = load_from_disk(DATASET_PATH)

    print("[Training] Initializing Qwen/Qwen2.5-3B-Instruct model...")
    try:
        from unsloth import FastLanguageModel
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

    trainer = SFTTrainer(
        model=model,
        tokenizer=tokenizer,
        train_dataset=dataset,
        dataset_text_field="text",
        max_seq_length=2048,
        args=TrainingArguments(
            per_device_train_batch_size=2,
            gradient_accumulation_steps=4,
            warmup_steps=10,
            num_train_epochs=2,
            learning_rate=2e-4,
            fp16=not torch.cuda.is_bf16_supported(),
            bf16=torch.cuda.is_bf16_supported(),
            logging_steps=10,
            output_dir="training_outputs",
            save_strategy="epoch"
        )
    )

    print("[Training] Training in progress...")
    trainer.train()

    print(f"[Training] Saving adapter weights to '{OUTPUT_PATH}'...")
    model.save_pretrained(OUTPUT_PATH)
    tokenizer.save_pretrained(OUTPUT_PATH)
    print("[Training] SUCCESS: Model fine-tuning complete!")

if __name__ == "__main__":
    train()