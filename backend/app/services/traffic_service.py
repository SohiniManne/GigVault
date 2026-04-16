from __future__ import annotations

from typing import Any, Dict, Optional

import httpx

from app.config import get_settings


async def get_traffic_signal(
    *,
    origin_lat: Optional[float],
    origin_lon: Optional[float],
    city: Optional[str],
) -> Dict[str, Any]:
    settings = get_settings()
    # Fallback mock if key/coords are unavailable
    if not settings.google_maps_api_key.strip() or origin_lat is None or origin_lon is None:
        return {"congestion_level": "medium", "delay_multiplier": 1.35, "source": "google_mock"}

    destination = city or f"{origin_lat},{origin_lon}"
    params = {
        "origins": f"{origin_lat},{origin_lon}",
        "destinations": destination,
        "departure_time": "now",
        "key": settings.google_maps_api_key.strip(),
    }
    try:
        async with httpx.AsyncClient(timeout=12.0) as client:
            resp = await client.get(
                "https://maps.googleapis.com/maps/api/distancematrix/json",
                params=params,
            )
            resp.raise_for_status()
            data = resp.json()
        rows = data.get("rows") or []
        elements = (rows[0] or {}).get("elements") if rows else []
        e0 = (elements[0] or {}) if elements else {}
        duration = ((e0.get("duration") or {}).get("value")) or 0
        in_traffic = ((e0.get("duration_in_traffic") or {}).get("value")) or duration
        delay_multiplier = (float(in_traffic) / float(duration)) if duration else 1.0
    except Exception:
        delay_multiplier = 1.35

    if delay_multiplier >= 1.8:
        level = "high"
    elif delay_multiplier >= 1.25:
        level = "medium"
    else:
        level = "low"
    return {"congestion_level": level, "delay_multiplier": round(delay_multiplier, 2), "source": "google_maps"}
