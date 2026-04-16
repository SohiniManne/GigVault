"""
Fraud ring detection: users sharing grid + time bucket + claim pattern.
"""
from __future__ import annotations

from collections import defaultdict
from typing import Any, Dict, List

from app.db.firestore_client import fetch_recent_claim_events, get_user
from app.models.schemas import FraudRingCluster


def detect_rings(min_users: int = 3) -> List[FraudRingCluster]:
    events = fetch_recent_claim_events(800)
    groups: Dict[tuple, List[str]] = defaultdict(list)
    counts: Dict[tuple, int] = defaultdict(int)

    for e in events:
        gk = e.get("grid_key") or "unknown"
        tb = e.get("time_bucket") or ""
        pat = e.get("pattern") or "default"
        uid = e.get("user_id")
        if not uid:
            continue
        key = (gk, tb, pat)
        if uid not in groups[key]:
            groups[key].append(uid)
        counts[key] += 1

    rings: List[FraudRingCluster] = []
    for key, uids in groups.items():
        gk, tb, _pat = key
        if len(uids) >= min_users:
            risk = "high" if len(uids) >= 6 else "medium"
            rings.append(
                FraudRingCluster(
                    grid_key=gk,
                    time_bucket=tb,
                    user_ids=uids,
                    claim_count=counts[key],
                    risk_level=risk,
                )
            )
    return rings


def fraud_alerts() -> List[Dict[str, Any]]:
    rings = detect_rings(min_users=2)
    alerts: List[Dict[str, Any]] = []
    for r in rings:
        alerts.append(
            {
                "type": "ring",
                "severity": r.risk_level,
                "message": f"Coordinated activity ({len(r.user_ids)} users) at {r.grid_key} bucket {r.time_bucket}",
                "user_ids": r.user_ids,
            }
        )

    # Individual risk alerts: still useful when no coordinated ring exists.
    recent = fetch_recent_claim_events(300)
    latest_by_user: Dict[str, Dict[str, Any]] = {}
    for e in recent:
        uid = e.get("user_id")
        if not uid:
            continue
        prev = latest_by_user.get(uid)
        if prev is None or float(e.get("ts", 0)) > float(prev.get("ts", 0)):
            latest_by_user[uid] = e

    for uid, ev in latest_by_user.items():
        fraud_score = float(ev.get("fraud_score") or 0.0)
        trust = float(get_user(uid).get("trust_score") or 0.0)
        if fraud_score < 70.0 and trust > 25.0:
            continue
        severity = "high" if fraud_score >= 85.0 or trust <= 12.0 else "medium"
        alerts.append(
            {
                "type": "user_risk",
                "severity": severity,
                "message": (
                    f"High individual risk for {uid}: fraud score {fraud_score:.1f}, "
                    f"trust {trust:.1f}"
                ),
                "user_ids": [uid],
            }
        )
    return alerts
