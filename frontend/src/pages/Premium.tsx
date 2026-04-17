import CheckCircleIcon from "@mui/icons-material/CheckCircle";
import {
  Alert,
  Box,
  Button,
  Card,
  CardActions,
  CardContent,
  Chip,
  Grid,
  Paper,
  Stack,
  Typography,
} from "@mui/material";
import { useCallback, useEffect, useState } from "react";
import type {
  CreateOrderResponse,
  PolicyPayload,
  PremiumResponse,
} from "../api/client";
import {
  getUserProfile,
  postCreateOrder,
  postPremium,
  postVerifyPayment,
} from "../api/client";
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
    Razorpay?: any;
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
    script.onerror = () => reject(new Error("Failed to load Razorpay"));
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
    postPremium(userId).then(setData).catch(() => {});
    refreshPolicy();
  }, [userId, refreshPolicy]);

  const handleChoosePlan = async (tier: Tier) => {
    if (activePolicy?.status === "active") return;

    setErr(null);
    setSuccess(null);
    setSelectingTier(tier);

    try {
      await loadRazorpayScript();

      const price = Number(data?.plans[tier] ?? 0);
      if (!price) throw new Error("Invalid plan price");

      const order: CreateOrderResponse = await postCreateOrder({
        user_id: userId,
        plan: tier,
        amount: price,
      });

      await new Promise<void>((resolve, reject) => {
        const rzp = new window.Razorpay({
          key: order.key_id,
          amount: order.amount_paise,
          currency: "INR",
          name: "GigVault",
          description: `${tier.toUpperCase()} Plan`,
          order_id: order.order_id,

          handler: async (response: any) => {
            try {
              console.log("🔥 PAYMENT RESPONSE:", response);

              const policy = await postVerifyPayment({
                user_id: userId,
                plan: tier,
                order_id: response.razorpay_order_id,
                payment_id: response.razorpay_payment_id,
                signature: response.razorpay_signature,
              });

              console.log("🔥 POLICY SAVED:", policy);

              setActivePolicy(policy);
              setSuccess(`Plan Activated: ${policy.plan}`);
              await refreshPolicy();

              resolve();
            } catch (e) {
              console.error("❌ VERIFY ERROR:", e);
              reject(new Error("Payment verified but saving failed"));
            }
          },

          modal: {
            ondismiss: () => reject(new Error("Payment cancelled")),
          },
        });

        rzp.on("payment.failed", (err: any) => {
          console.error("❌ PAYMENT FAILED:", err);
          reject(new Error("Payment failed"));
        });

        rzp.open();
      });
    } catch (e: any) {
      setErr(e.message);
    } finally {
      setSelectingTier(null);
    }
  };

  const hasActivePlan = activePolicy?.status === "active";

  return (
    <Stack spacing={3}>
      <Box>
        <Typography variant="h4" fontWeight={700}>
          Premium Plans
        </Typography>
      </Box>

      <Paper sx={{ p: 3 }}>
        <TrustMeter value={data?.trust_score ?? 70} />

        <Typography sx={{ mt: 2 }}>
          {hasActivePlan
            ? `Active: ${activePolicy.plan}`
            : "No Active Plan"}
        </Typography>

        {success && <Alert severity="success">{success}</Alert>}
        {err && <Alert severity="error">{err}</Alert>}
      </Paper>

      <Grid container spacing={2}>
        {(["basic", "pro", "elite"] as const).map((tier) => (
          <Grid item xs={12} md={4} key={tier}>
            <Card>
              <CardContent>
                <Typography variant="h6">{tier}</Typography>

                <Typography variant="h3">
                  ₹{data?.plans[tier]?.toFixed(2)}
                </Typography>

                {features[tier].map((f) => (
                  <Typography key={f}>{f}</Typography>
                ))}
              </CardContent>

              <CardActions>
                <Button
                  fullWidth
                  onClick={() => handleChoosePlan(tier)}
                  disabled={hasActivePlan || selectingTier !== null}
                >
                  {hasActivePlan
                    ? "Active"
                    : selectingTier === tier
                    ? "Processing..."
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
