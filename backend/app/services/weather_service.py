from __future__ import annotations

import logging
from typing import Any, Dict, Optional

import httpx

from app.config import get_settings

logger = logging.getLogger(__name__)


async def _openweather_payload(*, lat: Optional[float], lon: Optional[float], city: Optional[str]) -> Optional[Dict[str, Any]]:
    settings = get_settings()
    if not settings.openweather_api_key.strip():
        return None
    params: Dict[str, Any] = {"appid": settings.openweather_api_key.strip(), "units": "metric"}
    if lat is not None and lon is not None:
        params.update({"lat": lat, "lon": lon})
    elif city:
        params["q"] = city
    else:
        return None
    try:
        async with httpx.AsyncClient(timeout=12.0) as client:
            resp = await client.get("https://api.openweathermap.org/data/2.5/weather", params=params)
            resp.raise_for_status()
            data = resp.json()
        weather = (data.get("weather") or [{}])[0] or {}
        main = data.get("main") or {}
        rain = data.get("rain") or {}
        return {
            "temperature": float(main.get("temp")) if main.get("temp") is not None else None,
            "rainfall": float(rain.get("1h") or rain.get("3h") or 0.0),
            "condition": str(weather.get("main") or "unknown").lower(),
            "description": str(weather.get("description") or ""),
            "source": "openweather",
        }
    except Exception as exc:
        logger.warning("OpenWeather fetch failed: %s", exc)
        return None


async def _tomorrow_payload(*, lat: Optional[float], lon: Optional[float], city: Optional[str]) -> Optional[Dict[str, Any]]:
    settings = get_settings()
    if not settings.tomorrow_api_key.strip():
        return None
    location = None
    if lat is not None and lon is not None:
        location = f"{lat},{lon}"
    elif city:
        location = city
    if not location:
        return None
    params = {
        "location": location,
        "apikey": settings.tomorrow_api_key.strip(),
        "fields": "temperature,precipitationIntensity,weatherCode",
        "units": "metric",
    }
    try:
        async with httpx.AsyncClient(timeout=12.0) as client:
            resp = await client.get("https://api.tomorrow.io/v4/weather/realtime", params=params)
            resp.raise_for_status()
            data = resp.json()
        values = ((data.get("data") or {}).get("values") or {})
        weather_code = str(values.get("weatherCode") or "unknown")
        condition_map = {
            "4000": "drizzle",
            "4200": "light_rain",
            "4201": "heavy_rain",
            "5000": "snow",
            "8000": "thunderstorm",
        }
        return {
            "temperature": float(values.get("temperature")) if values.get("temperature") is not None else None,
            "rainfall": float(values.get("precipitationIntensity") or 0.0),
            "condition": condition_map.get(weather_code, "unknown"),
            "description": f"weatherCode={weather_code}",
            "source": "tomorrow",
        }
    except Exception as exc:
        logger.warning("Tomorrow.io fetch failed: %s", exc)
        return None


async def get_weather_signal(*, lat: Optional[float], lon: Optional[float], city: Optional[str]) -> Dict[str, Any]:
    primary = await _openweather_payload(lat=lat, lon=lon, city=city)
    if primary:
        return primary
    fallback = await _tomorrow_payload(lat=lat, lon=lon, city=city)
    if fallback:
        return fallback
    return {
        "temperature": None,
        "rainfall": 0.0,
        "condition": "unknown",
        "description": "No weather provider available",
        "source": "placeholder",
    }
