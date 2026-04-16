from __future__ import annotations

from typing import Any, Dict, Optional

from app.db.firestore_client import fetch_recent_claim_events, get_user
from app.services.gps import grid_key


def validate_claim_fraud(
    *,
    user_id: str,
    lat: Optional[float],
    lon: Optional[float],
    disruption_type: Optional[str],
    disruption: Dict[str, Any],
) -> Dict[str, Any]:
    user = get_user(user_id)
    reasons = []
    score = 0

    # 1) Location check
    stored_lat = user.get("lat")
    stored_lon = user.get("lon")
    if lat is not None and lon is not None and stored_lat is not None and stored_lon is not None:
        if abs(float(lat) - float(stored_lat)) > 0.3 or abs(float(lon) - float(stored_lon)) > 0.3:
            score += 40
            reasons.append("GPS mismatch with profile location")

    # 2) Claim/disruption consistency check
    d_type = (disruption_type or "").strip().lower()
    engine_type = str(disruption.get("disruption_type") or "").lower()
    if d_type and engine_type and d_type not in engine_type and engine_type not in d_type:
        score += 35
        reasons.append("Claim reason inconsistent with disruption signals")

    # 3) Cluster detection by location/time bucket
    gk = grid_key(lat, lon)
    recent = fetch_recent_claim_events(300)
    same_grid_recent = [e for e in recent if e.get("grid_key") == gk]
    if len(same_grid_recent) >= 8:
        score += 35
        reasons.append("High claim cluster detected in same location")
    elif len(same_grid_recent) >= 4:
        score += 20
        reasons.append("Medium claim cluster detected in same location")

    if score >= 70:
        risk = "high"
    elif score >= 35:
        risk = "medium"
    else:
        risk = "low"
    return {
        "is_fraud": risk == "high",
        "risk_level": risk,
        "reason": "; ".join(reasons) if reasons else "No fraud indicators",
        "score": score,
    }
