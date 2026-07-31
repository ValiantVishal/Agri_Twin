import os
import json
import random
from datasets import Dataset
from huggingface_hub import hf_hub_download
from tnau_qa import TNAU_QA_PAIRS

CROPS = ["paddy", "rice", "groundnut", "sugarcane", "maize"]

def format_chatml(question, answer):
    return {
        "text": f"<|im_start|>user\n{question}<|im_end|>\n<|im_start|>assistant\n{answer}<|im_end|>"
    }

def load_agrillm_safely(limit=25000):
    print("[Data Prep] Downloading raw 'agrillm-train-146k' directly from HuggingFace Hub...")
    # Fetch file directly to bypass PyArrow schema mismatch errors
    file_path = hf_hub_download(
        repo_id="AI71ai/agrillm-train-146k", 
        filename="train.jsonl", 
        repo_type="dataset"
    )
    
    rows = []
    print(f"[Data Prep] Parsing first {limit} rows safely...")
    with open(file_path, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f):
            if i >= limit:
                break
            try:
                data = json.loads(line)
                rows.append(data)
            except Exception:
                continue
                
    return rows

def prepare_training_dataset():
    print("[Data Prep] Ingesting AI71ai/agrillm-train-146k dataset...")
    
    # Load first 25,000 rows without PyArrow schema errors
    raw_rows = load_agrillm_safely(limit=25000)

    formatted_rows = []

    # Filter for targeted regional crops
    for row in raw_rows:
        turns = row.get("turns", [])
        if turns and isinstance(turns, list) and len(turns) >= 1:
            turn = turns[0]
            if isinstance(turn, dict):
                user_msg = turn.get("user", "")
                assistant_msg = turn.get("assistant", "")
                
                # Ensure text is string (handles cases where assistant was an object/dict)
                user_str = str(user_msg) if user_msg else ""
                assistant_str = str(assistant_msg) if assistant_msg else ""
                
                text_block = (user_str + " " + assistant_str).lower()

                if any(crop in text_block for crop in CROPS):
                    formatted_rows.append(format_chatml(user_str, assistant_str))

    print(f"[Data Prep] Filtered {len(formatted_rows)} matching regional crop samples.")

    # Cap at 3,500 samples for optimal 20-minute training times
    if len(formatted_rows) > 3500:
        random.seed(42)
        formatted_rows = random.sample(formatted_rows, 3500)

    # Append manual TNAU ground-truth pairs
    for pair in TNAU_QA_PAIRS:
        formatted_rows.append(format_chatml(pair["question"], pair["answer"]))

    random.shuffle(formatted_rows)
    final_ds = Dataset.from_list(formatted_rows)
    
    output_path = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "agritwin_dataset"))
    final_ds.save_to_disk(output_path)
    print(f"[Data Prep] SUCCESS: Prepared {len(final_ds)} samples and cached to '{output_path}'.")

if __name__ == "__main__":
    prepare_training_dataset()