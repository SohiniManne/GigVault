from fastapi import APIRouter

from app.models.schemas import PremiumQuery, PremiumResponse
from app.services.premium import compute_plans
from app.services.trust import read_trust

router = APIRouter(tags=["premium"])


@router.post("/premium", response_model=PremiumResponse)
def premium(body: PremiumQuery) -> PremiumResponse:
    trust = read_trust(body.user_id)
    plans = compute_plans(body.user_id)
    return PremiumResponse(user_id=body.user_id, trust_score=round(trust, 2), plans=plans)
