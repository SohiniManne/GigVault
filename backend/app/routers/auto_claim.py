from fastapi import APIRouter

from app.models.schemas import AutoClaimRequest, AutoClaimResponse
from app.services.auto_claim import run_auto_claim

router = APIRouter(tags=["auto-claim"])


@router.post("/auto-claim", response_model=AutoClaimResponse)
async def auto_claim(body: AutoClaimRequest) -> AutoClaimResponse:
    """Main decision engine: weather + fraud + ML → payout decision."""
    return await run_auto_claim(
        body.user_id,
        lat=body.lat,
        lon=body.lon,
        city=body.city,
        disruption_type=body.disruption_type,
        record_attempt=True,
    )
