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

type Props = {
  ruleScore: number;
  mlProbability: number;
  combined: number;
};

export function FraudScoreChart({ ruleScore, mlProbability, combined }: Props) {
  const data = [
    { name: "Rule-based", score: Math.min(100, ruleScore * 0.65) },
    { name: "ML risk ×100", score: Math.min(100, mlProbability * 100) },
    { name: "Combined", score: combined },
  ];

  return (
    <Paper sx={{ p: 2, height: 280 }}>
      <Typography variant="subtitle2" color="text.secondary" gutterBottom>
        Fraud signal blend
      </Typography>
      <ResponsiveContainer width="100%" height="85%">
        <BarChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="#ffffff22" />
          <XAxis dataKey="name" tick={{ fill: "#aaa", fontSize: 12 }} />
          <YAxis domain={[0, 100]} tick={{ fill: "#aaa", fontSize: 12 }} />
          <Tooltip
            contentStyle={{ background: "#111827", border: "1px solid #333" }}
            labelStyle={{ color: "#e5e7eb" }}
          />
          <Bar dataKey="score" fill="#5c6bc0" radius={[6, 6, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </Paper>
  );
}
