from fastapi import APIRouter

from app.models.schemas import FraudRingsResponse
from app.services.rings import detect_rings, fraud_alerts

router = APIRouter(tags=["fraud-rings"])


@router.get("/fraud-rings", response_model=FraudRingsResponse)
def fraud_rings() -> FraudRingsResponse:
    """Flagged clusters: same location bucket, time bucket, and claim pattern."""
    rings = detect_rings(min_users=3)
    alerts = fraud_alerts()
    return FraudRingsResponse(rings=rings, alerts=alerts)
