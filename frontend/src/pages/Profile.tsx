import SaveIcon from "@mui/icons-material/Save";
import {
  Alert,
  Button,
  FormControl,
  InputLabel,
  MenuItem,
  Paper,
  Select,
  Stack,
  TextField,
  Typography,
} from "@mui/material";
import { useCallback, useEffect, useState } from "react";

import type { UserProfile } from "../api/client";
import { getUserProfile, putUserProfile } from "../api/client";
import { getFirebaseAuth } from "../firebase";
import { useGeoLocation } from "../hooks/useGeoLocation";
import { useUserId } from "../hooks/useUserId";

export default function Profile() {
  const [userId] = useUserId();

  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [company, setCompany] = useState("");
  const [isOnline, setIsOnline] = useState(false);
  const [city, setCity] = useState("");

  const [msg, setMsg] = useState<string | null>(null);
  const [err, setErr] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [initialLoading, setInitialLoading] = useState(true);

  const { coords, error: gpsError, loading: gpsLoading, refresh: refreshGps } =
    useGeoLocation();

  // ✅ LOAD PROFILE (SAFE)
  const load = useCallback(async () => {
    if (!userId) return;

    try {
      const p: UserProfile = await getUserProfile(userId);

      setName(p.name || "");
      setEmail(p.email || "");
      setCompany(p.company ?? "");
      setIsOnline(Boolean(p.is_online));
      setCity(p.location?.city ?? "");
    } catch {
      setErr("❌ Could not load profile (backend issue?)");
    } finally {
      setInitialLoading(false);
    }
  }, [userId]);

  useEffect(() => {
    void load();
  }, [load]);

  // ✅ FILL FROM FIREBASE (fallback)
  useEffect(() => {
    const auth = getFirebaseAuth();
    const current = auth?.currentUser;

    if (!current) return;

    if (!email && current.email) setEmail(current.email);
    if (!name && current.displayName) setName(current.displayName);
  }, [email, name]);

  // ✅ SAVE PROFILE (ONLY BACKEND)
  const onSave = async () => {
    if (!userId) return;

    setLoading(true);
    setErr(null);
    setMsg(null);

    const lat = coords?.lat;
    const lon = coords?.lon;

    try {
      await putUserProfile({
        user_id: userId,
        name,
        email,
        company,
        is_online: isOnline,
        location: {
          city: city || undefined,
          lat:
            lat !== undefined && !Number.isNaN(lat) ? lat : undefined,
          lon:
            lon !== undefined && !Number.isNaN(lon) ? lon : undefined,
        },
      });

      setMsg("✅ Profile saved successfully");

      // reload fresh data
      await load();
    } catch (e) {
      setErr(e instanceof Error ? e.message : "❌ Save failed");
    } finally {
      setLoading(false);
    }
  };

  // ✅ LOADING STATE
  if (initialLoading) {
    return (
      <Stack p={3}>
        <Typography>Loading profile...</Typography>
      </Stack>
    );
  }

  return (
    <Stack spacing={3} maxWidth={560}>
      <Typography variant="h4" fontWeight={700}>
        Worker profile
      </Typography>

      <Typography color="text.secondary">
        Identity and service area. Location helps with disruption detection.
      </Typography>

      <Paper sx={{ p: 3 }}>
        <Stack spacing={2}>
          <TextField
            label="User ID (Firebase UID)"
            value={userId || ""}
            disabled
            fullWidth
          />

          <TextField
            label="Name"
            value={name}
            onChange={(e) => setName(e.target.value)}
            fullWidth
          />

          <TextField
            label="Email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            fullWidth
          />

          <TextField
            label="Company you work for"
            value={company}
            onChange={(e) => setCompany(e.target.value)}
            fullWidth
          />

          <FormControl fullWidth>
            <InputLabel>Working status</InputLabel>
            <Select
              label="Working status"
              value={isOnline ? "online" : "offline"}
              onChange={(e) => setIsOnline(e.target.value === "online")}
            >
              <MenuItem value="online">Online</MenuItem>
              <MenuItem value="offline">Offline</MenuItem>
            </Select>
          </FormControl>

          <TextField
            label="City"
            value={city}
            onChange={(e) => setCity(e.target.value)}
            fullWidth
          />

          {/* GPS */}
          <Alert severity={coords ? "success" : "info"}>
            {coords
              ? `GPS: ${coords.lat.toFixed(5)}, ${coords.lon.toFixed(5)}`
              : "Enable location for auto-detection"}
          </Alert>

          {gpsError && <Alert severity="warning">{gpsError}</Alert>}

          <Button
            variant="text"
            onClick={refreshGps}
            disabled={gpsLoading || loading}
          >
            {gpsLoading ? "Refreshing GPS..." : "Refresh GPS"}
          </Button>

          {/* SAVE BUTTON */}
          <Button
            variant="contained"
            startIcon={<SaveIcon />}
            onClick={onSave}
            disabled={loading}
          >
            {loading ? "Saving..." : "Save profile"}
          </Button>

          {/* STATUS */}
          {msg && <Alert severity="success">{msg}</Alert>}
          {err && <Alert severity="error">{err}</Alert>}
        </Stack>
      </Paper>
    </Stack>
  );
}
