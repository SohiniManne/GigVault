from fastapi import APIRouter, HTTPException

from app.models.schemas import PolicyPayload, SelectPolicyRequest

router = APIRouter(tags=["policy"])


@router.post("/select-policy", response_model=PolicyPayload)
def select_policy(body: SelectPolicyRequest) -> PolicyPayload:
    raise HTTPException(status_code=410, detail="Direct policy activation is disabled. Complete payment first.")
