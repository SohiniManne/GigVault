"""
Auto claim pipeline: location → weather → fraud → decision → persistence.
"""

from __future__ import annotations
from typing import Any, Dict, Optional, Tuple

from app.config import get_settings
from app.db.firestore_client import (
    append_location,
    get_user,
    increment_approved_claims,
    increment_claims,
    record_claim_event,
    save_user,
)
from app.models.schemas import AutoClaimResponse, WeatherPayload
from app.services import weather as weather_svc
from app.services.disruption_engine import evaluate_disruption
from app.services.fraud import combined_fraud_scores, time_bucket_now
from app.services.fraud_service import validate_claim_fraud
from app.services.gps import grid_key
from app.services.premium import compute_plans
from app.services.trust import adjust_trust
from app.services.weather import is_rainy_condition


# ✅ SAFE USER POLICY FETCH
def _policy_plan_for_user(user_id: str) -> str:
    user = get_user(user_id) or {}

    policy = user.get("policy")
    if isinstance(policy, dict) and policy.get("status") == "active":
        plan = str(policy.get("plan") or "basic").lower()
        if plan in {"basic", "pro", "elite"}:
            return plan

    return "basic"


# ✅ WEATHER QUALIFICATION
def _weather_qualifies(plan: str, condition: str, description: str) -> bool:
    c = (condition or "").lower()
    d = (description or "").lower()

    rainy = is_rainy_condition(c)

    if plan == "elite":
        return True

    if plan == "basic":
        return rainy and any(term in d for term in ["heavy", "very heavy", "extreme"])

    return rainy


# ================= MAIN =================

async def run_auto_claim(
    user_id: str,
    *,
    lat: Optional[float],
    lon: Optional[float],
    city: Optional[str],
    disruption_type: Optional[str] = None,
    record_attempt: bool = True,
) -> AutoClaimResponse:

    settings = get_settings()

    # ✅ SAFE USER
    user = get_user(user_id) or {}

    plan = _policy_plan_for_user(user_id)

    worker_online = bool(user.get("is_online", False))

    worker_status_note = (
        "Worker marked online at disruption time."
        if worker_online
        else "Worker marked offline at disruption time."
    )

    # ✅ SAFE LAT/LON DEFAULT
    if lat is None or lon is None:
        lat = user.get("lat", 13.0827)
        lon = user.get("lon", 80.2707)

    # ✅ FIXED DISRUPTION CALL
    disruption = await evaluate_disruption(
        city=city,
        lat=lat,
        lon=lon,
    )

    # ✅ WEATHER
    w = await weather_svc.fetch_weather(lat=lat, lon=lon, city=city)

    # ✅ SAVE LOCATION
    save_user(user_id, {"lat": lat, "lon": lon})
    locs = append_location(user_id, lat, lon)

    # ================= FRAUD =================

    gk = grid_key(lat, lon)
    tb = time_bucket_now()

    if w.source != "openweather" or not w.condition:
        weather_mismatch = 0.0
    else:
        weather_mismatch = 0.0 if is_rainy_condition(w.condition) else 1.0

    fraud_combined, rule_score, ml_anom, ml_prob, _ = combined_fraud_scores(
        user_id,
        weather_mismatch=weather_mismatch,
        locations=locs,
        grid_key=gk,
        time_bucket=tb,
        policy_plan=plan,
    )

    threshold = settings.fraud_block_threshold
    blocked = fraud_combined >= threshold

    # ================= DECISION =================

    qualifies = _weather_qualifies(plan, w.condition, w.description)

    decision = "no_claim"
    message = "No valid trigger"
    blocked_reason = None

    if blocked:
        decision = "blocked"
        message = "Fraud risk too high"
        blocked_reason = "fraud_score"

    elif not disruption.get("trigger"):
        decision = "no_claim"
        message = "No disruption trigger"

    elif qualifies:
        decision = "approved"
        message = "Claim approved"

    # ================= FRAUD VALIDATION =================

    fraud_validation = validate_claim_fraud(
        user_id=user_id,
        lat=lat,
        lon=lon,
        disruption_type=disruption_type,
        disruption=disruption,
    )

    if decision == "approved" and fraud_validation["is_fraud"]:
        decision = "blocked"
        message = f"Fraud detected: {fraud_validation['reason']}"
        blocked_reason = "fraud_validation"

    # ================= TRUST =================

    trust = adjust_trust(
        user_id,
        fraud_blocked=(decision == "blocked"),
        claim_approved=(decision == "approved"),
        fraud_score=fraud_combined,
    )

    # ================= SAVE =================

    if record_attempt:
        increment_claims(user_id, 1)

        if decision == "approved":
            increment_approved_claims(user_id, 1)

        record_claim_event(
            user_id,
            lat,
            lon,
            approved=(decision == "approved"),
            fraud_score=fraud_combined,
        )

    plans = compute_plans(user_id)

    # ================= RESPONSE =================

    return AutoClaimResponse(
        message=message,
        weather=w,
        fraud_score=round(fraud_combined, 2),
        trust_score=round(trust, 2),
        premium=plans,
        decision=decision,
        fraud_score_rule=round(rule_score, 2),
        ml_anomaly_score=round(ml_anom, 4),
        fraud_probability=round(ml_prob, 4),
        blocked_reason=blocked_reason,
        worker_online_at_disruption=worker_online,
        worker_status_note=worker_status_note,
    )
# ================= PREVIEW FRAUD =================

async def preview_fraud_context(user_id: str, lat: float, lon: float):
    """
    Lightweight preview for fraud scoring (used by fraud_score router)
    """

    user = get_user(user_id) or {}

    locs = list(user.get("locations", []))

    gk = grid_key(lat, lon)
    tb = time_bucket_now()

    fraud_combined, rule_score, ml_anom, ml_prob, _ = combined_fraud_scores(
        user_id,
        weather_mismatch=0.0,
        locations=locs,
        grid_key=gk,
        time_bucket=tb,
        policy_plan=_policy_plan_for_user(user_id),
    )

    return {
        "fraud_score": fraud_combined,
        "rule_score": rule_score,
        "ml_anomaly": ml_anom,
        "probability": ml_prob,
    }
