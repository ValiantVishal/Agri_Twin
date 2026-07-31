import os

# Force Hugging Face transformers into strict local offline mode
os.environ["TRANSFORMERS_OFFLINE"] = "1"
os.environ["HF_HUB_OFFLINE"] = "1"

from backend.ai.engine import (
    get_fertilizer_recommendation,
    query_farm_memory,
    get_seasonal_advisory
)

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