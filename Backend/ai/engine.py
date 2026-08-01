import os
import torch
from unsloth import FastLanguageModel

from .crop_data import CROP_DATA
from .climate_data import MONTHLY_RAINFALL_MM

# FIXED: Aligned directory name with train.py (agritwin_fine_tuned)
ADAPTER_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "agritwin_fine_tuned"))

print(f"[AgriTwin Engine] Initializing fine-tuned model from: {ADAPTER_DIR}")

try:
    model, tokenizer = FastLanguageModel.from_pretrained(
        model_name=ADAPTER_DIR,
        max_seq_length=2048,
        load_in_4bit=True
    )
    FastLanguageModel.for_inference(model)
    model.eval()

    _eos_ids = [tokenizer.eos_token_id]
    _im_end_id = tokenizer.convert_tokens_to_ids("<|im_end|>")
    if _im_end_id is not None and _im_end_id != tokenizer.unk_token_id:
        _eos_ids.append(_im_end_id)
    print(f"[AgriTwin Engine] EOS token ids in use: {_eos_ids}")

    print("[AgriTwin Engine] SUCCESS: Fine-tuned model loaded and ready for inference.")
except Exception as e:
    print(f"[AgriTwin Engine] Failed to load model from '{ADAPTER_DIR}': {e}")
    model, tokenizer, _eos_ids = None, None, None


def _generate(prompt: str, system_prompt: str = None, max_new_tokens: int = 300) -> str:
    if model is None or tokenizer is None:
        return "Error: AI model is not loaded. Ensure training is completed."

    if system_prompt is None:
        # Check if the prompt contains Tamil script characters
        is_tamil = any("\u0b80" <= c <= "\u0bff" for c in prompt)
        system_prompt = (
            "நீ ஒரு தமிழக கிராமப்புற விவசாய உதவியாளர். விவசாயிகளின் கேள்விகளுக்கு எளிய முறையில், துல்லியமான தமிழ் மொழியில் பதில் அளிக்கவும்."
            if is_tamil
            else "You are an agricultural assistant for AgriTwin. Respond ONLY in clear, accurate English."
        )

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": prompt}
    ]

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
            do_sample=False,
            pad_token_id=tokenizer.eos_token_id,
            eos_token_id=_eos_ids,
        )

    input_length = inputs["input_ids"].shape[1]
    decoded = tokenizer.decode(outputs[0][input_length:], skip_special_tokens=True)
    return decoded.strip()


def get_fertilizer_recommendation(crop: str, area_acres: float) -> dict:
    crop_key = crop.lower().strip()
    if crop_key not in CROP_DATA:
        return {"error": f"Crop '{crop}' not found. Supported: {list(CROP_DATA.keys())}"}

    base = CROP_DATA[crop_key]
    return {
        "crop": crop_key,
        "area_acres": area_acres,
        "seed_kg": round(base["seed_kg_per_acre"] * area_acres, 2),
        "urea_kg": round(base["urea_kg_per_acre"] * area_acres, 2),
        "dap_kg": round(base["dap_kg_per_acre"] * area_acres, 2),
        "potash_kg": round(base["potash_kg_per_acre"] * area_acres, 2),
        "source": base["source"]
    }


def query_farm_memory(plot_id: str, question: str, logs: list[str]) -> str:
    logs_formatted = "\n".join(f"- {log}" for log in logs) if logs else "No past observations recorded."
    user_prompt = f"""You are answering questions for plot '{plot_id}'.

Logged field observations:
{logs_formatted}

User Question: "{question}"

Instructions:
1. Answer strictly using only the field observations above.
2. If the information isn't available, state that clearly."""

    return _generate(user_prompt)


def get_seasonal_advisory(month: str, logs: list[str]) -> str:
    m_key = month.lower().strip()
    rainfall = MONTHLY_RAINFALL_MM.get(m_key)

    if rainfall is None:
        return f"No historical climate data available for '{month}'."

    logs_text = "\n".join(f"- {log}" for log in logs) if logs else "No plot history notes logged."

    user_prompt = f"""Historical average rainfall for {m_key.capitalize()} is {rainfall} mm.
Farmer's past field notes:
{logs_text}

Provide concise irrigation and maintenance advice for {m_key.capitalize()} based on this data."""

    return _generate(user_prompt)


def get_daily_brief_ai(profile_summary: str) -> str:
    system_prompt = (
        "நீ ஒரு விவசாய உதவியாளர். தமிழ் மொழியில் மட்டும் சுருக்கமான, "
        "விவசாயி உடனடியாக செய்யக்கூடிய அறிவுரைகளை பட்டியலாக (bullet points) வழங்கவும்."
    )
    return _generate(profile_summary, system_prompt=system_prompt)