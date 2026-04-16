import CheckCircleIcon from "@mui/icons-material/CheckCircle";
import { Alert, Box, Button, Card, CardActions, CardContent, Chip, Grid, Paper, Stack, Typography } from "@mui/material";
import { useCallback, useEffect, useState } from "react";
import type { CreateOrderResponse, PolicyPayload, PremiumResponse } from "../api/client";
import { getUserProfile, postCreateOrder, postPremium, postVerifyPayment } from "../api/client";
import { TrustMeter } from "../components/TrustMeter";
import { useUserId } from "../hooks/useUserId";

const features: Record<string, string[]> = {
  basic: ["Heavy rain trigger only", "Email support", "48h payouts"],
  pro: ["Moderate rain trigger", "Priority fraud review", "24h payouts"],
  elite: ["Fast-track approval", "Lower fraud strictness", "6h payouts"],
};

type Tier = "basic" | "pro" | "elite";

declare global {
  interface Window {
    Razorpay?: new (options: Record<string, unknown>) => {
      open: () => void;
      on: (event: string, callback: (response: Record<string, unknown>) => void) => void;
    };
  }
}

let razorpayScriptPromise: Promise<void> | null = null;

function loadRazorpayScript(): Promise<void> {
  if (window.Razorpay) return Promise.resolve();
  if (razorpayScriptPromise) return razorpayScriptPromise;
  razorpayScriptPromise = new Promise((resolve, reject) => {
    const script = document.createElement("script");
    script.src = "https://checkout.razorpay.com/v1/checkout.js";
    script.async = true;
    script.onload = () => resolve();
    script.onerror = () => reject(new Error("Could not load Razorpay checkout script"));
    document.body.appendChild(script);
  });
  return razorpayScriptPromise;
}

