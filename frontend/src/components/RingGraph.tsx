import { Paper, Typography } from "@mui/material";
import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import type { FraudRingCluster } from "../api/client";

type Props = { rings: FraudRingCluster[] };

export function RingGraph({ rings }: Props) {
  const data = rings.slice(0, 8).map((r) => ({
    name: r.grid_key.slice(0, 10),
    users: r.user_ids.length,
    claims: r.claim_count,
  }));

  if (!data.length) {
    return (
      <Paper sx={{ p: 3 }}>
        <Typography color="text.secondary">No coordinated clusters detected.</Typography>
      </Paper>
    );
  }

  return (
    <Paper sx={{ p: 2, height: 320 }}>
      <Typography variant="subtitle2" color="text.secondary" gutterBottom>
        Cluster size (fraud rings)
      </Typography>
      <ResponsiveContainer width="100%" height="85%">
        <BarChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="#ffffff22" />
          <XAxis dataKey="name" tick={{ fill: "#aaa", fontSize: 11 }} />
          <YAxis allowDecimals={false} tick={{ fill: "#aaa", fontSize: 12 }} />
          <Tooltip
            contentStyle={{ background: "#111827", border: "1px solid #333" }}
            formatter={(v: number, key: string) => [v, key === "users" ? "Users" : "Claims"]}
          />
          <Bar dataKey="users" stackId="a" fill="#ef5350" radius={[4, 4, 0, 0]} />
          <Bar dataKey="claims" stackId="a" fill="#ffb74d" radius={[4, 4, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </Paper>
  );
}
