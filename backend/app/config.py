"""
Central settings loaded from environment. No secrets in code.
"""
from functools import lru_cache
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    openweather_api_key: str = ""
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"
    firebase_credentials_path: str = ""
    firebase_credentials_json: str = ""
    port: int = 8000

    # Fraud / GPS thresholds (tunable without code changes via env if extended)
    gps_speed_threshold_ms: float = 90.0  # ~324 km/h — flags impossible surface travel
    fraud_block_threshold: float = 85.0
    repeated_claim_hours: int = 24
    max_recent_claims_for_repeat: int = 2
    trust_delta_fraud: float = 8.0
    trust_delta_valid_claim: float = 3.0
    trust_min: float = 0.0
    trust_max: float = 100.0
    premium_base_basic: float = 29.0
    premium_base_pro: float = 59.0
    premium_base_elite: float = 99.0
    premium_trust_multiplier: float = 0.45
    razorpay_key_id: str = ""
    razorpay_key_secret: str = ""
    razorpay_currency: str = "INR"
    tomorrow_api_key: str = ""
    news_api_key: str = ""
    google_maps_api_key: str = ""
    disruption_threshold: float = 60.0

    @property
    def cors_origin_list(self) -> List[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
