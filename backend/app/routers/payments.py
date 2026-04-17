import hashlib
import hmac
import logging
import time

import httpx
from fastapi import APIRouter, HTTPException

from app.config import get_settings
from app.db.firestore_client import get_user, save_user
from app.models.schemas import (
    CreateOrderRequest,
    CreateOrderResponse,
    PolicyPayload,
    RazorpayOrderRequest,
    RazorpayOrderResponse,
    VerifyPaymentRequest,
)
from app.services.premium import compute_plans

router = APIRouter(tags=["payments"])
logger = logging.getLogger(__name__)
RAZORPAY_CURRENCY = "INR"


@router.post("/create-order", response_model=CreateOrderResponse)
def create_order(body: CreateOrderRequest) -> CreateOrderResponse:
    settings = get_settings()
    if not settings.razorpay_key_id or not settings.razorpay_key_secret:
        raise HTTPException(status_code=500, detail="Razorpay keys are not configured on server")
    if not settings.razorpay_key_id.startswith("rzp_test_"):
        logger.warning("Razorpay key is not a test key. Ensure test-mode credentials are configured.")

    plans = compute_plans(body.user_id)
    if body.plan not in plans:
        raise HTTPException(status_code=400, detail="Invalid plan")

    plan_price = float(plans[body.plan])
    requested_amount = float(body.amount)
    if abs(requested_amount - plan_price) > 1.0:
        logger.warning(
            "plan amount mismatch user_id=%s plan=%s requested=%s expected=%s; using expected price",
            body.user_id,
            body.plan,
            requested_amount,
            plan_price,
        )

    amount_paise = max(100, int(round(plan_price * 100)))
    payload = {
        "amount": amount_paise,
        "currency": RAZORPAY_CURRENCY,
        "receipt": f"{body.user_id[:20]}-{body.plan}",
        "notes": {"user_id": body.user_id, "plan": body.plan},
    }

    try:
        resp = httpx.post(
            "https://api.razorpay.com/v1/orders",
            json=payload,
            auth=(settings.razorpay_key_id, settings.razorpay_key_secret),
            timeout=15.0,
        )
        resp.raise_for_status()
        data = resp.json()
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail=f"Razorpay order creation failed: {exc}") from exc

    logger.info("razorpay order created order_id=%s user_id=%s plan=%s amount_paise=%s", data["id"], body.user_id, body.plan, amount_paise)
    return CreateOrderResponse(
        order_id=data["id"],
        key_id=settings.razorpay_key_id,
        amount_paise=amount_paise,
        currency=RAZORPAY_CURRENCY,
        plan=body.plan,
    )


@router.post("/payments/razorpay/order", response_model=RazorpayOrderResponse)
def create_legacy_razorpay_order(body: RazorpayOrderRequest) -> RazorpayOrderResponse:
    out = create_order(
        CreateOrderRequest(
            user_id=body.user_id,
            plan=body.tier,
            amount=float(compute_plans(body.user_id).get(body.tier, 0.0)),
        )
    )
    return RazorpayOrderResponse(
        order_id=out.order_id,
        key_id=out.key_id,
        amount_paise=out.amount_paise,
        currency=out.currency,
        plan=out.plan,
        plan_price=round(out.amount_paise / 100.0, 2),
    )


@router.post("/verify-payment", response_model=PolicyPayload)
def verify_payment(body: VerifyPaymentRequest) -> PolicyPayload:
    settings = get_settings()
    if not settings.razorpay_key_secret:
        raise HTTPException(status_code=500, detail="Razorpay key secret is not configured on server")

    user = get_user(body.user_id)
    existing = user.get("premium")
    if isinstance(existing, dict) and existing.get("status") == "active":
        return PolicyPayload(**existing)

    logger.info("verify payment request order_id=%s payment_id=%s user_id=%s", body.order_id, body.payment_id, body.user_id)
    digest = hmac.new(
        settings.razorpay_key_secret.encode("utf-8"),
        f"{body.order_id}|{body.payment_id}".encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()
    if not hmac.compare_digest(digest, body.signature):
        logger.warning("signature verification failed order_id=%s payment_id=%s", body.order_id, body.payment_id)
        raise HTTPException(status_code=400, detail="Invalid payment signature")
    logger.info("signature verification success order_id=%s", body.order_id)

    plans = compute_plans(body.user_id)
    premium = float(plans.get(body.plan, 0.0))
    premium_data = {
    "plan": body.plan,
    "paid_amount": round(premium, 2),
    "status": "active",
    "start_date": time.time(),
}

save_user(body.user_id, {"premium": premium_data})
    return PolicyPayload(**policy)
