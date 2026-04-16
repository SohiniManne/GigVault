import GppBadIcon from "@mui/icons-material/GppBad";
import {
  Alert,
  Chip,
  Paper,
  Stack,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Typography,
} from "@mui/material";
import { useEffect, useState } from "react";
import type { FraudRingsResponse } from "../api/client";
import { getFraudRings } from "../api/client";
import { RingGraph } from "../components/RingGraph";

export function FraudInsights() {
  const [data, setData] = useState<FraudRingsResponse | null>(null);
  const [err, setErr] = useState<string | null>(null);

  useEffect(() => {
    void getFraudRings()
      .then(setData)
      .catch((e) => setErr(e instanceof Error ? e.message : "Failed to load intelligence"));
  }, []);

  return (
    <Stack spacing={3}>
      <Stack direction="row" spacing={1} alignItems="center">
        <GppBadIcon color="error" />
        <Typography variant="h4" fontWeight={700}>
          Fraud intelligence
        </Typography>
      </Stack>
      <Typography color="text.secondary" maxWidth={800}>
        Surfaces coordinated claim activity: identical location buckets, synchronized time windows,
        and shared claim patterns — the same signals the API uses for cluster penalties.
      </Typography>

      {err && <Alert severity="error">{err}</Alert>}

      {data && <RingGraph rings={data.rings} />}

      <Paper sx={{ p: 2 }}>
        <Typography variant="h6" gutterBottom>
          Live alerts
        </Typography>
        <Stack spacing={1}>
          {(data?.alerts ?? []).length === 0 && (
            <Typography color="text.secondary">No active alerts.</Typography>
          )}
          {(data?.alerts ?? []).map((a, i) => (
            <Alert
              key={i}
              severity={a.severity === "high" ? "error" : "warning"}
              icon={<GppBadIcon fontSize="inherit" />}
            >
              <Typography fontWeight={600}>{a.message}</Typography>
              <Stack direction="row" gap={0.5} flexWrap="wrap" sx={{ mt: 1 }}>
                {a.user_ids.map((u) => (
                  <Chip key={u} size="small" label={u} variant="outlined" />
                ))}
              </Stack>
            </Alert>
          ))}
        </Stack>
      </Paper>

      <TableContainer component={Paper}>
        <Table size="small">
          <TableHead>
            <TableRow>
              <TableCell>Grid</TableCell>
              <TableCell>Time bucket</TableCell>
              <TableCell align="right">Users</TableCell>
              <TableCell align="right">Claims</TableCell>
              <TableCell>Risk</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {(data?.rings ?? []).map((r) => (
              <TableRow key={`${r.grid_key}-${r.time_bucket}`}>
                <TableCell>{r.grid_key}</TableCell>
                <TableCell>{r.time_bucket}</TableCell>
                <TableCell align="right">{r.user_ids.length}</TableCell>
                <TableCell align="right">{r.claim_count}</TableCell>
                <TableCell>
                  <Chip
                    size="small"
                    label={r.risk_level}
                    color={r.risk_level === "high" ? "error" : "warning"}
                  />
                </TableCell>
              </TableRow>
            ))}
            {(data?.rings ?? []).length === 0 && (
              <TableRow>
                <TableCell colSpan={5}>
                  <Typography color="text.secondary">No rings yet — trigger a few claims to populate.</Typography>
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </TableContainer>
    </Stack>
  );
}
