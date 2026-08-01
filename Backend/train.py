from unsloth import FastLanguageModel, is_bfloat16_supported
import os
import torch
from datasets import load_from_disk
from transformers import DataCollatorForSeq2Seq
from trl import SFTTrainer, SFTConfig

# ------------------------------------------------------------------------------
# 1. SETUP PARAMETERS
# ------------------------------------------------------------------------------
MAX_SEQ_LENGTH = 2048
MODEL_NAME = "unsloth/Qwen2.5-3B-Instruct"
DATASET_PATH = os.path.normpath(os.path.join(os.path.dirname(__file__), "agritwin_dataset"))
OUTPUT_DIR = os.path.normpath(os.path.join(os.path.dirname(__file__), "agritwin_fine_tuned"))

def main():
    print(f"[Train] Loading pre-processed dataset from: {DATASET_PATH}")
    dataset = load_from_disk(DATASET_PATH)
    print(f"[Train] Total dataset size: {len(dataset)} samples")

    # 2. LOAD UNSLOTH MODEL & TOKENIZER
    model, tokenizer = FastLanguageModel.from_pretrained(
        model_name=MODEL_NAME,
        max_seq_length=MAX_SEQ_LENGTH,
        dtype=None,             # Auto-detects precision (FP16 / BF16)
        load_in_4bit=True,      # 4-bit QLoRA quant
    )

    # Target standard projection layers
    model = FastLanguageModel.get_peft_model(
        model,
        r=16,
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
        lora_alpha=16,
        lora_dropout=0,         # Unsloth optimized dropout rate
        bias="none",
        use_gradient_checkpointing="unsloth",
        random_state=42,
    )

    # 3. CONFIGURE SFT TRAINER
    trainer = SFTTrainer(
        model=model,
        processing_class=tokenizer,
        train_dataset=dataset,
        data_collator=DataCollatorForSeq2Seq(tokenizer=tokenizer),
        args=SFTConfig(
            dataset_text_field="text",
            max_length=MAX_SEQ_LENGTH,
            dataset_num_proc=1,      # Safe for Windows multiprocessing
            packing=False,
            eos_token=tokenizer.eos_token,
            per_device_train_batch_size=2,
            gradient_accumulation_steps=4,
            warmup_steps=10,
            max_steps=300,
            learning_rate=2e-4,
            fp16=not is_bfloat16_supported(),
            bf16=is_bfloat16_supported(),
            logging_steps=10,
            optim="adamw_8bit",
            weight_decay=0.01,
            lr_scheduler_type="linear",
            seed=42,
            output_dir=OUTPUT_DIR,
            save_strategy="steps",
            save_steps=100,
        ),
    )

    # 4. START TRAINING
    print("\n[Train] Starting AgriTwin Fine-Tuning...")
    trainer.train()

    # 5. SAVE LOA ADAPTERS
    print(f"\n[Train] Saving fine-tuned LoRA weights to '{OUTPUT_DIR}'...")
    model.save_pretrained(OUTPUT_DIR)
    tokenizer.save_pretrained(OUTPUT_DIR)

    print("\n[Train] SUCCESS: AgriTwin fine-tuning complete!")

if __name__ == "__main__":
    main()