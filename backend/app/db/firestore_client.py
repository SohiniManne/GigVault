import os
import json
from google.cloud import firestore
from google.oauth2 import service_account
from datetime import datetime

# 🔥 Create Firestore client once
def get_db():
    creds_json = json.loads(os.environ["GOOGLE_APPLICATION_CREDENTIALS_JSON"])

    credentials = service_account.Credentials.from_service_account_info(creds_json)

    return firestore.Client(
        credentials=credentials,
        project=creds_json["project_id"]
    )


db = get_db()


# ================= USER =================

def get_user(user_id: str):
    doc = db.collection("users").document(user_id).get()
    return doc.to_dict() or {}


def save_user(user_id: str, data: dict):
    db.collection("users").document(user_id).set(data, merge=True)


# ================= LOCATION =================

def append_location(user_id: str, lat: float, lon: float):
    ref = db.collection("users").document(user_id)
    user = ref.get().to_dict() or {}

    locations = user.get("locations", [])
    locations.append({"lat": lat, "lon": lon})

    ref.set({"locations": locations}, merge=True)
    return locations


# ================= CLAIMS =================

def increment_claims(user_id: str, count: int):
    ref = db.collection("users").document(user_id)
    user = ref.get().to_dict() or {}

    total = user.get("claims_count", 0) + count
    ref.set({"claims_count": total}, merge=True)


def increment_approved_claims(user_id: str, count: int):
    ref = db.collection("users").document(user_id)
    user = ref.get().to_dict() or {}

    total = user.get("claims_approved_count", 0) + count
    ref.set({"claims_approved_count": total}, merge=True)


def record_claim_event(user_id: str, lat, lon, **kwargs):
    db.collection("claims").add({
        "user_id": user_id,
        "lat": lat,
        "lon": lon,
        "timestamp": datetime.utcnow().isoformat(),
        **kwargs
    })
# ================= FRAUD SUPPORT =================

def fetch_recent_claim_events(limit: int = 20):
    try:
        docs = (
            db.collection("claims")
            .order_by("timestamp", direction=firestore.Query.DESCENDING)
            .limit(limit)
            .stream()
        )
        return [doc.to_dict() for doc in docs]
    except Exception as e:
        print("⚠️ fetch_recent_claim_events error:", e)
        return []


def recent_user_claim_timestamps(user_id: str, limit: int = 10):
    try:
        docs = (
            db.collection("claims")
            .where("user_id", "==", user_id)
            .order_by("timestamp", direction=firestore.Query.DESCENDING)
            .limit(limit)
            .stream()
        )
        return [doc.to_dict().get("timestamp") for doc in docs]
    except Exception as e:
        print("⚠️ recent_user_claim_timestamps error:", e)
        return []
