"""
GigVault API — parametric gig insurance with hybrid fraud detection.
"""
import logging
import os
import asyncio

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.routers import auto_claim, disruption, fraud_rings, fraud_score, payments, policy, premium, user_profile, weather
from app.services.disruption_engine import evaluate_disruption

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("gigvault")

app = FastAPI(title="GigVault API", version="1.0.0")

settings = get_settings()
print("🔥 ACTIVE CORS:", settings.cors_origin_list)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 🔥 FORCE ALLOW EVERYTHING
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(auto_claim.router)
app.include_router(weather.router)
app.include_router(fraud_score.router)
app.include_router(user_profile.router)
app.include_router(premium.router)
app.include_router(fraud_rings.router)
app.include_router(payments.router)
app.include_router(policy.router)
app.include_router(disruption.router)

_bg_tasks: list[asyncio.Task] = []


async def _loop_runner(name: str, interval_seconds: int, coro_factory):
    while True:
        try:
            await coro_factory()
            logger.info("background job completed: %s", name)
        except Exception as exc:
            logger.warning("background job failed: %s (%s)", name, exc)
        await asyncio.sleep(interval_seconds)


@app.on_event("startup")
async def startup_jobs():
    async def weather_job():
        await evaluate_disruption(city="Delhi", lat=None, lon=None)

    async def aqi_job():
        await evaluate_disruption(city="Mumbai", lat=None, lon=None)

    async def traffic_job():
        await evaluate_disruption(city="Bengaluru", lat=12.9716, lon=77.5946)

    async def engine_job():
        await evaluate_disruption(city="Hyderabad", lat=17.3850, lon=78.4867)

    _bg_tasks.extend(
        [
            asyncio.create_task(_loop_runner("weather_10m", 600, weather_job)),
            asyncio.create_task(_loop_runner("aqi_15m", 900, aqi_job)),
            asyncio.create_task(_loop_runner("traffic_10m", 600, traffic_job)),
            asyncio.create_task(_loop_runner("disruption_engine_5m", 300, engine_job)),
        ]
    )


@app.on_event("shutdown")
async def shutdown_jobs():
    for task in _bg_tasks:
        task.cancel()


@app.get("/health")
def health():
    return {"status": "ok", "service": "gigvault-api"}


# Render uses PORT; local dev uses uvicorn default
def run():
    port = int(os.environ.get("PORT", settings.port))
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=False)


if __name__ == "__main__":
    run()
