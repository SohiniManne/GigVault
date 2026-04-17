import {
  Alert,
  Box,
  Button,
  MenuItem,
  Paper,
  Stack,
  TextField,
  Typography,
} from "@mui/material";
import { useEffect, useState } from "react";
import { getUserProfile, putUserProfile } from "../api/client";
import { useUserId } from "../hooks/useUserId";

export default function Signup() {
  const [userId] = useUserId();

  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [company, setCompany] = useState("");
  const [city, setCity] = useState("");
  const [workingStatus, setWorkingStatus] = useState("Offline");

  const [lat, setLat] = useState<number | null>(null);
  const [lon, setLon] = useState<number | null>(null);

  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [msg, setMsg] = useState<string | null>(null);

  // ✅ LOAD PROFILE
  useEffect(() => {
    if (!userId) return;

    const loadProfile = async () => {
      try {
        const data = await getUserProfile(userId);

        setName(data.name || "");
        setEmail(data.email || "");
        setCompany(data.company || "");
        setCity(data.location?.city || "");
        setWorkingStatus(data.is_online ? "Online" : "Offline");

        setLat(data.location?.lat ?? null);
        setLon(data.location?.lon ?? null);
      } catch (err) {
        console.error(err);
        setMsg("❌ Failed to load profile");
      } finally {
        setLoading(false);
      }
    };

    loadProfile();
  }, [userId]);

  // ✅ SAVE PROFILE
  const handleSave = async () => {
    if (!userId) return;

    setSaving(true);
    setMsg(null);

    try {
      await putUserProfile({
        user_id: userId,
        name,
        email,
        company,
        is_online: workingStatus === "Online",
        location: {
          lat,
          lon,
          city,
        },
      });

      setMsg("✅ Profile saved successfully");
    } catch (err) {
      console.error(err);
      setMsg("❌ Failed to save profile");
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <Box sx={{ p: 4 }}>
        <Typography>Loading profile...</Typography>
      </Box>
    );
  }

  return (
    <Box sx={{ display: "grid", placeItems: "center", py: 4 }}>
      <Paper sx={{ p: 3, width: "100%", maxWidth: 500 }}>
        <Stack spacing={2}>
          <Typography variant="h5" fontWeight={700}>
            Profile
          </Typography>

          {msg && <Alert severity="info">{msg}</Alert>}

          <TextField label="User ID" value={userId || ""} disabled />

          <TextField
            label="Name"
            value={name}
            onChange={(e) => setName(e.target.value)}
          />

          <TextField
            label="Email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />

          <TextField
            label="Company you work for"
            value={company}
            onChange={(e) => setCompany(e.target.value)}
          />

          <TextField
            select
            label="Working status"
            value={workingStatus}
            onChange={(e) => setWorkingStatus(e.target.value)}
          >
            <MenuItem value="Online">Online</MenuItem>
            <MenuItem value="Offline">Offline</MenuItem>
          </TextField>

          <TextField
            label="City"
            value={city}
            onChange={(e) => setCity(e.target.value)}
          />

          <Button
            variant="contained"
            onClick={handleSave}
            disabled={saving}
          >
            {saving ? "Saving..." : "Save profile"}
          </Button>
        </Stack>
      </Paper>
    </Box>
  );
}
