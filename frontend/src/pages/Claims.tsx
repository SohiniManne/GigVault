import PlaylistAddCheckIcon from "@mui/icons-material/PlaylistAddCheck";
import {
  Alert,
  Box,
  Button,
  FormControl,
  Grid,
  InputLabel,
  MenuItem,
  Paper,
  Select,
  Stack,
  TextField,
  Typography,
} from "@mui/material";
import { useCallback, useEffect, useState } from "react";
import type { AutoClaimResponse, DisruptionSignalResponse, UserProfile, VerificationStatusResponse } from "../api/client";
import { getUserProfile, getVerificationStatus, postAutoClaim, postSimulateDisruption } from "../api/client";
import { useGeoLocation } from "../hooks/useGeoLocation";
import { useUserId } from "../hooks/useUserId";

type DisruptionType =
  | "heavy_rain"
  | "flood"
  | "extreme_heat"
  | "severe_pollution"
  | "unplanned_curfew"
  | "local_strike"
  | "market_zone_closure";

const disruptionOptions: Array<{ value: DisruptionType; label: string; category: "Environmental" | "Social" }> = [
  { value: "heavy_rain", label: "Heavy rain", category: "Environmental" },
  { value: "flood", label: "Floods", category: "Environmental" },
  { value: "extreme_heat", label: "Extreme heat", category: "Environmental" },
  { value: "severe_pollution", label: "Severe pollution", category: "Environmental" },
  { value: "unplanned_curfew", label: "Unplanned curfews", category: "Social" },
  { value: "local_strike", label: "Local strikes", category: "Social" },
  { value: "market_zone_closure", label: "Sudden market/zone closures", category: "Social" },
];

