import httpx
import random
from app.config import get_settings

settings = get_settings()

async def get_aqi_signal(lat: float, lon: float):
    try:
        url = f"https://api.openweathermap.org/data/2.5/air_pollution?lat={lat}&lon={lon}&appid={settings.openweather_api_key}"

        async with httpx.AsyncClient() as client:
            res = await client.get(url)
            data = res.json()

        aqi_level = data["list"][0]["main"]["aqi"]

        # Convert 1–5 scale → realistic AQI
        aqi_map = {
            1: random.randint(10, 50),
            2: random.randint(50, 100),
            3: random.randint(100, 150),
            4: random.randint(150, 200),
            5: random.randint(200, 300),
        }

        aqi = aqi_map.get(aqi_level, 85)

        return {
            "aqi": aqi,
            "category": "High" if aqi > 150 else "Moderate",
            "source": "openweather"
        }

    except Exception as e:
        print("AQI API failed:", e)
        return {
            "aqi": random.randint(60, 150),
            "category": "Moderate",
            "source": "fallback"
        }
