from fastapi import APIRouter
from pydantic import BaseModel
from pathlib import Path

from app.services.disruption_engine import LAST_DISRUPTION_SIGNAL, evaluate_disruption

router = APIRouter(tags=["disruption"])


class SimulateDisruptionRequest(BaseModel):
    city: str | None = None
    lat: float | None = None
    lon: float | None = None
    disruption_type: str | None = None


@router.post("/simulate-disruption")
async def simulate_disruption(body: SimulateDisruptionRequest):
    return await evaluate_disruption(
        city=body.city,
        lat=body.lat,
        lon=body.lon,
        forced_disruption_type=body.disruption_type,
    )


@router.get("/disruption/latest")
def latest_disruption():
    return LAST_DISRUPTION_SIGNAL or {"message": "No disruption run yet"}


@router.get("/verification-status")
def verification_status():
    artifact_path = (
        Path(__file__).resolve().parents[2]
        / "ml"
        / "artifacts"
        / "fraud_anomaly_isolation_forest.joblib"
    )
    model_ready = artifact_path.exists()
    return {
        "backend_online": True,
        "model_ready": model_ready,
        "mode": "active" if model_ready else "training",
        "model_artifact": str(artifact_path),
    }
