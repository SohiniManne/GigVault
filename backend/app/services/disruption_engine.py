from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from app.config import get_settings
from app.services.aqi_service import get_aqi_signal
from app.services.news_service import get_news_disruption_signal
from app.services.platform_service import get_platform_signal
from app.services.traffic_service import get_traffic_signal
from app.services.weather_service import get_weather_signal

logger = logging.getLogger(__name__)

LAST_DISRUPTION_SIGNAL: Dict[str, Any] = {}


def _score_weather(sig: Dict[str, Any]) -> float:
    condition = str(sig.get("condition") or "").lower()
    rainfall = float(sig.get("rainfall") or 0.0)
    if "heavy" in condition or rainfall >= 10:
        return 100.0
    if "rain" in condition or rainfall >= 3:
        return 70.0
    return 20.0


def _score_traffic(sig: Dict[str, Any]) -> float:
    mult = float(sig.get("delay_multiplier") or 1.0)
    return min(100.0, max(0.0, (mult - 1.0) * 100.0))


def _score_aqi(sig: Dict[str, Any]) -> float:
    aqi = float(sig.get("aqi") or 0.0)
    return min(100.0, max(0.0, aqi / 3.0))


def _score_news(sig: Dict[str, Any]) -> float:
    if sig.get("disruption_detected"):
        return 100.0
    return 0.0


def _score_platform(sig: Dict[str, Any]) -> float:
    zone = str(sig.get("zone_status") or "active")
    return {"closed": 100.0, "low_demand": 65.0, "active": 10.0}.get(zone, 10.0)


async def evaluate_disruption(
    *,
    city: Optional[str],
    lat: Optional[float],
    lon: Optional[float],
    forced_disruption_type: Optional[str] = None,
) -> Dict[str, Any]:
    weather = await get_weather_signal(lat=lat, lon=lon, city=city)
    aqi = get_aqi_signal(city=city)
    traffic = await get_traffic_signal(origin_lat=lat, origin_lon=lon, city=city)
    news = await get_news_disruption_signal(city=city)
    platform = get_platform_signal(city=city, disruption_hint=bool(news.get("disruption_detected")))

    score = (
        0.30 * _score_weather(weather)
        + 0.25 * _score_traffic(traffic)
        + 0.15 * _score_aqi(aqi)
        + 0.15 * _score_news(news)
        + 0.15 * _score_platform(platform)
    )
    threshold = get_settings().disruption_threshold
    trigger = score >= threshold

    if forced_disruption_type:
        disruption_type = forced_disruption_type
    elif news.get("disruption_detected"):
        disruption_type = "social_disruption"
    elif float(weather.get("rainfall") or 0.0) >= 10.0:
        disruption_type = "heavy_rain"
    elif float(aqi.get("aqi") or 0.0) >= 180.0:
        disruption_type = "severe_pollution"
    else:
        disruption_type = "normal_conditions"

    result = {
        "disruption_score": round(score, 2),
        "disruption_type": disruption_type,
        "trigger": trigger,
        "threshold": threshold,
        "signals": {
            "weather": weather,
            "traffic": traffic,
            "aqi": aqi,
            "news": news,
            "platform": platform,
        },
    }
    LAST_DISRUPTION_SIGNAL.clear()
    LAST_DISRUPTION_SIGNAL.update(result)
    logger.info("disruption score=%s trigger=%s type=%s", result["disruption_score"], trigger, disruption_type)
    return result
