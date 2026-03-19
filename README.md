# GigVault 🔒

### AI-Powered Parametric Income Insurance for Q-Commerce Delivery Partners

**"Your income, protected in 10 minutes or less."**

---

## 🚀 TL;DR

GigVault is an AI-powered parametric insurance platform that protects the income of delivery riders by automatically detecting real-world disruptions (weather, AQI, outages) and triggering instant payouts — all priced dynamically on a weekly basis.

---

## 🧑‍💼 The Problem

India's Q-Commerce delivery partners (Zepto, Blinkit, Swish) operate in a high-pressure, hyper-local model with **zero income protection**.

Riders depend on daily earnings with no savings buffer, making even short disruptions financially critical.

When disruptions occur:

* 🌧️ Heavy rain → orders drop instantly
* 🌫️ AQI spikes → platforms reduce delivery activity
* 🚧 Curfews / roadblocks → riders locked out
* ⚙️ App outages → zero earnings during peak hours

👉 **Result:** Riders lose **20–30% of weekly income** with no fallback.

---

## 👤 Persona: The Q-Commerce Rider

* **Name:** Ravi
* **Age:** 26
* **City:** Bangalore
* **Platforms:** Zepto + Blinkit
* **Income:** ₹800–₹1,200/day

**Pain Point:**
One bad disruption = ₹900 lost. No compensation. No safety net.

---

## ⚠️ Real-World Disruption Scenarios

| Scenario        | Trigger            | Impact               |
| --------------- | ------------------ | -------------------- |
| Heavy Rain      | Rainfall > 15mm/hr | 3–4 hrs no orders    |
| AQI Emergency   | AQI > 400          | 60% drop in orders   |
| Local Bandh     | Zone closure       | Full-day income loss |
| Platform Outage | > 45 mins downtime | Zero earnings        |
| Extreme Heat    | Temp > 44°C        | Forced work pause    |

---

## 💡 Why Parametric Insurance?

| Traditional Insurance | GigVault              |
| --------------------- | --------------------- |
| Manual claims         | Automatic triggers    |
| Slow payouts          | Instant payouts       |
| Requires proof        | No paperwork          |
| Complex process       | Zero-touch experience |

---

## 🛡️ What GigVault Does

### 🔄 End-to-End Workflow

1. Rider purchases weekly coverage
2. System monitors real-time disruption data
3. A trigger threshold is breached
4. Rider activity & GPS validated
5. Claim auto-approved
6. Instant payout via UPI

---

## 💰 Weekly Premium Model

* Coverage: Monday → Sunday
* Premium deducted weekly
* Rider selects coverage tier

### 📊 Coverage Tiers

| Tier     | Weekly Premium | Max Payout |
| -------- | -------------- | ---------- |
| Basic    | ₹29            | ₹500       |
| Standard | ₹59            | ₹1200      |
| Max      | ₹99            | ₹2500      |

---

## 🤖 Dynamic Pricing (AI-Powered)

Premium adjusts based on:

* Zone risk score
* Weather forecasts
* Rider activity
* Claim history

### 📌 Example

Ravi (Bangalore, high-risk zone, monsoon week)
→ Base premium: ₹59
→ Risk adjustment: +₹20
→ Final premium: **₹79/week**

---

## ⚡ Parametric Triggers

| Trigger  | Threshold       | Payout        | Insight                |
| -------- | --------------- | ------------- | ---------------------- |
| Rainfall | >15mm/hr        | Hourly payout | Most common disruption |
| AQI      | >400            | ₹200          | Safety-based slowdown  |
| Heat     | >44°C           | ₹150          | Worker protection      |
| Curfew   | Official notice | Full payout   | Total shutdown         |
| Outage   | >45 mins        | ₹100/30 min   | Hidden income loss     |

App outages are detected using platform uptime monitoring signals, such as API response failures, third-party status tracking services, or simulated downtime thresholds.

---

### 📌 Example Claim Flow

Ravi is active during heavy rain (16mm/hr for 45 mins)
→ Orders drop
→ System detects trigger
→ Validates activity + GPS
→ ₹150 payout credited instantly

---

## 🤖 AI/ML Integration

GigVault uses AI for real-time risk prediction, pricing, and fraud detection.

### 1. Dynamic Pricing Model

* Model: XGBoost
* Inputs: Zone, weather, activity, history
* Output: Weekly premium

👉 Retrained weekly using latest data



### 2. Fraud Detection Engine

* GPS validation (location check)
* Activity validation (platform online status)
* Duplicate claim prevention
* Anomaly detection (>80% claim frequency)

Fraud detection models are continuously evaluated against historical claim patterns to improve accuracy and reduce false positives.

📌 Example:
Rider offline during rain → ❌ Claim rejected
GPS mismatch → 🚨 Flagged



### 3. Risk Profiling

* Zone Risk Score (ZRS) at onboarding
* Updated weekly
* Predictive alerts for disruptions

The model continuously updates premiums based on rolling disruption data and rider behavior, enabling adaptive risk pricing over time.

The model is trained on historical weather patterns and simulated rider activity datasets, and is retrained weekly to adapt to changing risk conditions.

---
## 🚨 Adversarial Defense & Anti-Spoofing Strategy

