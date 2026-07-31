import os
import torch
from unsloth import FastLanguageModel

# Relative imports to work regardless of module path execution
from .crop_data import CROP_DATA
from .climate_data import MONTHLY_RAINFALL_MM

ADAPTER_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "agritwin_finetuned"))

print(f"[AgriTwin Engine] Initializing model from: {ADAPTER_DIR}")

# Load seamlessly using Unsloth (perfect for offline local directories)
try:
    model, tokenizer = FastLanguageModel.from_pretrained(
        model_name=ADAPTER_DIR,
        max_seq_length=2048,
        load_in_4bit=True
    )
    FastLanguageModel.for_inference(model)
    print("[AgriTwin Engine] SUCCESS: Model loaded and ready for inference.")
except Exception as e:
    print(f"[AgriTwin Engine] Failed to load model: {e}")
    model, tokenizer = None, None

def _generate(prompt: str, max_new_tokens: int = 250) -> str:
    if model is None or tokenizer is None:
        return "Error: AI model is not loaded."

    messages = [{"role": "user", "content": prompt}]
    
    # Return as a dict containing both input_ids and attention_mask
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
            attention_mask=inputs["attention_mask"], # Explicitly pass attention mask
            max_new_tokens=max_new_tokens,
            temperature=0.3,
            do_sample=True,
            use_cache=True,
            pad_token_id=tokenizer.eos_token_id
        )

    decoded = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return decoded.split("assistant")[-1].strip()

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
    if not logs:
        return "No past observations have been logged for this plot yet."

    logs_formatted = "\n".join(f"- {log}" for log in logs)
    prompt = f"""You are an agricultural assistant answering questions for plot '{plot_id}'.

Logged field observations:
{logs_formatted}

User Question: "{question}"

Instructions: Answer strictly using only the logged field observations above. If the answer is not mentioned, state that honestly. Answer in the same language as the question."""

    return _generate(prompt)

def get_seasonal_advisory(month: str, logs: list[str]) -> str:
    m_key = month.lower().strip()
    rainfall = MONTHLY_RAINFALL_MM.get(m_key)

    if rainfall is None:
        return f"No historical climate data available for '{month}'."

    logs_text = "\n".join(f"- {log}" for log in logs) if logs else "No plot history notes logged."
    prompt = f"""Historical average rainfall for {m_key.capitalize()} is {rainfall} mm.
Farmer's past field notes:
{logs_text}

Provide a concise irrigation advice for {m_key.capitalize()} based on historical rainfall and past notes."""

    return _generate(prompt)