export function Claims() {
  const [userId] = useUserId();
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [city, setCity] = useState("London");
  const [disruptionType, setDisruptionType] = useState<DisruptionType>("heavy_rain");
  const [loading, setLoading] = useState(false);
  const [signalsLoading, setSignalsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<AutoClaimResponse | null>(null);
  const [signals, setSignals] = useState<DisruptionSignalResponse | null>(null);
  const [verificationStatus, setVerificationStatus] = useState<VerificationStatusResponse | null>(null);
  const [verificationError, setVerificationError] = useState<string | null>(null);
  const { coords } = useGeoLocation();

  const refreshProfile = useCallback(async () => {
    const p = await getUserProfile(userId);
    setProfile(p);
    if (p.location.city) setCity(p.location.city);
  }, [userId]);

  useEffect(() => {
    void refreshProfile().catch(() => undefined);
  }, [refreshProfile]);

  const refreshSignals = useCallback(async () => {
    setSignalsLoading(true);
    try {
      const payload: Parameters<typeof postSimulateDisruption>[0] = {
        city: city || undefined,
        disruption_type: disruptionType,
      };
      if (coords) {
        payload.lat = coords.lat;
        payload.lon = coords.lon;
      }
      const out = await postSimulateDisruption(payload);
      setSignals(out);
    } finally {
      setSignalsLoading(false);
    }
  }, [city, coords, disruptionType]);

  useEffect(() => {
    void refreshSignals().catch(() => undefined);
  }, [refreshSignals]);

  useEffect(() => {
    let cancelled = false;
    const refreshVerification = async () => {
      try {
        const status = await getVerificationStatus();
        if (!cancelled) {
          setVerificationStatus(status);
          setVerificationError(null);
        }
      } catch {
        if (!cancelled) {
          setVerificationStatus(null);
          setVerificationError("Backend unavailable");
        }
      }
    };

    void refreshVerification();
    const timer = window.setInterval(() => {
      void refreshVerification();
    }, 15000);

    return () => {
      cancelled = true;
      window.clearInterval(timer);
    };
  }, []);

  const onCreateClaim = async () => {
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const body: Parameters<typeof postAutoClaim>[0] = {
        user_id: userId,
        city: city || undefined,
        disruption_type: disruptionType,
      };
      if (coords) {
        body.lat = coords.lat;
        body.lon = coords.lon;
      }
      const response = await postAutoClaim(body);
      setResult(response);
      await refreshProfile();
      await refreshSignals();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Claim creation failed");
    } finally {
      setLoading(false);
    }
  };

  const selected = disruptionOptions.find((o) => o.value === disruptionType);
  const isSocial = selected?.category === "Social";

  return (
    <Stack spacing={3}>
      <Box>
        <Typography variant="h4" fontWeight={700} gutterBottom>
          Claims
        </Typography>
        <Typography color="text.secondary">
          Create disruption-based claims and run weather + GPS + fraud validation.
        </Typography>
      </Box>

      <Grid container spacing={2}>
        <Grid item xs={12} md={7}>
          <Paper sx={{ p: 3 }}>
            <Stack spacing={2}>
              <Stack direction="row" spacing={1} alignItems="center">
                <PlaylistAddCheckIcon color="secondary" />
                <Typography variant="h6">Create claim</Typography>
              </Stack>
              {!profile?.policy && <Alert severity="info">No Active Plan. Select a plan in Premium first.</Alert>}
              <Alert severity={profile?.is_online ? "success" : "info"}>
                Worker status at claim time: {profile?.is_online ? "Online" : "Offline"}
              </Alert>
              <FormControl fullWidth>
                <InputLabel id="disruption-type-label">Disruption type</InputLabel>
                <Select
                  labelId="disruption-type-label"
                  value={disruptionType}
                  label="Disruption type"
                  onChange={(e) => setDisruptionType(e.target.value as DisruptionType)}
                >
                  {disruptionOptions.map((option) => (
                    <MenuItem key={option.value} value={option.value}>
                      {option.category}: {option.label}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
              {isSocial && (
                verificationError ? (
                  <Alert severity="error">
                    Social disruption auto-verification status unavailable ({verificationError}). Check backend connection.
                  </Alert>
                ) : verificationStatus?.mode === "active" ? (
                  <Alert severity="success">
                    Social disruption auto-verification is active. Model is ready and environmental triggers are live.
                  </Alert>
                ) : (
                  <Alert severity="warning">
                    Social disruption auto-verification is in training mode. Environmental triggers are active now.
                  </Alert>
                )
              )}
              <TextField
                label="City (fallback if GPS unavailable)"
                value={city}
                onChange={(e) => setCity(e.target.value)}
                fullWidth
              />
              <Button variant="contained" onClick={() => void onCreateClaim()} disabled={loading || !profile?.policy}>
                {loading ? "Evaluating claim..." : "Create claim"}
              </Button>
              <Button variant="outlined" onClick={() => void refreshSignals()} disabled={signalsLoading}>
                {signalsLoading ? "Refreshing signals..." : "Refresh live signals"}
              </Button>
              {error && <Alert severity="error">{error}</Alert>}
              {result && (
                <Alert severity={result.decision === "approved" ? "success" : result.decision === "blocked" ? "error" : "info"}>
                  <Typography fontWeight={600}>{result.message}</Typography>
                  <Typography variant="body2">Decision: {result.decision}</Typography>
                  <Typography variant="body2">{result.worker_status_note}</Typography>
                </Alert>
              )}
            </Stack>
          </Paper>
        </Grid>
        <Grid item xs={12} md={5}>
          <Paper sx={{ p: 3 }}>
            <Stack spacing={1}>
              <Typography variant="h6">Claim stats</Typography>
              <Typography>No. of claims triggered: {profile?.claims_count ?? 0}</Typography>
              <Typography>No. of claims accepted: {profile?.claims_approved_count ?? 0}</Typography>
              <Typography>
                Acceptance rate:{" "}
                {profile && profile.claims_count > 0
                  ? `${((profile.claims_approved_count / profile.claims_count) * 100).toFixed(1)}%`
                  : "0.0%"}
              </Typography>
            </Stack>
          </Paper>
        </Grid>
        <Grid item xs={12}>
          <Grid container spacing={2}>
            <Grid item xs={12} md={6} lg={4}>
              <Paper sx={{ p: 2 }}>
                <Typography variant="subtitle2">Weather</Typography>
                <Typography variant="body2">
                  {signals
                    ? `${signals.signals.weather.condition ?? "unknown"} | ${signals.signals.weather.rainfall ?? 0} mm`
                    : "No data"}
                </Typography>
              </Paper>
            </Grid>
            <Grid item xs={12} md={6} lg={4}>
              <Paper sx={{ p: 2 }}>
                <Typography variant="subtitle2">AQI</Typography>
                <Typography variant="body2">
                  {signals
                    ? `${signals.signals.aqi.aqi ?? "--"} (${signals.signals.aqi.category ?? "unknown"})`
                    : "No data"}
                </Typography>
              </Paper>
            </Grid>
            <Grid item xs={12} md={6} lg={4}>
              <Paper sx={{ p: 2 }}>
                <Typography variant="subtitle2">Traffic</Typography>
                <Typography variant="body2">
                  {signals
                    ? `${signals.signals.traffic.congestion_level ?? "unknown"} (${signals.signals.traffic.delay_multiplier ?? 1}x)`
                    : "No data"}
                </Typography>
              </Paper>
            </Grid>
            <Grid item xs={12} md={6} lg={4}>
              <Paper sx={{ p: 2 }}>
                <Typography variant="subtitle2">News</Typography>
                <Typography variant="body2">
                  {signals
                    ? signals.signals.news.disruption_detected
                      ? `Detected: ${(signals.signals.news.keywords_found ?? []).join(", ") || "keywords"}`
                      : "No disruption keywords"
                    : "No data"}
                </Typography>
              </Paper>
            </Grid>
            <Grid item xs={12} md={6} lg={4}>
              <Paper sx={{ p: 2 }}>
                <Typography variant="subtitle2">Platform</Typography>
                <Typography variant="body2">
                  {signals
                    ? `${signals.signals.platform.zone_status ?? "unknown"} | ${signals.signals.platform.reason ?? ""}`
                    : "No data"}
                </Typography>
              </Paper>
            </Grid>
          </Grid>
          {signals && (
            <Alert sx={{ mt: 2 }} severity={signals.trigger ? "warning" : "info"}>
              Disruption score: {signals.disruption_score} / 100 | Type: {signals.disruption_type} | Trigger:{" "}
              {signals.trigger ? "Yes" : "No"}
            </Alert>
          )}
        </Grid>
      </Grid>
    </Stack>
  );
}
