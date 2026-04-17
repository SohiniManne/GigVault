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

    if not lat or not lon:
        lat, lon = 13.0827, 80.2707  # default Chennai

    # 🔥 Gather signals
    weather = await get_weather_signal(lat=lat, lon=lon, city=city)
    aqi = await get_aqi_signal(lat, lon)
    traffic = await get_traffic_signal(lat, lon)
    news = await get_news_disruption_signal(city)
    platform = get_platform_signal(city=city)

    # 🧠 Score calculation
    disruption_score = 0

    if aqi["aqi"] > 150:
        disruption_score += 40
    elif aqi["aqi"] > 100:
        disruption_score += 25

    if traffic["congestion_level"] == "high":
        disruption_score += 30
    elif traffic["congestion_level"] == "medium":
        disruption_score += 15

    if weather.get("condition") in ["Rain", "Storm"]:
        disruption_score += 30

    if news.get("disruption_detected"):
        disruption_score += 20

    if platform.get("zone_status") == "closed":
        disruption_score += 40

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
