from __future__ import annotations

from typing import Any, Dict, Optional


def get_aqi_signal(*, city: Optional[str]) -> Dict[str, Any]:
    # Mocked CPCB-like response for now. Replace with CPCB connector when available.
    city_key = (city or "").strip().lower()
    mock_aqi = 85 if city_key else 65
    if mock_aqi <= 50:
        category = "Good"
    elif mock_aqi <= 100:
        category = "Moderate"
    else:
        category = "Severe"
    return {"aqi": mock_aqi, "category": category, "source": "cpcb_mock"}
