/**
 * API client — uses VITE_API_URL in production; dev proxy maps /api → FastAPI.
 */
const base = (import.meta.env.VITE_API_URL ?? "/api").replace(/\/$/, "");

async function jsonFetch<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${base}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers ?? {}),
    },
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || res.statusText);
  }
  return res.json() as Promise<T>;
}

export type WeatherPayload = {
  condition: string;
  temperature_c: number | null;
  description: string;
  source: string;
};

export type AutoClaimResponse = {
  message: string;
  weather: WeatherPayload;
  fraud_score: number;
  trust_score: number;
  premium: Record<string, number>;
  decision: string;
  fraud_score_rule: number;
  ml_anomaly_score: number;
  fraud_probability: number;
  blocked_reason?: string | null;
  worker_online_at_disruption: boolean;
  worker_status_note: string;
};

export type UserProfile = {
  user_id: string;
  name: string;
  email: string;
  company: string;
  is_online: boolean;
  location: { lat: number | null; lon: number | null; city: string };
  trust_score: number;
  claims_count: number;
  claims_approved_count: number;
  policy?: PolicyPayload | null;
};

export type PremiumResponse = {
  user_id: string;
  trust_score: number;
  plans: Record<string, number>;
};

export type PolicyPayload = {
  plan: "basic" | "pro" | "elite";
  premium: number;
  status: string;
  created_at: number;
};

export type CreateOrderResponse = {
  order_id: string;
  key_id: string;
  amount_paise: number;
  currency: string;
  plan: "basic" | "pro" | "elite";
};

export type FraudRingCluster = {
  grid_key: string;
  time_bucket: string;
  user_ids: string[];
  claim_count: number;
  risk_level: string;
};

export type FraudRingsResponse = {
  rings: FraudRingCluster[];
  alerts: { type: string; severity: string; message: string; user_ids: string[] }[];
};

export type DisruptionSignalResponse = {
  disruption_score: number;
  disruption_type: string;
  trigger: boolean;
  threshold: number;
  signals: {
    weather: { temperature?: number | null; rainfall?: number | null; condition?: string; source?: string };
    traffic: { congestion_level?: string; delay_multiplier?: number; source?: string };
    aqi: { aqi?: number; category?: string; source?: string };
    news: { disruption_detected?: boolean; keywords_found?: string[]; source?: string };
    platform: { zone_status?: string; reason?: string; source?: string };
  };
};

export type VerificationStatusResponse = {
  backend_online: boolean;
  model_ready: boolean;
  mode: "active" | "training";
  model_artifact: string;
};

export function postAutoClaim(body: {
  user_id: string;
  lat?: number | null;
  lon?: number | null;
  city?: string | null;
  disruption_type?: string | null;
}) {
  return jsonFetch<AutoClaimResponse>("/auto-claim", {
    method: "POST",
    body: JSON.stringify(body),
  });
}

export function postWeather(body: { lat?: number | null; lon?: number | null; city?: string | null }) {
  return jsonFetch<WeatherPayload>("/weather", {
    method: "POST",
    body: JSON.stringify(body),
  });
}

export function getUserProfile(userId: string) {
  return jsonFetch<UserProfile>(`/user-profile/${encodeURIComponent(userId)}`);
}

export function putUserProfile(body: {
  user_id: string;
  name?: string;
  email?: string;
  company?: string;
  is_online?: boolean;
  location?: { lat?: number | null; lon?: number | null; city?: string | null };
}) {
  return jsonFetch<UserProfile>("/user-profile", {
    method: "PUT",
    body: JSON.stringify(body),
  });
}

export function postPremium(userId: string) {
  return jsonFetch<PremiumResponse>("/premium", {
    method: "POST",
    body: JSON.stringify({ user_id: userId }),
  });
}

export function postCreateOrder(body: { user_id: string; plan: "basic" | "pro" | "elite"; amount: number }) {
  return jsonFetch<CreateOrderResponse>("/create-order", {
    method: "POST",
    body: JSON.stringify(body),
  });
}

export function postVerifyPayment(body: {
  user_id: string;
  plan: "basic" | "pro" | "elite";
  order_id: string;
  payment_id: string;
  signature: string;
}) {
  return jsonFetch<PolicyPayload>("/verify-payment", {
    method: "POST",
    body: JSON.stringify(body),
  });
}

export function postSimulateDisruption(body: {
  city?: string | null;
  lat?: number | null;
  lon?: number | null;
  disruption_type?: string | null;
}) {
  return jsonFetch<DisruptionSignalResponse>("/simulate-disruption", {
    method: "POST",
    body: JSON.stringify(body),
  });
}

export function getFraudRings() {
  return jsonFetch<FraudRingsResponse>("/fraud-rings");
}

export function getVerificationStatus() {
  return jsonFetch<VerificationStatusResponse>("/verification-status");
}
