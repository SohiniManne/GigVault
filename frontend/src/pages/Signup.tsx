import {
  Alert,
  Box,
  Button,
  Paper,
  Stack,
  TextField,
  Typography,
} from "@mui/material";
import {
  createUserWithEmailAndPassword,
  updateProfile,
} from "firebase/auth";
import { type FormEvent, useState } from "react";
import { useNavigate } from "react-router-dom";
import { getFirebaseAuth } from "../firebase";
import { useUserId } from "../hooks/useUserId";

const API_BASE = "https://gigvault-backend.onrender.com";

export default function Signup() {
  const [email, setEmail] = useState("");
  const [name, setName] = useState("");
  const [password, setPassword] = useState("");
  const [confirm, setConfirm] = useState("");
  const [err, setErr] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const nav = useNavigate();
  const [, setUserId] = useUserId();

  const onSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setErr(null);

    if (password !== confirm) {
      setErr("Passwords do not match");
      return;
    }

    const auth = getFirebaseAuth();
    if (!auth) {
      setErr("Firebase not configured");
      return;
    }

    setLoading(true);

    try {
      // ✅ 1. CREATE FIREBASE USER
      const credential = await createUserWithEmailAndPassword(
        auth,
        email.trim(),
        password
      );

      const uid = credential.user.uid;

      // ✅ 2. SET DISPLAY NAME (Firebase)
      if (name.trim()) {
        await updateProfile(credential.user, {
          displayName: name.trim(),
        });
      }

      // ✅ 3. SAVE USER ID LOCALLY
      setUserId(uid);

      // ✅ 4. SAVE PROFILE TO BACKEND (🔥 IMPORTANT)
      await fetch(`${API_BASE}/user-profile`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          user_id: uid,
          name: name.trim(),
          email: email.trim(),
          company: "",
          is_online: false,
          location: {
            city: "",
            lat: null,
            lon: null,
          },
        }),
      });

      // ✅ 5. GO TO DASHBOARD (NOT PROFILE)
      nav("/dashboard");
    } catch (error) {
      setErr(error instanceof Error ? error.message : "Signup failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box sx={{ minHeight: "100vh", display: "grid", placeItems: "center" }}>
      <Paper sx={{ p: 3, width: 400 }} component="form" onSubmit={onSubmit}>
        <Stack spacing={2}>
          <Typography variant="h5">Sign up</Typography>

          {err && <Alert severity="error">{err}</Alert>}

          <TextField
            label="Full name"
            value={name}
            onChange={(e) => setName(e.target.value)}
            required
          />

          <TextField
            label="Email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />

          <TextField
            label="Password"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />

          <TextField
            label="Confirm password"
            type="password"
            value={confirm}
            onChange={(e) => setConfirm(e.target.value)}
            required
          />

          <Button type="submit" variant="contained" disabled={loading}>
            {loading ? "Creating..." : "Sign up"}
          </Button>
        </Stack>
      </Paper>
    </Box>
  );
}
