from fastapi import APIRouter

from app.models.schemas import WeatherPayload, WeatherRequest
from app.services.weather import fetch_weather

router = APIRouter(tags=["weather"])


@router.post("/weather", response_model=WeatherPayload)
async def weather(body: WeatherRequest) -> WeatherPayload:
    """Expose weather engine (city or lat/lon)."""
    return await fetch_weather(lat=body.lat, lon=body.lon, city=body.city)
