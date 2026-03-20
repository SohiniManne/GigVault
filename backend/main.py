from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import random

app = FastAPI()

# -----------------------------
# Models
# -----------------------------
class TriggerRequest(BaseModel):
    event: str

class FraudRequest(BaseModel):
    gps: str
    ip: str

class PremiumRequest(BaseModel):
    city: str
    risk: str

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # for demo (later restrict)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------
# 1. Trigger Simulation
# -----------------------------
@app.post("/simulate-trigger")
def simulate_trigger(req: TriggerRequest):
    if req.event == "rain":
        return {
            "status": "triggered",
            "payout": 150,
            "message": "Heavy rain detected 🌧️ → ₹150 credited"
        }
    return {"status": "no trigger"}

# -----------------------------
# 2. Fraud Detection
# -----------------------------
@app.post("/check-fraud")
def check_fraud(req: FraudRequest):
    if req.gps != req.ip:
        return {
            "fraud": True,
            "message": "GPS mismatch detected 🚨"
        }
    return {
        "fraud": False,
        "message": "Valid user ✅"
    }

# -----------------------------
# 3. Premium Calculation
# -----------------------------
@app.post("/get-premium")
def get_premium(req: PremiumRequest):
    base_price = 59
    
    if req.risk == "high":
        base_price += 20
    elif req.risk == "low":
        base_price -= 10

    return {
        "premium": base_price,
        "message": f"Weekly premium = ₹{base_price}"
    }