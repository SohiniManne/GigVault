"""Trust score adjustments after claim decisions."""
from __future__ import annotations

from app.config import get_settings
from app.db.firestore_client import get_user, save_user


def adjust_trust(
    user_id: str,
    *,
    fraud_blocked: bool,
    claim_approved: bool,
    fraud_score: float,
) -> float:
    settings = get_settings()
    user = get_user(user_id)
    t = float(user.get("trust_score", 78.0))

    if fraud_blocked or fraud_score >= settings.fraud_block_threshold:
        t -= settings.trust_delta_fraud
    elif claim_approved:
        t += settings.trust_delta_valid_claim

    t = max(settings.trust_min, min(settings.trust_max, t))
    save_user(user_id, {"trust_score": t})
    return t


def read_trust(user_id: str) -> float:
    return float(get_user(user_id).get("trust_score", 78.0))
