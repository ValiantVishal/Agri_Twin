import os
import json
import random
from datasets import Dataset, load_dataset
from tnau_qa import TNAU_QA_PAIRS

SYSTEM_PROMPT_ENGLISH = "You are an agricultural assistant for AgriTwin. Respond ONLY in clear, accurate English."
SYSTEM_PROMPT_TAMIL = "நீ ஒரு தமிழக கிராமப்புற விவசாய உதவியாளர். விவசாயிகளின் கேள்விகளுக்கு எளிய முறையில், துல்லியமான தமிழ் மொழியில் பதில் அளிக்கவும்."


def format_chatml(question, answer, system_prompt=SYSTEM_PROMPT_ENGLISH):
    return {
        "text": (
            f"<|im_start|>system\n{system_prompt}<|im_end|>\n"
            f"<|im_start|>user\n{question}<|im_end|>\n"
            f"<|im_start|>assistant\n{answer}<|im_end|>"
        )
    }


# ==============================================================================
# 1. NEW FUNCTION: Ingest English Agricultural QA from Hugging Face
# ==============================================================================
def load_english_hf_datasets(sample_limit=3500):
    formatted_en_rows = []
    print("[Data Prep] Ingesting English Agri QA ('KisanVaani/agriculture-qa-english-only') from Hugging Face...")
    try:
        ds_en = load_dataset("KisanVaani/agriculture-qa-english-only", split="train")
        for row in ds_en:
            q = row.get("question") or row.get("questions") or row.get("input")
            a = row.get("answer") or row.get("answers") or row.get("output")
            if q and a:
                formatted_en_rows.append(format_chatml(str(q).strip(), str(a).strip(), SYSTEM_PROMPT_ENGLISH))
        
        print(f"[Data Prep] Loaded {len(formatted_en_rows)} English Agri QA samples.")
        
        # Subsample to keep dataset balanced across English & Tamil
        if len(formatted_en_rows) > sample_limit:
            random.seed(42)
            formatted_en_rows = random.sample(formatted_en_rows, sample_limit)
            print(f"[Data Prep] Subsampled English set to {sample_limit} balanced samples.")

    except Exception as e:
        print(f"[Data Prep Notice] Skipping English HF dataset: {e}")

    return formatted_en_rows


# ==============================================================================
# 2. FUNCTION: Ingest Tamil Agri QA & Dialect Datasets from Hugging Face
# ==============================================================================
def load_tamil_hf_datasets():
    formatted_ta_rows = []

    # A. Ingest Kobi-01/tamil_agriculture_QA
    print("[Data Prep] Ingesting Tamil Agri QA ('Kobi-01/tamil_agriculture_QA') from Hugging Face...")
    try:
        ds_ta = load_dataset("Kobi-01/tamil_agriculture_QA", split="train")
        for row in ds_ta:
            q = row.get("question") or row.get("instruction")
            a = row.get("answer") or row.get("output")
            if q and a:
                formatted_ta_rows.append(format_chatml(str(q).strip(), str(a).strip(), SYSTEM_PROMPT_TAMIL))
        print(f"[Data Prep] Loaded {len(formatted_ta_rows)} Tamil Agri QA samples.")
    except Exception as e:
        print(f"[Data Prep Notice] Skipping 'Kobi-01/tamil_agriculture_QA': {e}")

    # B. Ingest sanujen/Tamil-Colloquial-Standard-Parlance-Corpus
    print("[Data Prep] Ingesting Tamil Dialect Corpus ('sanujen/Tamil-Colloquial-Standard-Parlance-Corpus') from Hugging Face...")
    try:
        ds_colloquial = load_dataset("sanujen/Tamil-Colloquial-Standard-Parlance-Corpus", split="train")
        count = 0
        for row in ds_colloquial:
            std = row.get("standard")
            colloq = row.get("colloquial")
            if std and colloq:
                formatted_ta_rows.append(format_chatml(str(std).strip(), str(colloq).strip(), SYSTEM_PROMPT_TAMIL))
                count += 1
        print(f"[Data Prep] Loaded {count} Tamil Colloquial Dialect samples.")
    except Exception as e:
        print(f"[Data Prep Notice] Skipping 'sanujen/Tamil-Colloquial-Standard-Parlance-Corpus': {e}")

    return formatted_ta_rows


# ==============================================================================
# 3. MAIN PREPARATION PIPELINE
# ==============================================================================
def prepare_training_dataset():
    all_rows = []

    # 1. Fetch English Agri QA
    english_rows = load_english_hf_datasets(sample_limit=3500)
    all_rows.extend(english_rows)

    # 2. Fetch Tamil Agri QA + Colloquial Dialect Data
    tamil_rows = load_tamil_hf_datasets()
    all_rows.extend(tamil_rows)

    # 3. Append core TNAU pairs
    print("[Data Prep] Appending TNAU domain rules...")
    for pair in TNAU_QA_PAIRS:
        prompt_sys = SYSTEM_PROMPT_TAMIL if any("\u0b80" <= c <= "\u0bff" for c in pair["question"]) else SYSTEM_PROMPT_ENGLISH
        all_rows.append(format_chatml(pair["question"], pair["answer"], prompt_sys))

    # 4. Shuffle all sources together to build a multi-turn bilingual dataset
    random.seed(42)
    random.shuffle(all_rows)

    print("\n[Data Prep] Sample formatted example:")
    print(all_rows[0]["text"])

    # 5. Convert to Hugging Face Dataset & Cache to disk
    final_ds = Dataset.from_list(all_rows)

    output_path = os.path.normpath(os.path.join(os.path.dirname(__file__), "agritwin_dataset"))
    final_ds.save_to_disk(output_path)
    print(f"\n[Data Prep] SUCCESS: Prepared {len(final_ds)} multi-source samples and saved to '{output_path}'.")


if __name__ == "__main__":
    prepare_training_dataset()