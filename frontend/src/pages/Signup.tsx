import { Alert, Box, Button, Paper, Stack, TextField, Typography } from "@mui/material";
import { createUserWithEmailAndPassword, updateProfile } from "firebase/auth";
import { type FormEvent, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { getFirebaseAuth } from "../firebase";
import { useUserId } from "../hooks/useUserId";

export function Signup() {
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
      setErr("Firebase Auth is not configured. Check `frontend/.env` and restart Vite.");
      return;
    }
    setLoading(true);
    try {
      const credential = await createUserWithEmailAndPassword(auth, email.trim(), password);
      if (name.trim()) {
        await updateProfile(credential.user, { displayName: name.trim() });
      }
      setUserId(credential.user.uid);
      nav("/profile");
    } catch (error) {
      setErr(error instanceof Error ? error.message : "Signup failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box
      sx={{
        minHeight: "100vh",
        display: "grid",
        placeItems: "center",
        px: 2,
        py: 4,
      }}
    >
      <Paper sx={{ p: 3, width: "100%", maxWidth: 460 }} component="form" onSubmit={onSubmit}>
        <Stack spacing={2}>
          <Typography variant="h5" fontWeight={700}>
            Sign up
          </Typography>
          {err && <Alert severity="error">{err}</Alert>}
          <TextField
            label="Full name"
            required
            value={name}
            onChange={(e) => setName(e.target.value)}
          />
          <TextField
            label="Email"
            type="email"
            required
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />
          <TextField
            label="Password"
            type="password"
            required
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
          <TextField
            label="Confirm password"
            type="password"
            required
            value={confirm}
            onChange={(e) => setConfirm(e.target.value)}
          />
          <Button type="submit" variant="contained" disabled={loading}>
            {loading ? "Creating account..." : "Sign up"}
          </Button>
          <Typography variant="body2">
            Already have an account? <Link to="/login">Login</Link>
          </Typography>
        </Stack>
      </Paper>
    </Box>
  );
}
