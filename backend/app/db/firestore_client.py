import os
import json
from google.cloud import firestore
from google.oauth2 import service_account

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
        **kwargs
    })
