import { useState } from "react";

export default function App() {
  const [result, setResult] = useState("");

  const simulateRain = async () => {
    const res = await fetch("http://127.0.0.1:8000/simulate-trigger", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ event: "rain" })
    });
    const data = await res.json();
    setResult(data.message);
  };

  const checkFraud = async () => {
    const res = await fetch("http://127.0.0.1:8000/check-fraud", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ gps: "Bangalore", ip: "Delhi" })
    });
    const data = await res.json();
    setResult(data.message);
  };

  const getPremium = async () => {
    const res = await fetch("http://127.0.0.1:8000/get-premium", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ city: "Bangalore", risk: "high" })
    });
    const data = await res.json();
    setResult(data.message);
  };

  return (
    <div style={{
      minHeight: "100vh",
      background: "#0f172a",
      color: "white",
      display: "flex",
      flexDirection: "column",
      alignItems: "center",
      justifyContent: "center",
      fontFamily: "Arial"
    }}>
      <h1 style={{ fontSize: "2.5rem", marginBottom: "20px" }}>
        🚀 GigVault Demo
      </h1>

      <div style={{ display: "flex", gap: "15px", marginBottom: "30px" }}>
        <button onClick={simulateRain} style={btn}>
          🌧️ Simulate Rain
        </button>
        <button onClick={checkFraud} style={btn}>
          🛡️ Check Fraud
        </button>
        <button onClick={getPremium} style={btn}>
          💰 Get Premium
        </button>
      </div>

      <div style={{
        background: "#1e293b",
        padding: "20px",
        borderRadius: "10px",
        minWidth: "300px",
        textAlign: "center"
      }}>
        <h2>{result || "Run a simulation to see results..."}</h2>
      </div>
    </div>
  );
}

const btn = {
  padding: "12px 20px",
  borderRadius: "8px",
  border: "none",
  cursor: "pointer",
  fontWeight: "bold"
};