import os
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
from peft import PeftModel

# Relative imports to work regardless of module path execution
from .crop_data import CROP_DATA
from .climate_data import MONTHLY_RAINFALL_MM
ADAPTER_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "agritwin_finetuned"))
BASE_MODEL = "Qwen/Qwen2.5-3B-Instruct"

print(f"[AgriTwin Engine] Initializing model adapter from: {ADAPTER_DIR}")

# 1. First attempt: Try loading from local adapter/tokenizer directly
# 2. Fallback: If base model weights aren't merged in adapter dir, load base model with local_files_only
try:
    tokenizer = AutoTokenizer.from_pretrained(ADAPTER_DIR, trust_remote_code=True, local_files_only=True)
except Exception:
    tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL, trust_remote_code=True, local_files_only=True)

bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.float16
)

try:
    # Try loading directly if ADAPTER_DIR is a fully merged model
    model = AutoModelForCausalLM.from_pretrained(
        ADAPTER_DIR,
        quantization_config=bnb_config,
        device_map="auto",
        trust_remote_code=True,
        local_files_only=True
    )
except Exception:
    # Otherwise load base model offline + apply PEFT adapter
    base_model = AutoModelForCausalLM.from_pretrained(
        BASE_MODEL,
        quantization_config=bnb_config,
        device_map="auto",
        trust_remote_code=True,
        local_files_only=True
    )
    model = PeftModel.from_pretrained(base_model, ADAPTER_DIR, local_files_only=True)

model.eval()

print("[AgriTwin Engine] SUCCESS: Model loaded and ready for inference.")

def _generate(prompt: str, max_new_tokens: int = 250) -> str:
    formatted = f"<|im_start|>user\n{prompt}<|im_end|>\n<|im_start|>assistant\n"
    inputs = tokenizer(formatted, return_tensors="pt").to("cuda")

    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            temperature=0.3,
            do_sample=True,
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