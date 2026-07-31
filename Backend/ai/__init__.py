"""
AgriTwin AI Core Module
Exposes local inference engine functions, deterministic lookup algorithms,
and historical regional climate data.
"""

from Backend.ai.crop_data import CROP_DATA
from Backend.ai.climate_data import MONTHLY_RAINFALL_MM
from Backend.ai.engine import (
    get_fertilizer_recommendation,
    query_farm_memory,
    get_seasonal_advisory,
)

__all__ = [
    "CROP_DATA",
    "MONTHLY_RAINFALL_MM",
    "get_fertilizer_recommendation",
    "query_farm_memory",
    "get_seasonal_advisory",
]