"""
Firestore access with graceful fallback to in-memory store when Firebase is not configured.
Keeps the API operational for local demos without credentials.
"""
from __future__ import annotations

import json
import logging
import threading
import time
import uuid
from typing import Any, Dict, List, Optional

from app.config import get_settings

logger = logging.getLogger(__name__)

_firestore = None
_firestore_enabled = False
_memory_lock = threading.Lock()
_memory_users: Dict[str, Dict[str, Any]] = {}
_memory_claims: List[Dict[str, Any]] = []


def _init_firebase() -> None:
    global _firestore, _firestore_enabled
    if _firestore is not None:
        return
    settings = get_settings()
    try:
        import firebase_admin
        from firebase_admin import credentials, firestore
    except ImportError:
        logger.warning("firebase-admin not installed; using in-memory store")
        _firestore_enabled = False
        return

    existing_apps = getattr(firebase_admin, "_apps", None)
    if existing_apps:
        _firestore = firestore.client()
        _firestore_enabled = True
        return

    cred = None
    if settings.firebase_credentials_path:
        cred = credentials.Certificate(settings.firebase_credentials_path)
    elif settings.firebase_credentials_json:
        info = json.loads(settings.firebase_credentials_json)
        cred = credentials.Certificate(info)

    if cred is None:
        logger.info("No Firebase credentials; using in-memory store")
        _firestore_enabled = False
        return

    try:
        firebase_admin.initialize_app(cred)
        _firestore = firestore.client()
        _firestore_enabled = True
        logger.info("Firebase Firestore initialized")
    except Exception as e:
        logger.warning("Firebase init failed (%s); using in-memory store", e)
        _firestore_enabled = False


def is_firestore_enabled() -> bool:
    _init_firebase()
    return _firestore_enabled


def get_db():
    _init_firebase()
    return _firestore


def default_user_doc(user_id: str) -> Dict[str, Any]:
    return {
        "name": "Gig Worker",
        "email": "",
        "company": "",
        "is_online": False,
        "status_updated_at": None,
        "lat": None,
        "lon": None,
        "city": "",
        "trust_score": 78.0,
        "claims_count": 0,
        "claims_approved_count": 0,
        "policy": None,
        "locations": [],
        "updated_at": time.time(),
    }


def get_user(user_id: str) -> Dict[str, Any]:
    if is_firestore_enabled():
        doc = get_db().collection("users").document(user_id).get()
        if doc.exists:
            data = doc.to_dict() or {}
            data["user_id"] = user_id
            return data
        return {**default_user_doc(user_id), "user_id": user_id}

    with _memory_lock:
        if user_id not in _memory_users:
            _memory_users[user_id] = {**default_user_doc(user_id), "user_id": user_id}
        return dict(_memory_users[user_id])


def save_user(user_id: str, patch: Dict[str, Any]) -> Dict[str, Any]:
    patch = {k: v for k, v in patch.items() if v is not None}
    patch["updated_at"] = time.time()

    if is_firestore_enabled():
        ref = get_db().collection("users").document(user_id)
        ref.set(patch, merge=True)
        merged = get_user(user_id)
        return merged

    with _memory_lock:
        base = _memory_users.get(user_id, default_user_doc(user_id))
        base.update(patch)
        base["user_id"] = user_id
        _memory_users[user_id] = base
        return dict(base)


def append_location(user_id: str, lat: float, lon: float, max_keep: int = 2) -> List[Dict[str, Any]]:
    user = get_user(user_id)
    locs: List[Dict[str, Any]] = list(user.get("locations") or [])
    locs.append({"lat": lat, "lon": lon, "ts": time.time()})
    locs = locs[-max_keep:]
    save_user(user_id, {"locations": locs})
    return locs


def increment_claims(user_id: str, delta: int = 1) -> int:
    user = get_user(user_id)
    n = int(user.get("claims_count") or 0) + delta
    save_user(user_id, {"claims_count": n})
    return n


def increment_approved_claims(user_id: str, delta: int = 1) -> int:
    user = get_user(user_id)
    n = int(user.get("claims_approved_count") or 0) + delta
    save_user(user_id, {"claims_approved_count": n})
    return n


def record_claim_event(
    user_id: str,
    lat: Optional[float],
    lon: Optional[float],
    pattern: str,
    approved: bool,
    fraud_score: float,
    time_bucket: str,
    grid_key: str,
) -> None:
    row = {
        "id": str(uuid.uuid4()),
        "user_id": user_id,
        "lat": lat,
        "lon": lon,
        "ts": time.time(),
        "pattern": pattern,
        "approved": approved,
        "fraud_score": fraud_score,
        "time_bucket": time_bucket,
        "grid_key": grid_key,
    }
    if is_firestore_enabled():
        get_db().collection("claim_events").document(row["id"]).set(row)
        return
    with _memory_lock:
        _memory_claims.append(row)
        if len(_memory_claims) > 2000:
            del _memory_claims[:1000]


def fetch_recent_claim_events(limit: int = 500) -> List[Dict[str, Any]]:
    if is_firestore_enabled():
        try:
            from google.cloud.firestore import Query

            q = (
                get_db()
                .collection("claim_events")
                .order_by("ts", direction=Query.DESCENDING)
                .limit(limit)
            )
            return [d.to_dict() for d in q.stream()]
        except Exception as e:
            logger.warning("claim_events query failed: %s", e)
            return []
    with _memory_lock:
        return list(_memory_claims[-limit:])


def recent_user_claim_timestamps(user_id: str, hours: float) -> List[float]:
    cutoff = time.time() - hours * 3600
    events = fetch_recent_claim_events(800)
    return [e["ts"] for e in events if e.get("user_id") == user_id and e.get("ts", 0) >= cutoff]
