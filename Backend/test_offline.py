import sys
import os

# 1. ALWAYS import Unsloth first to apply patches
try:
    from unsloth import FastLanguageModel
except ImportError:
    pass

# 2. Force Hugging Face transformers into strict local offline mode
os.environ["TRANSFORMERS_OFFLINE"] = "1"
os.environ["HF_HUB_OFFLINE"] = "1"

# 3. Ensure Backend directory is in Python path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

# 4. Import engine logic (which now uses Unsloth internally)
from ai.engine import (
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
    # This will trigger your offline AI model!
    print("English query:", query_farm_memory("plot_A", "Which field section retains water?", sample_logs))
    print("Tamil query:", query_farm_memory("plot_A", "எந்த பகுதியில் தண்ணீர் தேங்கும்?", sample_logs))

    print("\n--- TEST 3: Seasonal Climate Advisory ---")
    # This will also trigger your offline AI model!
    print(get_seasonal_advisory("july", sample_logs))