import httpx
import random
from app.config import get_settings

settings = get_settings()

async def get_traffic_signal(lat: float, lon: float):
    try:
        url = f"https://api.tomtom.com/traffic/services/4/flowSegmentData/absolute/10/json?key={settings.tomtom_api_key}&point={lat},{lon}"

        async with httpx.AsyncClient() as client:
            res = await client.get(url)
            data = res.json()

        flow = data["flowSegmentData"]
        current = flow["currentSpeed"]
        free = flow["freeFlowSpeed"]

        ratio = current / free if free else 1

        if ratio > 0.8:
            level = "low"
        elif ratio > 0.5:
            level = "medium"
        else:
            level = "high"

        return {
            "congestion_level": level,
            "delay_multiplier": round(1 + (1 - ratio), 2),
            "source": "tomtom"
        }

    except Exception as e:
        print("Traffic API failed:", e)
        return {
            "congestion_level": "medium",
            "delay_multiplier": round(random.uniform(1.2, 1.8), 2),
            "source": "fallback"
        }
