import CloudQueueIcon from "@mui/icons-material/CloudQueue";
import LaunchIcon from "@mui/icons-material/Launch";
import { Alert, Box, Button, Grid, Paper, Stack, TextField, Typography } from "@mui/material";
import { useCallback, useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import type { PolicyPayload, UserProfile, WeatherPayload } from "../api/client";
import { getUserProfile, postWeather } from "../api/client";
import { TrustMeter } from "../components/TrustMeter";
import { useGeoLocation } from "../hooks/useGeoLocation";
import { useUserId } from "../hooks/useUserId";

export function Dashboard() {
  const [userId] = useUserId();
  const nav = useNavigate();
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [city, setCity] = useState<string>("London");
  const [error, setError] = useState<string | null>(null);
  const [currentWeather, setCurrentWeather] = useState<WeatherPayload | null>(null);
  const [policy, setPolicy] = useState<PolicyPayload | null>(null);
  const { coords, error: gpsError, loading: gpsLoading, refresh: refreshGps } = useGeoLocation();

  const refreshProfile = useCallback(async () => {
    try {
      const p = await getUserProfile(userId);
      setProfile(p);
      setPolicy(p.policy ?? null);
      if (p.location.city) setCity(p.location.city);
    } catch {
      setProfile(null);
    }
  }, [userId]);

  useEffect(() => {
    void refreshProfile();
  }, [refreshProfile]);

  const onRefreshWeather = async () => {
    setError(null);
    try {
      const payload: { lat?: number; lon?: number; city?: string } = {};
      if (coords) {
        payload.lat = coords.lat;
        payload.lon = coords.lon;
      } else if (city) {
        payload.city = city;
      }
      const w = await postWeather(payload);
      setCurrentWeather(w);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Weather fetch failed");
    }
  };

  const trust = profile?.trust_score ?? 78;

  return (
    <Stack spacing={3}>
      <Box>
        <Typography variant="h4" fontWeight={700} gutterBottom>
          Live coverage cockpit
        </Typography>
        <Typography color="text.secondary" maxWidth={720}>
          Monitor active plan and weather context. Use the dedicated Claims page to create and validate disruption claims.
        </Typography>
      </Box>

      <Grid container spacing={2}>
        <Grid item xs={12} md={7}>
          <Paper sx={{ p: 3 }}>
            <Stack spacing={2}>
              <Stack direction="row" alignItems="center" spacing={1}>
                <CloudQueueIcon color="secondary" />
                <Typography variant="h6">Location & trigger</Typography>
              </Stack>
              <Alert severity={policy ? "success" : "info"}>
                {policy
                  ? `Active Plan: ${policy.plan.toUpperCase()}  |  Premium: ₹${policy.premium.toFixed(2)}`
                  : "No Active Plan"}
              </Alert>
              <Button
                variant="contained"
                endIcon={<LaunchIcon />}
                onClick={() => nav("/claims")}
                disabled={!policy}
              >
                Open Claims Page
              </Button>
              {!policy && <Alert severity="info">Select a premium plan before creating claims.</Alert>}
              <TextField
                label="City (fallback if no GPS)"
                value={city}
                onChange={(e) => setCity(e.target.value)}
                fullWidth
              />
              <Alert severity={coords ? "success" : "info"}>
                {coords
                  ? `GPS detected: ${coords.lat.toFixed(5)}, ${coords.lon.toFixed(5)}`
                  : "Using city fallback right now. Allow location access for GPS auto-detection."}
              </Alert>
              {gpsError && <Alert severity="warning">{gpsError}</Alert>}
              <Button variant="text" onClick={refreshGps} disabled={gpsLoading}>
                {gpsLoading ? "Refreshing GPS..." : "Refresh GPS location"}
              </Button>
              <Button variant="outlined" onClick={() => void onRefreshWeather()}>
                Refresh current weather
              </Button>
              {currentWeather && (
                <Alert severity="info">
                  Current weather: {currentWeather.condition}{" "}
                  {currentWeather.temperature_c != null ? `(${currentWeather.temperature_c}°C)` : ""}
                </Alert>
              )}
              {error && <Alert severity="error">{error}</Alert>}
            </Stack>
          </Paper>
        </Grid>
        <Grid item xs={12} md={5}>
          <Paper sx={{ p: 3 }}>
            <TrustMeter value={trust} />
            <Box sx={{ mt: 2 }}>
              <Typography>No. of claims triggered: {profile?.claims_count ?? 0}</Typography>
              <Typography>No. of claims accepted: {profile?.claims_approved_count ?? 0}</Typography>
            </Box>
          </Paper>
        </Grid>
      </Grid>
    </Stack>
  );
}
