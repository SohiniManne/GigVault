import SaveIcon from "@mui/icons-material/Save";
import { Alert, Button, FormControl, InputLabel, MenuItem, Paper, Select, Stack, TextField, Typography } from "@mui/material";
import { doc, setDoc } from "firebase/firestore";
import { useCallback, useEffect, useState } from "react";
import type { UserProfile } from "../api/client";
import { getUserProfile, putUserProfile } from "../api/client";
import { getDb, getFirebaseAuth } from "../firebase";
import { useGeoLocation } from "../hooks/useGeoLocation";
import { useUserId } from "../hooks/useUserId";

export function Profile() {
  const [userId] = useUserId();
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [company, setCompany] = useState("");
  const [isOnline, setIsOnline] = useState(false);
  const [city, setCity] = useState("");
  const [msg, setMsg] = useState<string | null>(null);
  const [err, setErr] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const { coords, error: gpsError, loading: gpsLoading, refresh: refreshGps } = useGeoLocation();

  const load = useCallback(async () => {
    try {
      const p: UserProfile = await getUserProfile(userId);
      setName(p.name);
      setEmail(p.email);
      setCompany(p.company ?? "");
      setIsOnline(Boolean(p.is_online));
      setCity(p.location.city ?? "");
    } catch {
      setErr("Could not load profile from API (is the backend running?)");
    }
  }, [userId]);

  useEffect(() => {
    void load();
  }, [load]);

  useEffect(() => {
    const auth = getFirebaseAuth();
    const current = auth?.currentUser;
    if (!current) return;
    if (!email && current.email) setEmail(current.email);
    if (!name && current.displayName) setName(current.displayName);
  }, [email, name]);

  const onSave = async () => {
    setLoading(true);
    setErr(null);
    setMsg(null);
    const la = coords?.lat;
    const lo = coords?.lon;
    try {
      await putUserProfile({
        user_id: userId,
        name,
        email,
        company,
        is_online: isOnline,
        location: {
          city: city || undefined,
          lat: la !== undefined && !Number.isNaN(la) ? la : undefined,
          lon: lo !== undefined && !Number.isNaN(lo) ? lo : undefined,
        },
      });

      const db = getDb();
      if (db) {
        await setDoc(
          doc(db, "users", userId),
          {
            name,
            email,
            company,
            is_online: isOnline,
            city,
            lat: la !== undefined && !Number.isNaN(la) ? la : null,
            lon: lo !== undefined && !Number.isNaN(lo) ? lo : null,
            updatedAt: new Date().toISOString(),
          },
          { merge: true },
        );
        setMsg("Saved to API and Firebase Firestore.");
      } else {
        setMsg("Saved to API. Add Firebase web env vars to mirror in Firestore.");
      }
      await load();
    } catch (e) {
      setErr(e instanceof Error ? e.message : "Save failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <Stack spacing={3} maxWidth={560}>
      <Typography variant="h4" fontWeight={700}>
        Worker profile
      </Typography>
      <Typography color="text.secondary">
        Identity and service area. Location drives weather verification and GPS intelligence.
      </Typography>
      <Paper sx={{ p: 3 }}>
        <Stack spacing={2}>
          <TextField label="User ID (Firebase UID)" value={userId} disabled fullWidth />
          <TextField label="Name" value={name} onChange={(e) => setName(e.target.value)} fullWidth />
          <TextField label="Email" value={email} onChange={(e) => setEmail(e.target.value)} fullWidth />
          <TextField
            label="Company you work for"
            value={company}
            onChange={(e) => setCompany(e.target.value)}
            fullWidth
          />
          <FormControl fullWidth>
            <InputLabel id="worker-status-label">Working status</InputLabel>
            <Select
              labelId="worker-status-label"
              label="Working status"
              value={isOnline ? "online" : "offline"}
              onChange={(e) => setIsOnline(e.target.value === "online")}
            >
              <MenuItem value="online">Online</MenuItem>
              <MenuItem value="offline">Offline</MenuItem>
            </Select>
          </FormControl>
          <TextField label="City" value={city} onChange={(e) => setCity(e.target.value)} fullWidth />
          <Alert severity={coords ? "success" : "info"}>
            {coords
              ? `GPS auto-detected: ${coords.lat.toFixed(5)}, ${coords.lon.toFixed(5)}`
              : "GPS not detected yet. Allow location permission to auto-fill coordinates."}
          </Alert>
          {gpsError && <Alert severity="warning">{gpsError}</Alert>}
          <Button variant="text" onClick={refreshGps} disabled={gpsLoading || loading}>
            {gpsLoading ? "Refreshing GPS..." : "Refresh GPS location"}
          </Button>
          <Button
            variant="contained"
            startIcon={<SaveIcon />}
            onClick={() => void onSave()}
            disabled={loading}
          >
            Save profile
          </Button>
          {msg && <Alert severity="success">{msg}</Alert>}
          {err && <Alert severity="error">{err}</Alert>}
        </Stack>
      </Paper>
    </Stack>
  );
}
