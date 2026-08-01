import os
import torch
from unsloth import FastLanguageModel

# Relative imports
from .crop_data import CROP_DATA
from .climate_data import MONTHLY_RAINFALL_MM

ADAPTER_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "agritwin_finetuned"))

print(f"[AgriTwin Engine] Initializing model from: {ADAPTER_DIR}")

try:
    model, tokenizer = FastLanguageModel.from_pretrained(
        model_name=ADAPTER_DIR,
        max_seq_length=2048,
        load_in_4bit=True
    )
    model.eval()
    print("[AgriTwin Engine] SUCCESS: Model loaded and ready for inference.")
except Exception as e:
    print(f"[AgriTwin Engine] Failed to load model: {e}")
    model, tokenizer = None, None


def _generate_with_chat_template(system_prompt: str, user_prompt: str, max_new_tokens: int = 300) -> str:
    """Helper to format prompts into Qwen chat structure to avoid repetition loops."""
    if model is None or tokenizer is None:
        return "Error: AI model is not loaded."

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]

    # Convert to Qwen chat format
    inputs = tokenizer.apply_chat_template(
        messages,
        tokenize=True,
        add_generation_prompt=True,
        return_tensors="pt",
        return_dict=True
    ).to("cuda")

    with torch.no_grad():
        outputs = model.generate(
            input_ids=inputs["input_ids"],
            attention_mask=inputs["attention_mask"],
            max_new_tokens=max_new_tokens,
            temperature=0.3,
            top_p=0.9,
            repetition_penalty=1.25,  # High repetition penalty prevents loops like "sqlite sqlite"
            do_sample=True,
            pad_token_id=tokenizer.eos_token_id
        )

    # Extract only newly generated tokens
    input_len = inputs["input_ids"].shape[1]
    decoded = tokenizer.decode(outputs[0][input_len:], skip_special_tokens=True)
    return decoded.strip()


def query_farm_memory(plot_id: str, question: str, logs: list[str]) -> str:
    system_prompt = "You are an agricultural assistant for AgriTwin. You MUST respond ONLY in Tamil or English."
    
    logs_formatted = "\n".join(f"- {log}" for log in logs) if logs else "No observations logged."
    user_prompt = f"""Plot: '{plot_id}'
Field Notes:
{logs_formatted}

Question: "{question}"
Provide a clear answer in Tamil or English."""

    return _generate_with_chat_template(system_prompt, user_prompt)


def get_daily_brief_ai(profile_summary: str) -> str:
    """Used for daily recommendations."""
    system_prompt = "நீ ஒரு விவசாய உதவியாளர். தமிழ் மொழியில் மட்டும் சுருக்கமான அறிவுரைகளை வழங்கவும்."
    return _generate_with_chat_template(system_prompt, profile_summary)