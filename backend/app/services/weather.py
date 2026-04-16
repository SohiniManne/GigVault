"""
Real-time weather via OpenWeather Current Weather API.
Fails soft: returns a safe placeholder so the pipeline never crashes.
"""
from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from app.models.schemas import WeatherPayload
from app.services.weather_service import get_weather_signal

logger = logging.getLogger(__name__)


async def fetch_weather(
    *,
    lat: Optional[float] = None,
    lon: Optional[float] = None,
    city: Optional[str] = None,
) -> WeatherPayload:
    sig = await get_weather_signal(lat=lat, lon=lon, city=city)
    return WeatherPayload(
        condition=str(sig.get("condition") or "unknown"),
        temperature_c=sig.get("temperature"),
        rainfall_mm=sig.get("rainfall"),
        description=str(sig.get("description") or ""),
        source=str(sig.get("source") or "placeholder"),
    )


def is_rainy_condition(condition: str) -> bool:
    c = (condition or "").lower()
    return any(
        x in c
        for x in (
            "rain",
            "drizzle",
            "thunderstorm",
            "squall",
        )
    )
