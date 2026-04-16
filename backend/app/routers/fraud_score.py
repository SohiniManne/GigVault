from fastapi import APIRouter

from app.models.schemas import FraudScoreRequest, FraudScoreResponse
from app.services.auto_claim import preview_fraud_context

router = APIRouter(tags=["fraud"])


@router.post("/fraud-score", response_model=FraudScoreResponse)
async def fraud_score(body: FraudScoreRequest) -> FraudScoreResponse:
    """Compute multi-signal fraud score without necessarily recording a claim."""
    w, combined, rule, ml_a, ml_p, signals, _locs = await preview_fraud_context(
        body.user_id,
        lat=body.lat,
        lon=body.lon,
        city=body.city,
    )
    return FraudScoreResponse(
        fraud_score=round(combined, 2),
        fraud_score_rule=round(rule, 2),
        ml_anomaly_score=round(ml_a, 4),
        fraud_probability=round(ml_p, 4),
        signals=signals,
        weather=w,
    )
