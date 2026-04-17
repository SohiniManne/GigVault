from fastapi import APIRouter
from pydantic import BaseModel
from pathlib import Path
from typing import Optional

from app.services.disruption_engine import evaluate_disruption
from app.db.firestore_client import save_user, get_user

router = APIRouter(tags=["disruption"])


class SimulateDisruptionRequest(BaseModel):
    city: Optional[str] = None
    lat: Optional[float] = None
    lon: Optional[float] = None
    disruption_type: Optional[str] = None


# ✅ Run disruption simulation
@router.post("/simulate-disruption")
async def simulate_disruption(body: SimulateDisruptionRequest):
    result = await evaluate_disruption(
        city=body.city,
        lat=body.lat,
        lon=body.lon,
    )

    # ✅ Store latest result persistently (no globals)
    save_user("system", {"last_disruption": result})

    return result


# ✅ Get latest disruption (persistent)
@router.get("/disruption/latest")
def latest_disruption():
    system_data = get_user("system")
    return system_data.get("last_disruption") or {
        "message": "No disruption run yet"
    }


# ✅ Model verification (unchanged)
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
