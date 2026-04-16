"""
Multi-signal fraud engine: rule-based score + hooks for ML combination.
"""
from __future__ import annotations

import time
from typing import Any, Dict, List, Tuple

from app.config import get_settings
from app.db.firestore_client import fetch_recent_claim_events, get_user, recent_user_claim_timestamps
from app.services import ml_anomaly
from app.services.gps import compute_gps_jump_signal


def _repeated_claims_signal(user_id: str, hours: int, max_ok: int) -> float:
    ts_list = recent_user_claim_timestamps(user_id, hours)
    # Count attempts in window; penalize if more than max_ok
    excess = max(0, len(ts_list) - max_ok)
    return float(excess)


def _cluster_behavior_signal(user_id: str, grid_key: str, time_bucket: str) -> float:
    """
    Boost risk if many distinct users filed from same grid + hour bucket recently.
    """
    events = fetch_recent_claim_events(600)
    users = {
        e.get("user_id")
        for e in events
        if e.get("grid_key") == grid_key
        and e.get("time_bucket") == time_bucket
        and e.get("user_id")
    }
    if user_id in users:
        users.discard(user_id)
    peer_count = len(users)
    if peer_count >= 4:
        return 2.0
    if peer_count >= 2:
        return 1.0
    return 0.0


def compute_rule_fraud_score(
    user_id: str,
    *,
    claims_count: int,
    gps_jump: float,
    weather_mismatch: float,
    locations: List[Dict[str, Any]],
    grid_key: str,
    time_bucket: str,
    strictness_multiplier: float = 1.0,
) -> Tuple[float, Dict[str, Any]]:
    settings = get_settings()
    repeated = _repeated_claims_signal(
        user_id, settings.repeated_claim_hours, settings.max_recent_claims_for_repeat
    )
    cluster = _cluster_behavior_signal(user_id, grid_key, time_bucket)

    # User-requested formula + cluster term
    base = (
        float(claims_count) * 5.0
        + float(gps_jump) * 30.0
        + float(weather_mismatch) * 40.0
        + float(repeated) * 10.0
        + cluster * 15.0
    )
    base *= strictness_multiplier

    signals = {
        "claims_count": claims_count,
        "gps_jump": gps_jump,
        "weather_mismatch": weather_mismatch,
        "repeated_claims_excess": repeated,
        "cluster_behavior": cluster,
    }
    return float(min(base, 150.0)), signals


def build_features_for_ml(
    user_id: str,
    weather_mismatch: float,
    locations: List[Dict[str, Any]],
) -> Tuple[float, float, float]:
    user = get_user(user_id)
    claims_count = int(user.get("claims_count") or 0)
    settings = get_settings()
    gps_jump, _speed = compute_gps_jump_signal(locations, settings.gps_speed_threshold_ms)
    return float(claims_count), float(gps_jump), float(weather_mismatch)


def combined_fraud_scores(
    user_id: str,
    *,
    weather_mismatch: float,
    locations: List[Dict[str, Any]],
    grid_key: str,
    time_bucket: str,
    policy_plan: str = "pro",
) -> Tuple[float, float, float, float, Dict[str, Any]]:
    user = get_user(user_id)
    claims_count = int(user.get("claims_count") or 0)
    settings = get_settings()
    gps_jump, _ = compute_gps_jump_signal(locations, settings.gps_speed_threshold_ms)

    strictness_map = {"basic": 1.2, "pro": 1.0, "elite": 0.75}
    strictness = strictness_map.get(policy_plan, 1.0)
    rule_score, signals = compute_rule_fraud_score(
        user_id,
        claims_count=claims_count,
        gps_jump=gps_jump,
        weather_mismatch=weather_mismatch,
        locations=locations,
        grid_key=grid_key,
        time_bucket=time_bucket,
        strictness_multiplier=strictness,
    )

    ml_anomaly_score, ml_fraud_p = ml_anomaly.score_features(
        claims_count, gps_jump, weather_mismatch
    )

    # Normalize rule to 0-100-ish then blend with ML probability
    rule_norm = min(100.0, rule_score * 0.65)
    combined = min(100.0, 0.55 * rule_norm + 0.45 * (ml_fraud_p * 100.0))
    if policy_plan == "basic":
        combined = min(100.0, combined * 1.1)
    elif policy_plan == "elite":
        combined = max(0.0, combined * 0.85)

    signals["ml_anomaly_score"] = ml_anomaly_score
    signals["ml_fraud_probability"] = ml_fraud_p
    signals["implied_speed_note"] = _speed_note(locations, settings.gps_speed_threshold_ms)
    signals["policy_plan"] = policy_plan

    return combined, rule_score, ml_anomaly_score, ml_fraud_p, signals


def _speed_note(locations, threshold: float) -> str:
    if len(locations) < 2:
        return "insufficient_fixes"
    _, speed = compute_gps_jump_signal(locations, threshold)
    if speed is None:
        return "n/a"
    return f"{speed:.1f} m/s vs threshold {threshold}"


def time_bucket_now() -> str:
    return time.strftime("%Y-%m-%d-%H", time.gmtime())
