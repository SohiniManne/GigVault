import { Box, CircularProgress, CssBaseline, ThemeProvider } from "@mui/material";
import type { ReactNode } from "react";
import { useEffect, useState } from "react";
import { Navigate, Route, Routes } from "react-router-dom";

import { Layout } from "./components/Layout";
import { gigVaultTheme } from "./theme";

import { Dashboard } from "./pages/Dashboard";
import { Claims } from "./pages/Claims";
import { FraudInsights } from "./pages/FraudInsights";
import { Login } from "./pages/Login";
import { Premium } from "./pages/Premium";
import Profile from "./pages/Profile";
import Signup from "./pages/Signup";

import { useAuthState } from "./hooks/useAuthState";


// 🔄 Full page loader with message
function FullPageLoader() {
  return (
    <Box sx={{ minHeight: "100vh", display: "grid", placeItems: "center" }}>
      <div style={{ textAlign: "center" }}>
        <CircularProgress />
        <p style={{ marginTop: 12 }}>🚀 Starting GigVault engine...</p>
      </div>
    </Box>
  );
}


// 🔓 Public-only routes (login/signup)
function PublicOnly({ children }: { children: ReactNode }) {
  const { user, loading } = useAuthState();

  if (loading) return <FullPageLoader />;
  if (user) return <Navigate to="/dashboard" replace />;

  return <>{children}</>;
}


// 🔒 Protected routes
function ProtectedLayout() {
  const { user, loading } = useAuthState();

  if (loading) return <FullPageLoader />;
  if (!user) return <Navigate to="/login" replace />;

  return <Layout />;
}


export default function App() {
  const [backendReady, setBackendReady] = useState(false);

  useEffect(() => {
    const wakeBackend = async () => {
      try {
        await fetch("https://gigvault-backend.onrender.com/health");
        console.log("✅ Backend awake");
        setBackendReady(true);
      } catch (err) {
        console.log("⏳ Waking backend...");
        // fallback after delay
        setTimeout(() => setBackendReady(true), 5000);
      }
    };

    wakeBackend();
  }, []);

  // ⏳ Show loader until backend wakes up
  if (!backendReady) {
    return <FullPageLoader />;
  }

  return (
    <ThemeProvider theme={gigVaultTheme}>
      <CssBaseline />
      <Routes>
        <Route path="/" element={<Navigate to="/login" replace />} />

        <Route
          path="/login"
          element={
            <PublicOnly>
              <Login />
            </PublicOnly>
          }
        />

        <Route
          path="/signup"
          element={
            <PublicOnly>
              <Signup />
            </PublicOnly>
          }
        />

        <Route element={<ProtectedLayout />}>
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/claims" element={<Claims />} />
          <Route path="/profile" element={<Profile />} />
          <Route path="/premium" element={<Premium />} />
          <Route path="/fraud" element={<FraudInsights />} />
        </Route>

        <Route path="*" element={<Navigate to="/login" replace />} />
      </Routes>
    </ThemeProvider>
  );
}
