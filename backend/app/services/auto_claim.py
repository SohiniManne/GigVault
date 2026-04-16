"""
Auto claim pipeline: location → weather → fraud (rules + ML) → decision → trust/persistence.
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


def _policy_plan_for_user(user_id: str) -> str:
    user = get_user(user_id)
    policy = user.get("policy")
    if isinstance(policy, dict) and policy.get("status") == "active":
        plan = str(policy.get("plan") or "basic").lower()
        if plan in {"basic", "pro", "elite"}:
            return plan
    return "basic"


def _weather_qualifies(plan: str, condition: str, description: str) -> bool:
    c = (condition or "").lower()
    d = (description or "").lower()
    rainy = is_rainy_condition(c)
    if plan == "elite":
        return True
    if plan == "basic":
        heavy_terms = ("heavy", "very heavy", "extreme", "torrential")
        return rainy and any(term in d for term in heavy_terms)
    moderate_terms = ("moderate", "heavy", "thunderstorm", "shower")
    if any(term in d for term in moderate_terms):
        return True
    return rainy and "light" not in d


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
    plan = _policy_plan_for_user(user_id)
    user = get_user(user_id)
    worker_online = bool(user.get("is_online") or False)
    worker_status_note = (
        "Worker marked online at disruption time."
        if worker_online
        else "Worker marked offline at disruption time."
    )
    disruption = await evaluate_disruption(
        city=city,
        lat=lat,
        lon=lon,
        forced_disruption_type=disruption_type,
    )

    w = await weather_svc.fetch_weather(lat=lat, lon=lon, city=city)

    # Persist latest coords on profile when provided
    if lat is not None and lon is not None:
        save_user(user_id, {"lat": lat, "lon": lon})
        locs = append_location(user_id, lat, lon)
    else:
        locs = list(user.get("locations") or [])
        lat = lat if lat is not None else user.get("lat")
        lon = lon if lon is not None else user.get("lon")

    gk = grid_key(
        float(lat) if lat is not None else None,
        float(lon) if lon is not None else None,
    )
    tb = time_bucket_now()

    # Parametric rain cover: mismatch only when we have a trusted observation
    if w.source != "openweather" or not w.condition or w.condition == "unknown":
        weather_mismatch = 0.0
    else:
        weather_mismatch = 0.0 if is_rainy_condition(w.condition) else 1.0

    fraud_combined, rule_score, ml_anom, ml_prob, _signals = combined_fraud_scores(
        user_id,
        weather_mismatch=weather_mismatch,
        locations=locs,
        grid_key=gk,
        time_bucket=tb,
        policy_plan=plan,
    )

    threshold = settings.fraud_block_threshold
    if plan == "basic":
        threshold *= 0.9
    elif plan == "elite":
        threshold *= 1.2
    blocked = fraud_combined >= threshold
    disruption_key = (disruption_type or "heavy_rain").strip().lower()
    is_supported_natural = disruption_key in {"heavy_rain", "flood", "extreme_heat", "severe_pollution"}
    if disruption_key == "extreme_heat":
        qualifies = (w.temperature_c or 0.0) >= 40.0
    elif disruption_key in {"heavy_rain", "flood"}:
        qualifies = _weather_qualifies(plan, w.condition, w.description)
    elif disruption_key == "severe_pollution":
        # Placeholder until AQI provider is integrated.
        qualifies = False
    else:
        qualifies = False

    decision = "no_claim"
    message = "No qualifying weather event detected for automatic payout."
    blocked_reason = None

    if blocked:
        decision = "blocked"
        message = "Claim blocked due to elevated fraud risk."
        blocked_reason = "fraud_score_threshold"
    elif not bool(disruption.get("trigger")):
        decision = "no_claim"
        message = (
            f"No payout: disruption score {disruption.get('disruption_score')} "
            f"below threshold {disruption.get('threshold')}."
        )
    elif not is_supported_natural:
        decision = "no_claim"
        message = "This disruption type requires social-signal model training and is not yet auto-verified."
    elif plan == "elite":
        decision = "approved"
        message = "Elite plan fast-track applied — claim approved."
    elif qualifies:
        decision = "approved"
        if plan == "basic":
            message = "Heavy rain verified — basic policy claim approved."
        else:
            message = "Moderate rain verified — pro policy claim approved."
    else:
        decision = "no_claim"
        if plan == "basic":
            message = "Basic plan requires heavy rain trigger; no payout."
        else:
            message = "Pro plan requires moderate rain trigger; no payout."

    claim_approved = decision == "approved"
    fraud_blocked = decision == "blocked"
    fraud_validation = validate_claim_fraud(
        user_id=user_id,
        lat=lat,
        lon=lon,
        disruption_type=disruption_type,
        disruption=disruption,
    )
    if claim_approved and fraud_validation["is_fraud"]:
        claim_approved = False
        fraud_blocked = True
        decision = "blocked"
        blocked_reason = "fraud_validation_layer"
        message = f"Claim moved to review: {fraud_validation['reason']}"

    trust = adjust_trust(
        user_id,
        fraud_blocked=fraud_blocked,
        claim_approved=claim_approved,
        fraud_score=fraud_combined,
    )

    if record_attempt:
        increment_claims(user_id, 1)
        if claim_approved:
            increment_approved_claims(user_id, 1)
        record_claim_event(
            user_id,
            float(lat) if lat is not None else None,
            float(lon) if lon is not None else None,
            pattern="weather_rain_parametric",
            approved=claim_approved,
            fraud_score=fraud_combined,
            time_bucket=tb,
            grid_key=gk,
        )

    plans = compute_plans(user_id)

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


async def preview_fraud_context(
    user_id: str,
    *,
    lat: Optional[float],
    lon: Optional[float],
    city: Optional[str],
) -> Tuple[WeatherPayload, float, float, float, float, Dict[str, Any], list]:
    w = await weather_svc.fetch_weather(lat=lat, lon=lon, city=city)
    from app.db.firestore_client import get_user

    u = get_user(user_id)
    plan = _policy_plan_for_user(user_id)
    locs = list(u.get("locations") or [])
    if lat is not None and lon is not None:
        locs = locs + [{"lat": lat, "lon": lon, "ts": 0}]
        locs = locs[-2:]

    if w.source != "openweather" or not w.condition or w.condition == "unknown":
        weather_mismatch = 0.0
    else:
        weather_mismatch = 0.0 if is_rainy_condition(w.condition) else 1.0
    gk = grid_key(lat, lon)
    tb = time_bucket_now()
    combined, rule, ml_a, ml_p, signals = combined_fraud_scores(
        user_id,
        weather_mismatch=weather_mismatch,
        locations=locs,
        grid_key=gk,
        time_bucket=tb,
        policy_plan=plan,
    )
    return w, combined, rule, ml_a, ml_p, signals, locs
