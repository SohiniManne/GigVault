from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class LocationInput(BaseModel):
    lat: Optional[float] = None
    lon: Optional[float] = None
    city: Optional[str] = None


class WeatherRequest(BaseModel):
    lat: Optional[float] = None
    lon: Optional[float] = None
    city: Optional[str] = None


class UserProfileIn(BaseModel):
    user_id: str = Field(..., min_length=1)
    name: Optional[str] = None
    email: Optional[str] = None
    company: Optional[str] = None
    is_online: Optional[bool] = None
    location: Optional[LocationInput] = None


class AutoClaimRequest(BaseModel):
    user_id: str = Field(..., min_length=1)
    lat: Optional[float] = None
    lon: Optional[float] = None
    city: Optional[str] = None
    disruption_type: Optional[str] = None


class FraudScoreRequest(BaseModel):
    user_id: str
    lat: Optional[float] = None
    lon: Optional[float] = None
    city: Optional[str] = None
    simulate_claim_attempt: bool = True


class PremiumQuery(BaseModel):
    user_id: str


class SelectPolicyRequest(BaseModel):
    user_id: str = Field(..., min_length=1)
    plan: str = Field(..., pattern="^(basic|pro|elite)$")


class CreateOrderRequest(BaseModel):
    user_id: str = Field(..., min_length=1)
    plan: str = Field(..., pattern="^(basic|pro|elite)$")
    amount: float = Field(..., gt=0)


class CreateOrderResponse(BaseModel):
    order_id: str
    key_id: str
    amount_paise: int
    currency: str
    plan: str


class VerifyPaymentRequest(BaseModel):
    user_id: str = Field(..., min_length=1)
    plan: str = Field(..., pattern="^(basic|pro|elite)$")
    order_id: str = Field(..., min_length=1)
    payment_id: str = Field(..., min_length=1)
    signature: str = Field(..., min_length=1)


class PolicyPayload(BaseModel):
    plan: str
    premium: float
    status: str
    created_at: float


class RazorpayOrderRequest(BaseModel):
    user_id: str = Field(..., min_length=1)
    tier: str = Field(..., pattern="^(basic|pro|elite)$")


class WeatherPayload(BaseModel):
    condition: str = "unknown"
    temperature_c: Optional[float] = None
    rainfall_mm: Optional[float] = None
    description: str = ""
    source: str = "unavailable"


class AutoClaimResponse(BaseModel):
    message: str
    weather: WeatherPayload
    fraud_score: float
    trust_score: float
    premium: Dict[str, float]
    decision: str = ""
    fraud_score_rule: float = 0.0
    ml_anomaly_score: float = 0.0
    fraud_probability: float = 0.0
    blocked_reason: Optional[str] = None
    worker_online_at_disruption: bool = False
    worker_status_note: str = ""


class FraudScoreResponse(BaseModel):
    fraud_score: float
    fraud_score_rule: float
    ml_anomaly_score: float
    fraud_probability: float
    signals: Dict[str, Any]
    weather: WeatherPayload


class UserProfileOut(BaseModel):
    user_id: str
    name: str
    email: str
    company: str = ""
    is_online: bool = False
    location: Dict[str, Any]
    trust_score: float
    claims_count: int
    claims_approved_count: int
    policy: Optional[PolicyPayload] = None


class PremiumResponse(BaseModel):
    user_id: str
    trust_score: float
    plans: Dict[str, float]


class RazorpayOrderResponse(BaseModel):
    order_id: str
    key_id: str
    amount_paise: int
    currency: str
    plan: str
    plan_price: float


class FraudRingCluster(BaseModel):
    grid_key: str
    time_bucket: str
    user_ids: List[str]
    claim_count: int
    risk_level: str


class FraudRingsResponse(BaseModel):
    rings: List[FraudRingCluster]
    alerts: List[Dict[str, Any]]
