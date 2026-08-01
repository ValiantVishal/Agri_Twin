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


def _generate(prompt: str, system_prompt: str = None, max_new_tokens: int = 300) -> str:
    """Core LLM generator using Qwen chat formatting to prevent repetition and hallucinated script."""
    if model is None or tokenizer is None:
        return "Error: AI model is not loaded."

    if system_prompt is None:
        system_prompt = "You are an agricultural assistant for AgriTwin. You MUST respond ONLY in clear English or standard Tamil."

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": prompt}
    ]

    # Format using Qwen chat template tags
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
            repetition_penalty=1.25,  # Stops word loops like "sqlite"
            do_sample=True,
            pad_token_id=tokenizer.eos_token_id
        )

    # Slice out input tokens to retrieve response
    input_length = inputs["input_ids"].shape[1]
    decoded = tokenizer.decode(outputs[0][input_length:], skip_special_tokens=True)
    return decoded.strip()


def get_fertilizer_recommendation(crop: str, area_acres: float) -> dict:
    """Non-LLM deterministic calculations to prevent dosage hallucinations."""
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
    """Answers farmer questions based on plot history."""
    system_prompt = (
        "You are an agricultural assistant for AgriTwin. "
        "Respond strictly in clear English or standard Tamil based on the question."
    )
    
    logs_formatted = "\n".join(f"- {log}" for log in logs) if logs else "No past observations recorded."
    user_prompt = f"""You are answering questions for plot '{plot_id}'.

Logged field observations:
{logs_formatted}

User Question: "{question}"

Instructions:
1. Answer strictly using only the field observations above.
2. If the information isn't available, state that clearly."""

    return _generate(user_prompt, system_prompt=system_prompt)


def get_seasonal_advisory(month: str, logs: list[str]) -> str:
    """Generates seasonal irrigation advice."""
    m_key = month.lower().strip()
    rainfall = MONTHLY_RAINFALL_MM.get(m_key)

    if rainfall is None:
        return f"No historical climate data available for '{month}'."

    system_prompt = "You are an agricultural assistant providing irrigation and crop care advice in English or Tamil."
    logs_text = "\n".join(f"- {log}" for log in logs) if logs else "No plot history notes logged."
    
    user_prompt = f"""Historical average rainfall for {m_key.capitalize()} is {rainfall} mm.
Farmer's past field notes:
{logs_text}

Provide concise irrigation and maintenance advice for {m_key.capitalize()} based on this data."""

    return _generate(user_prompt, system_prompt=system_prompt)


def get_daily_brief_ai(profile_summary: str) -> str:
    """Generates daily task recommendations in Tamil."""
    system_prompt = (
        "நீ ஒரு விவசாய உதவியாளர். தமிழ் மொழியில் மட்டும் சுருக்கமான, "
        "விவசாயி உடனடியாக செய்யக்கூடிய அறிவுரைகளை பட்டியலாக (bullet points) வழங்கவும்."
    )
    return _generate(profile_summary, system_prompt=system_prompt)