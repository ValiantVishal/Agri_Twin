import os

# Force Hugging Face transformers into strict local offline mode
os.environ["TRANSFORMERS_OFFLINE"] = "1"
os.environ["HF_HUB_OFFLINE"] = "1"

# Import engine logic safely from local 'ai' directory
from ai.engine import (
    get_fertilizer_recommendation,
    query_farm_memory,
    get_seasonal_advisory
)

def test_fine_tuned_llm():
    print("\n--- TEST 4: Direct Offline Fine-Tuned LLM Inference ---")
    try:
        from unsloth import FastLanguageModel
        
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        MODEL_PATH = os.path.join(BASE_DIR, "agritwin_finetuned")
        
        if not os.path.exists(MODEL_PATH):
            print(f"[LLM Error] Path '{MODEL_PATH}' not found!")
            return

        print("[LLM Test] Loading local fine-tuned model from 'agritwin_finetuned'...")
        model, tokenizer = FastLanguageModel.from_pretrained(
            model_name=MODEL_PATH,
            max_seq_length=2048,
            load_in_4bit=True
        )
        FastLanguageModel.for_inference(model)

        messages = [
            {"role": "user", "content": "How much Urea fertilizer is recommended for Paddy cultivation?"}
        ]
        inputs = tokenizer.apply_chat_template(
            messages, 
            tokenize=True, 
            add_generation_prompt=True, 
            return_tensors="pt"
        ).to("cuda")

        print("[LLM Test] Generating offline response...")
        outputs = model.generate(input_ids=inputs, max_new_tokens=200, use_cache=True)
        response = tokenizer.batch_decode(outputs, skip_special_tokens=True)
        
        print("\n[AI Output]:")
        print(response[0])
        print("\n[LLM Test] SUCCESS: Local model generated response completely offline!")
        
    except Exception as e:
        print(f"[LLM Test Exception]: {e}")

if __name__ == "__main__":
    print("--- TEST 1: Fertilizer Deterministic Calculation ---")
    print(get_fertilizer_recommendation("paddy", 2.5))

    print("\n--- TEST 2: Multilingual Farm Memory ---")
    sample_logs = [
        "In July 2024, Paddy yielded 28 bags using 40kg Urea after heavy rainfall.",
        "The south field area retains standing water during monsoon."
    ]
    print("English query:", query_farm_memory("plot_A", "Which field section retains water?", sample_logs))
    print("Tamil query:", query_farm_memory("plot_A", "எந்த பகுதியில் தண்ணீர் தேங்கும்?", sample_logs))

    print("\n--- TEST 3: Seasonal Climate Advisory ---")
    print(get_seasonal_advisory("july", sample_logs))

    # Test the standalone fine-tuned model
    test_fine_tuned_llm()