import MenuIcon from "@mui/icons-material/Menu";
import ShieldMoonIcon from "@mui/icons-material/ShieldMoon";
import {
  AppBar,
  Box,
  Button,
  Container,
  Divider,
  Drawer,
  IconButton,
  List,
  ListItemButton,
  ListItemText,
  Toolbar,
  Typography,
  useMediaQuery,
} from "@mui/material";
import { useTheme } from "@mui/material/styles";
import { signOut } from "firebase/auth";
import { useEffect, useRef, useState } from "react";
import { Link, Outlet, useLocation, useNavigate } from "react-router-dom";
import { putUserProfile } from "../api/client";
import { getFirebaseAuth } from "../firebase";
import { useUserId } from "../hooks/useUserId";

const nav = [
  { to: "/dashboard", label: "Dashboard" },
  { to: "/claims", label: "Claims" },
  { to: "/premium", label: "Premium Plans" },
  { to: "/fraud", label: "Fraud Insights" },
];

export function Layout() {
  const theme = useTheme();
  const isSm = useMediaQuery(theme.breakpoints.down("md"));
  const [open, setOpen] = useState(false);
  const [userId] = useUserId();
  const loc = useLocation();
  const navTo = useNavigate();
  const lastCoordsRef = useRef<{ lat: number; lon: number } | null>(null);
  const lastMovementAtRef = useRef<number | null>(null);
  const lastSyncedOnlineRef = useRef<boolean | null>(null);
  const syncingRef = useRef(false);

  useEffect(() => {
    if (!userId || !navigator.geolocation) return;

    const minMoveMeters = 30;
    const inactivityMs = 5 * 60 * 1000;

    const distanceMeters = (a: { lat: number; lon: number }, b: { lat: number; lon: number }) => {
      const dLat = (a.lat - b.lat) * 111_320;
      const avgLat = ((a.lat + b.lat) / 2) * (Math.PI / 180);
      const dLon = (a.lon - b.lon) * (111_320 * Math.cos(avgLat));
      return Math.sqrt(dLat * dLat + dLon * dLon);
    };

    const syncStatus = (coords: { lat: number; lon: number }) => {
      if (syncingRef.current) return;
      const now = Date.now();
      const prev = lastCoordsRef.current;
      const moved = prev ? distanceMeters(coords, prev) >= minMoveMeters : true;

      if (moved) {
        lastMovementAtRef.current = now;
        lastCoordsRef.current = coords;
      } else if (!lastMovementAtRef.current) {
        lastMovementAtRef.current = now;
        lastCoordsRef.current = coords;
      }

      const lastMovedAt = lastMovementAtRef.current ?? now;
      const nextOnline = now - lastMovedAt < inactivityMs;
      const shouldSync = lastSyncedOnlineRef.current !== nextOnline || moved;
      if (!shouldSync) return;

      syncingRef.current = true;
      void putUserProfile({
        user_id: userId,
        is_online: nextOnline,
        location: { lat: coords.lat, lon: coords.lon },
      })
        .then(() => {
          lastSyncedOnlineRef.current = nextOnline;
        })
        .catch(() => undefined)
        .finally(() => {
          syncingRef.current = false;
        });
    };

    const tick = () => {
      navigator.geolocation.getCurrentPosition(
        (pos) => {
          syncStatus({ lat: pos.coords.latitude, lon: pos.coords.longitude });
        },
        () => undefined,
        { enableHighAccuracy: false, timeout: 10000, maximumAge: 60000 },
      );
    };

    tick();
    const timer = window.setInterval(tick, 60_000);
    return () => {
      window.clearInterval(timer);
    };
  }, [userId]);

  const drawer = (
    <Box sx={{ width: 260, pt: 2 }} role="presentation" onClick={() => setOpen(false)}>
      <Box sx={{ px: 2, pb: 2, display: "flex", alignItems: "center", gap: 1 }}>
        <ShieldMoonIcon color="secondary" />
        <Typography variant="h6" fontWeight={700}>
          GigVault
        </Typography>
      </Box>
      <Divider />
      <List>
        {nav.map((item) => (
          <ListItemButton
            key={item.to}
            component={Link}
            to={item.to}
            selected={loc.pathname === item.to}
          >
            <ListItemText primary={item.label} />
          </ListItemButton>
        ))}
      </List>
    </Box>
  );

  return (
    <Box sx={{ display: "flex", flexDirection: "column", minHeight: "100vh" }}>
      <AppBar position="sticky" elevation={0} sx={{ borderBottom: "1px solid #ffffff12" }}>
        <Toolbar>
          {isSm && (
            <IconButton color="inherit" edge="start" onClick={() => setOpen(true)} sx={{ mr: 1 }}>
              <MenuIcon />
            </IconButton>
          )}
          <ShieldMoonIcon color="secondary" sx={{ mr: 1, display: { xs: "none", md: "block" } }} />
          <Typography variant="h6" sx={{ flexGrow: 1, fontWeight: 700 }}>
            GigVault
          </Typography>
          {!isSm && (
            <Box sx={{ display: "flex", gap: 1 }}>
              {nav.map((item) => (
                <Typography
                  key={item.to}
                  component={Link}
                  to={item.to}
                  sx={{
                    mx: 1,
                    color: loc.pathname === item.to ? "secondary.main" : "inherit",
                    textDecoration: "none",
                    fontWeight: 600,
                  }}
                >
                  {item.label}
                </Typography>
              ))}
            </Box>
          )}
          <Button
            color="inherit"
            variant="outlined"
            component={Link}
            to="/profile"
            sx={{ ml: 2, borderColor: "#ffffff40" }}
          >
            Profile
          </Button>
          <Button
            color="inherit"
            variant="outlined"
            sx={{ ml: 1, borderColor: "#ffffff40" }}
            onClick={async () => {
              const auth = getFirebaseAuth();
              if (auth) await signOut(auth);
              localStorage.removeItem("gigvault_user_id");
              navTo("/login");
            }}
          >
            Logout
          </Button>
        </Toolbar>
      </AppBar>
      <Drawer anchor="left" open={open} onClose={() => setOpen(false)}>
        {drawer}
      </Drawer>
      <Container maxWidth="lg" sx={{ py: 3, flex: 1 }}>
        <Outlet />
      </Container>
    </Box>
  );
}
