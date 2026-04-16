"""Fixed weekly premium plans."""
from __future__ import annotations

from typing import Dict

def compute_plans(user_id: str) -> Dict[str, float]:
    _ = user_id
    return {
        "basic": 39.0,
        "pro": 49.0,
        "elite": 59.0,
    }