GigVault is designed to withstand large-scale coordinated fraud attacks, such as mass GPS spoofing by delivery partners attempting to exploit parametric triggers.

### 🎯 Threat Scenario: Market Crash
A coordinated group of 500 riders spoof their GPS locations during a disruption (e.g., heavy rain) to trigger false payouts simultaneously, draining the system.

GigVault is designed to remain stable even under coordinated attack scenarios, preventing large-scale payout draining.

## 🛡️ Multi-Layer Defense Architecture

GigVault uses a defense-in-depth strategy combining behavioral, spatial, and temporal validation.



### 1. 📍 Multi-Signal Location Verification
- GPS + device motion patterns
- Location consistency over time
- Speed validation (reject impossible movement)



### 2. 🧠 Behavioral Pattern Analysis
- Typical working hours
- Order frequency
- Sudden abnormal activity detection



### 3. 🌐 Cluster & Network Detection
- Multiple riders from same coordinates
- Simultaneous claims
- Group anomaly detection



### 4. ⏱️ Temporal Validation
- Was rider active before trigger?
- Did activity drop during disruption?
- Did activity resume after?


### 5. 📊 Risk Scoring Engine
Each claim gets a fraud score:
- Low → instant payout  
- Medium → delayed  
- High → blocked  



### 6. ⚖️ Fairness Layer
- First-time anomalies not blocked  
- Partial payouts for uncertain cases  
- Manual review fallback  



### 📌 Example Detection
500 riders claim rain payout:
- Same location → flagged  
- No activity history → flagged  
- Unrealistic movement → flagged  

👉 Result: Fraud ring blocked

## 🧱 System Stability Under Attack
GigVault is designed to handle sudden spikes in claim requests during disruption events.

To ensure system stability under a Market Crash scenario:

- Claim processing is rate-limited and queued to prevent system overload  
- Risk scoring is applied before payout execution to filter high-risk claims early  
- Batch validation is used for simultaneous claims in the same zone  
- High-risk clusters are temporarily isolated to prevent cascading payouts  

This ensures the platform remains financially and operationally stable even under coordinated attacks.

## 📌 Example Fairness Logic:
A rider with 6 weeks of consistent activity and no prior fraud signals claims during a verified rain event.

Even if 200+ riders in the same zone are flagged as a cluster, this rider is:
- Auto-approved due to strong historical trust score  
- Not penalized by cluster-level suspicion  

This ensures genuine users are protected while fraud rings are isolated.

---

## 🧩 System Architecture

GigVault operates as a real-time event-driven system:

* **Frontend:** React PWA
* **Backend:** FastAPI
* **Database:** PostgreSQL
* **ML Engine:** Python + XGBoost
* **Trigger Engine:** API polling + scheduler
* **APIs:** Weather, AQI
* **Payments:** Razorpay (test mode)

The system operates as an event-driven pipeline where external API signals trigger validation and payout workflows in real-time.

---

## 📊 Analytics Dashboard

### 👷 For Riders:

* Earnings protected
* Active coverage
* Claim history

### 🏢 For Insurers:

* Loss ratios
* Claims per zone
* Fraud alerts
* Risk heatmaps
* Avg payout per rider/week

---

## 🚀 Tech Stack

| Layer    | Tech                   |
| -------- | ---------------------- |
| Frontend | React.js               |
| Backend  | FastAPI                |
| DB       | PostgreSQL             |
| ML       | scikit-learn / XGBoost |
| APIs     | OpenWeather, AQICN     |
| Payments | Razorpay               |
| Hosting  | Vercel + Render        |

---

## 🗓️ Development Plan

### Phase 1 (Seed)

* Idea, pricing, triggers
* Basic UI + APIs

### Phase 2 (Scale)

* Automation
* Claims engine
* ML model

### Phase 3 (Soar)

* Fraud detection
* Dashboards
* Full demo

---

## 📦 Repository Structure

```
gigvault/
├── frontend/
├── backend/
├── data/
├── docs/
└── README.md
```

---

## ▶️ How to Run

```bash
# Frontend
cd frontend
npm install
npm run dev

# Backend
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

---

## 🎥 Demo

* Phase 1: Strategy Video (https://www.youtube.com/watch?v=Ne7Pmxbulxg)
* Phase 2: Prototype Demo
* Phase 3: Full Simulation

---

## 💼 Business Model

- Revenue: Weekly premiums  
- Cost: Payouts  
- Target Loss Ratio: 60–65%  
- Profit: Risk-adjusted margin  
- Scale: Partnerships with platforms  

At scale, profitability is achieved through diversified risk pools across zones and rider segments.

---

## 🌟 Key Innovations

* Weekly parametric insurance (rare)
* Hyper-local pricing
* Zero-touch claims
* Built for gig economy

---

## 📌 Constraints Compliance

* ✅ Income loss only
* ✅ Weekly pricing
* ✅ External triggers
* ✅ Single persona

---

## 👥 Team

**Tech Titans**

Sohini, Umesh, Manideep, Koushik

SRMIST

---

### 🚀 Built for Guidewire DEVTrails 2026

**GigVault transforms income uncertainty into predictable protection — built for the speed of the gig economy.**
