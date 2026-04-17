from typing import Dict, Any, Optional

from app.services.weather_service import get_weather_signal
from app.services.aqi_service import get_aqi_signal
from app.services.traffic_service import get_traffic_signal
from app.services.news_service import get_news_disruption_signal
from app.services.platform_service import get_platform_signal


async def evaluate_disruption(
    city: Optional[str] = None,
    lat: Optional[float] = None,
    lon: Optional[float] = None,
) -> Dict[str, Any]:

    # ✅ fallback location
    if not lat or not lon:
        lat, lon = 13.0827, 80.2707  # Chennai default

    # 🔥 FETCH SIGNALS SAFELY
    try:
        weather = await get_weather_signal(lat=lat, lon=lon, city=city)
    except Exception:
        weather = {"condition": "Unknown"}

    try:
        aqi = await get_aqi_signal(lat, lon)
    except Exception:
        aqi = {"aqi": 80}

    try:
        traffic = await get_traffic_signal(lat, lon)
    except Exception:
        traffic = {"congestion_level": "medium"}

    try:
        news = await get_news_disruption_signal(city=city)
    except Exception:
        news = {"disruption_detected": False}

    try:
        platform = get_platform_signal(city=city)
    except Exception:
        platform = {"zone_status": "active"}

    # 🧠 SCORE CALCULATION
    disruption_score = 0

    # AQI
    if aqi.get("aqi", 0) > 150:
        disruption_score += 40
    elif aqi.get("aqi", 0) > 100:
        disruption_score += 25

    # Traffic
    if traffic.get("congestion_level") == "high":
        disruption_score += 30
    elif traffic.get("congestion_level") == "medium":
        disruption_score += 15

    # Weather
    if weather.get("condition") in ["Rain", "Storm"]:
        disruption_score += 30

    # News
    if news.get("disruption_detected"):
        disruption_score += 20

    # Platform
    if platform.get("zone_status") == "closed":
        disruption_score += 40

    # Trigger
    trigger = disruption_score > 50

    return {
        "disruption_score": disruption_score,
        "disruption_type": "multi-factor",
        "trigger": trigger,
        "threshold": 50,
        "signals": {
            "weather": weather,
            "aqi": aqi,
            "traffic": traffic,
            "news": news,
            "platform": platform,
        },
    }
