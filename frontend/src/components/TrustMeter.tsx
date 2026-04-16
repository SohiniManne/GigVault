import { Box, LinearProgress, Typography } from "@mui/material";

type Props = { value: number; label?: string };

export function TrustMeter({ value, label = "Trust score" }: Props) {
  const clamped = Math.max(0, Math.min(100, value));
  const color =
    clamped >= 75 ? "success.main" : clamped >= 50 ? "warning.main" : "error.main";

  return (
    <Box>
      <Typography variant="body2" color="text.secondary" gutterBottom>
        {label}
      </Typography>
      <Box sx={{ display: "flex", alignItems: "center", gap: 2 }}>
        <Box sx={{ flex: 1 }}>
          <LinearProgress
            variant="determinate"
            value={clamped}
            sx={{
              height: 10,
              borderRadius: 5,
              bgcolor: "rgba(255,255,255,0.08)",
              "& .MuiLinearProgress-bar": {
                borderRadius: 5,
                bgcolor: color,
              },
            }}
          />
        </Box>
        <Typography variant="h6" sx={{ minWidth: 48, fontVariantNumeric: "tabular-nums" }}>
          {clamped.toFixed(0)}
        </Typography>
      </Box>
    </Box>
  );
}
