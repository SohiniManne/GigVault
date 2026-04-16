import { createTheme } from "@mui/material/styles";

export const gigVaultTheme = createTheme({
  palette: {
    mode: "dark",
    primary: { main: "#5c6bc0" },
    secondary: { main: "#26a69a" },
    background: {
      default: "#070b12",
      paper: "#0f141f",
    },
    success: { main: "#66bb6a" },
    warning: { main: "#ffb74d" },
    error: { main: "#ef5350" },
  },
  shape: { borderRadius: 12 },
  typography: {
    fontFamily: '"DM Sans", system-ui, sans-serif',
    h4: { fontWeight: 700 },
    h6: { fontWeight: 600 },
  },
  components: {
    MuiPaper: {
      styleOverrides: {
        root: {
          backgroundImage: "none",
          border: "1px solid rgba(255,255,255,0.06)",
        },
      },
    },
    MuiButton: {
      styleOverrides: {
        root: { textTransform: "none", fontWeight: 600 },
      },
    },
  },
});