export function Premium() {
  const [userId] = useUserId();
  const [data, setData] = useState<PremiumResponse | null>(null);
  const [err, setErr] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [selectingTier, setSelectingTier] = useState<Tier | null>(null);
  const [activePolicy, setActivePolicy] = useState<PolicyPayload | null>(null);

  const refreshPolicy = useCallback(async () => {
    const profile = await getUserProfile(userId);
    setActivePolicy(profile.policy ?? null);
  }, [userId]);

  useEffect(() => {
    void postPremium(userId)
      .then(setData)
      .catch((e) => setErr(e instanceof Error ? e.message : "Failed to load premiums"));
    void refreshPolicy().catch(() => undefined);
  }, [refreshPolicy, userId]);

  const handleChoosePlan = async (tier: Tier) => {
    if (activePolicy?.status === "active") return;
    setErr(null);
    setSuccess(null);
    setSelectingTier(tier);
    try {
      await loadRazorpayScript();
      if (!window.Razorpay) throw new Error("Razorpay SDK unavailable");

      const selectedAmount = Number(data?.plans[tier] ?? 0);
      if (!Number.isFinite(selectedAmount) || selectedAmount <= 0) {
        throw new Error("Invalid plan price");
      }
      const order: CreateOrderResponse = await postCreateOrder({
        user_id: userId,
        plan: tier,
        amount: selectedAmount,
      });
      if (!order.order_id) throw new Error("Backend did not return order_id");
      if ((order.currency || "").toUpperCase() !== "INR") {
        throw new Error(`Invalid currency from backend: ${order.currency}. Expected INR.`);
      }

      await new Promise<void>((resolve, reject) => {
        const checkout = new window.Razorpay!({
          key: order.key_id,
          amount: order.amount_paise,
          currency: "INR",
          name: "GigVault",
          description: `${tier.toUpperCase()} plan`,
          order_id: order.order_id,
          prefill: { name: userId },
          notes: { user_id: userId, plan: tier },
          handler: async (response: Record<string, unknown>) => {
            try {
              const paymentId = String(response.razorpay_payment_id ?? "");
              const signature = String(response.razorpay_signature ?? "");
              const returnedOrderId = String(response.razorpay_order_id ?? order.order_id);
              if (!paymentId || !signature || !returnedOrderId) {
                throw new Error("Payment response missing required fields");
              }
              const policy = await postVerifyPayment({
                user_id: userId,
                plan: tier,
                order_id: returnedOrderId,
                payment_id: paymentId,
                signature,
              });
              setActivePolicy(policy);
              setSuccess(`Plan Activated: ${policy.plan.toUpperCase()} (₹${policy.premium.toFixed(2)})`);
              await refreshPolicy();
              resolve();
            } catch (verifyError) {
              reject(verifyError);
            }
          },
          modal: {
            ondismiss: () => reject(new Error("Payment cancelled")),
          },
        });
        checkout.on("payment.failed", (payload: Record<string, unknown>) => {
          const errorObj = (payload.error ?? {}) as Record<string, unknown>;
          const reason = String(errorObj.description ?? errorObj.reason ?? "unknown error");
          reject(new Error(`Payment failed: ${reason}. Plan not activated.`));
        });
        checkout.open();
      });
    } catch (e) {
      setErr(e instanceof Error ? e.message : "Failed to select plan");
    } finally {
      setSelectingTier(null);
    }
  };

  const hasActivePlan = activePolicy?.status === "active";

  return (
    <Stack spacing={3}>
      <Box>
        <Typography variant="h4" fontWeight={700} gutterBottom>
          Premium plans
        </Typography>
        <Typography color="text.secondary" maxWidth={720}>
          Choose one active plan to power policy-based claim rules.
        </Typography>
      </Box>

      <Paper sx={{ p: 3 }}>
        <TrustMeter value={data?.trust_score ?? 78} />
        <Typography sx={{ mt: 2 }}>
          {hasActivePlan
            ? `Active Plan: ${activePolicy.plan.toUpperCase()}  |  Premium: ₹${activePolicy.premium.toFixed(2)}`
            : "No Active Plan"}
        </Typography>
        {success && <Alert severity="success" sx={{ mt: 2 }}>{success}</Alert>}
        {err && <Alert severity="error" sx={{ mt: 2 }}>{err}</Alert>}
      </Paper>

      <Grid container spacing={2}>
        {(["basic", "pro", "elite"] as const).map((tier) => (
          <Grid item xs={12} md={4} key={tier}>
            <Card sx={{ height: "100%", display: "flex", flexDirection: "column" }}>
              <CardContent sx={{ flex: 1 }}>
                <Stack direction="row" justifyContent="space-between" alignItems="center">
                  <Typography variant="h6" sx={{ textTransform: "capitalize" }}>
                    {tier}
                  </Typography>
                  {tier === "pro" && <Chip label="Popular" color="secondary" size="small" />}
                </Stack>
                <Typography variant="h3" sx={{ mt: 2, fontWeight: 800 }}>
                  ₹{data?.plans[tier]?.toFixed(2) ?? "—"}
                </Typography>
                <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                  per week
                </Typography>
                <Stack spacing={1}>
                  {(features[tier] ?? []).map((f) => (
                    <Stack direction="row" spacing={1} key={f} alignItems="center">
                      <CheckCircleIcon color="success" fontSize="small" />
                      <Typography variant="body2">{f}</Typography>
                    </Stack>
                  ))}
                </Stack>
              </CardContent>
              <CardActions sx={{ p: 2, pt: 0 }}>
                <Button
                  fullWidth
                  variant={tier === "pro" ? "contained" : "outlined"}
                  onClick={() => void handleChoosePlan(tier)}
                  disabled={hasActivePlan || selectingTier !== null}
                >
                  {hasActivePlan
                    ? "Plan active"
                    : selectingTier === tier
                      ? "Saving policy..."
                      : `Choose ${tier}`}
                </Button>
              </CardActions>
            </Card>
          </Grid>
        ))}
      </Grid>
    </Stack>
  );
}
