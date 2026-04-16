from fastapi import APIRouter, HTTPException
import time

from app.db.firestore_client import get_user, save_user
from app.models.schemas import UserProfileIn, UserProfileOut

router = APIRouter(tags=["users"])


@router.get("/user-profile/{user_id}", response_model=UserProfileOut)
def read_profile(user_id: str) -> UserProfileOut:
    u = get_user(user_id)
    return UserProfileOut(
        user_id=user_id,
        name=str(u.get("name") or ""),
        email=str(u.get("email") or ""),
        company=str(u.get("company") or ""),
        is_online=bool(u.get("is_online") or False),
        location={
            "lat": u.get("lat"),
            "lon": u.get("lon"),
            "city": u.get("city") or "",
        },
        trust_score=float(u.get("trust_score", 78.0)),
        claims_count=int(u.get("claims_count") or 0),
        claims_approved_count=int(u.get("claims_approved_count") or 0),
        policy=u.get("policy"),
    )


@router.put("/user-profile", response_model=UserProfileOut)
def upsert_profile(body: UserProfileIn) -> UserProfileOut:
    patch: dict = {}
    if body.name is not None:
        patch["name"] = body.name
    if body.email is not None:
        patch["email"] = body.email
    if body.company is not None:
        patch["company"] = body.company
    if body.is_online is not None:
        patch["is_online"] = bool(body.is_online)
        patch["status_updated_at"] = time.time()
    if body.location:
        if body.location.lat is not None:
            patch["lat"] = body.location.lat
        if body.location.lon is not None:
            patch["lon"] = body.location.lon
        if body.location.city is not None:
            patch["city"] = body.location.city
    if not patch:
        raise HTTPException(status_code=400, detail="No fields to update")
    save_user(body.user_id, patch)
    return read_profile(body.user_id)
