import { Alert, Box, Button, Paper, Stack, TextField, Typography } from "@mui/material";
import { signInWithEmailAndPassword } from "firebase/auth";
import { type FormEvent, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { getFirebaseAuth } from "../firebase";
import { useUserId } from "../hooks/useUserId";

export function Login() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [err, setErr] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const nav = useNavigate();
  const [, setUserId] = useUserId();

  const onSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setErr(null);
    const auth = getFirebaseAuth();
    if (!auth) {
      setErr("Firebase Auth is not configured. Check `frontend/.env` and restart Vite.");
      return;
    }
    setLoading(true);
    try {
      const credential = await signInWithEmailAndPassword(auth, email.trim(), password);
      setUserId(credential.user.uid);
      nav("/dashboard");
    } catch (error) {
      setErr(error instanceof Error ? error.message : "Login failed");
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
            Login
          </Typography>
          {err && <Alert severity="error">{err}</Alert>}
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
          <Button type="submit" variant="contained" disabled={loading}>
            {loading ? "Signing in..." : "Login"}
          </Button>
          <Typography variant="body2">
            New user? <Link to="/signup">Create an account</Link>
          </Typography>
        </Stack>
      </Paper>
    </Box>
  );
}
