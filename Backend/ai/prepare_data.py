import os
import random
from datasets import load_dataset, Dataset
from backend.ai.tnau_qa import TNAU_QA_PAIRS

CROPS = ["paddy", "rice", "groundnut", "sugarcane", "maize"]

def format_chatml(question, answer):
    return {
        "text": f"<|im_start|>user\n{question}<|im_end|>\n<|im_start|>assistant\n{answer}<|im_end|>"
    }

def prepare_training_dataset():
    print("[Data Prep] Ingesting AI71ai/agrillm-train-146k dataset...")
    # Load first 25,000 rows for high-speed processing
    raw_ds = load_dataset("AI71ai/agrillm-train-146k", split="train[:25000]")

    formatted_rows = []

    # Filter for targeted regional crops
    for row in raw_ds:
        turns = row.get("turns", [])
        if turns and len(turns) >= 1:
            user_msg = turns[0].get("user", "")
            assistant_msg = turns[0].get("assistant", "")
            text_block = (str(user_msg) + " " + str(assistant_msg)).lower()

            if any(crop in text_block for crop in CROPS):
                formatted_rows.append(format_chatml(user_msg, assistant_msg))

    # Cap at 3,500 samples for optimal 20-minute training times
    if len(formatted_rows) > 3500:
        random.seed(42)
        formatted_rows = random.sample(formatted_rows, 3500)

    # Append manual TNAU ground-truth pairs
    for pair in TNAU_QA_PAIRS:
        formatted_rows.append(format_chatml(pair["question"], pair["answer"]))

    random.shuffle(formatted_rows)
    final_ds = Dataset.from_list(formatted_rows)
    
    output_path = os.path.join(os.path.dirname(__file__), "..", "agritwin_dataset")
    final_ds.save_to_disk(output_path)
    print(f"[Data Prep] SUCCESS: Prepared {len(final_ds)} samples and cached to '{output_path}'.")

if __name__ == "__main__":
    prepare_training_dataset()