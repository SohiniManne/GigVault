import os
import json
from google.cloud import firestore
from google.oauth2 import service_account

def get_firestore_client():
    # 🔥 Load JSON from environment variable
    creds_json = json.loads(os.environ["GOOGLE_APPLICATION_CREDENTIALS_JSON"])

    # 🔥 Create credentials
    credentials = service_account.Credentials.from_service_account_info(creds_json)

    # 🔥 Create Firestore client
    db = firestore.Client(
        credentials=credentials,
        project=creds_json["project_id"]
    )

    return db
