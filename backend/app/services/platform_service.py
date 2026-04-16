from __future__ import annotations

from typing import Any, Dict, Optional


def get_platform_signal(*, city: Optional[str], disruption_hint: bool = False) -> Dict[str, Any]:
    if disruption_hint:
        return {"zone_status": "low_demand", "reason": "Disruption indicators elevated", "source": "platform_mock"}
    if not city:
        return {"zone_status": "active", "reason": "No city context", "source": "platform_mock"}
    city_key = city.strip().lower()
    if city_key in {"delhi", "mumbai", "bengaluru"}:
        return {"zone_status": "active", "reason": "Normal operations", "source": "platform_mock"}
    return {"zone_status": "low_demand", "reason": "Demand dip in zone", "source": "platform_mock"}
