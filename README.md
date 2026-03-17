GigVault 🔒
AI-Powered Parametric Income Insurance for Q-Commerce Delivery Partners
"Your income, protected in 10 minutes or less."

🚀 TL;DR
GigVault is an AI-powered parametric insurance platform that protects the income of delivery riders by automatically spotting problems in the real world (like bad weather, high AQI, or power outages) and making instant payments. The prices change every week.
🧑‍💼 The Problem
India's Q-Commerce delivery partners (Zepto, Blinkit, and Swish) work in a high-pressure, hyper-local way with no income protection.
When things go wrong:
• Heavy rain means that orders drop right away
• 🌫️ AQI goes up, so platforms cut back on delivery work
• 🚧 Curfews and roadblocks keep riders from getting in
• ⚙️ App outages mean no earnings during peak hours. 
👉Result: Riders lose 20–30% of their weekly income with no way to get it back 
👤 Persona: The Q-Commerce Rider
Name: Ravi
Age: 26
City: Bangalore
Platforms: Zepto + Blinkit
Income: ₹800–₹1,200/day
Pain Point:
One bad disruption = ₹900 lost. No compensation. No safety net.
⚠️ Real-World Disruption Scenarios
Scenario	Trigger	Impact
Heavy Rain	Rainfall > 15mm/hr	3–4 hrs no orders
AQI Emergency	AQI > 400	60% drop in orders
Local Bandh	Zone closure	Full-day income loss
Platform Outage	> 45 mins downtime	Zero earnings
Extreme Heat	Temp > 44°C	Forced work pause
💡 Why Parametric Insurance?
Traditional Insurance	GigVault
Manual claims	Automatic triggers
Slow payouts	Instant payouts
Requires proof	No paperwork
Complex process	Zero-touch experience

🛡️ What GigVault Does
🔄 End-to-End Workflow
1.	Rider purchases weekly coverage
2.	System monitors real-time disruption data
3.	A trigger threshold is breached
4.	Rider activity & GPS validated
5.	Claim auto-approved
6.	Instant payout via UPI

💰 Weekly Premium Model
•	Coverage: Monday → Sunday
•	Premium deducted weekly
•	Rider selects coverage tier
📊 Coverage Tiers
Tier	Weekly Premium	Max Payout
Basic	₹29	₹500
Standard	₹59	₹1200
Max	₹99	₹2500

🤖 Dynamic Pricing (AI-Powered)
Premium adjusts based on:
•	Zone risk score
•	Weather forecasts
•	Rider activity
•	Claim history
📌 Example
Ravi (Bangalore, high-risk zone, monsoon week)
→ Base premium: ₹59
→ Risk adjustment: +₹20
→ Final premium: ₹79/week

⚡ Parametric Triggers
Trigger	Threshold	Payout	Insight
Rainfall	>15mm/hr	Hourly payout	Most common disruption
AQI	>400	₹200	Safety-based slowdown
Heat	>44°C	₹150	Worker protection
Curfew	Official notice	Full payout	Total shutdown
Outage	>45 mins	₹100/30 min	Hidden income loss
📌 Example Claim Flow:
Ravi is active during heavy rain (16mm/hr for 45 mins)
→ Orders drop
→ System detects trigger
→ Validates activity + GPS
→ ₹150 payout credited instantly

🤖 AI/ML Integration
GigVault uses AI for real-time risk prediction, pricing, and fraud detection.
1. Dynamic Pricing Model
•	Model: XGBoost
•	Inputs: Zone, weather, activity, history
•	Output: Weekly premium
👉 Retrained weekly using latest data

2. Fraud Detection Engine
•	GPS validation (location check)
•	Activity validation (platform online status)
•	Duplicate claim prevention
•	Anomaly detection (>80% claim frequency)
📌 Example:
Rider offline during rain → ❌ Claim rejected
GPS mismatch → 🚨 Flagged

3. Risk Profiling
•	Zone Risk Score (ZRS) at onboarding
•	Updated weekly
•	Predictive alerts for disruptions

🧩 System Architecture
•	Frontend: React PWA
•	Backend: FastAPI
•	Database: PostgreSQL
•	ML Engine: Python + XGBoost
•	Trigger Engine: API polling + scheduler
•	APIs: Weather, AQI
•	Payments: Razorpay (test mode)

📊 Analytics Dashboard
👷 For Riders:
•	Earnings protected
•	Active coverage
•	Claim history
🏢 For Insurers:
•	Loss ratios
•	Claims per zone
•	Fraud alerts
•	Risk heatmaps

🚀 Tech Stack
Layer	Tech
Frontend	React.js
Backend	FastAPI
DB	PostgreSQL
ML	scikit-learn / XGBoost
APIs	OpenWeather, AQICN
Payments	Razorpay
Hosting	Vercel + Render

🗓️ Development Plan
Phase 1 (Seed)
•	Idea, pricing, triggers
•	Basic UI + APIs
Phase 2 (Scale)
•	Automation
•	Claims engine
•	ML model
Phase 3 (Soar)
•	Fraud detection
•	Dashboards
•	Full demo

📦 Repository Structure
gigvault/
├── frontend/
├── backend/
├── data/
├── docs/
└── README.md

▶️ How to Run
# Frontend
cd frontend
npm install
npm run dev

# Backend
cd backend
pip install -r requirements.txt
uvicorn main:app --reload

🎥 Demo
•	Phase 1: Strategy Video (link)
•	Phase 2: Prototype Demo
•	Phase 3: Full Simulation

💼 Business Model
•	Revenue: Weekly premiums
•	Cost: Payouts
•	Profit: Risk-adjusted margin
•	Scale: Partnerships with platforms

🌟 Key Innovations
•	Weekly parametric insurance (rare)
•	Hyper-local pricing
•	Zero-touch claims
•	Built for gig economy

📌 Constraints Compliance
•	✅ Income loss only
•	✅ Weekly pricing
•	✅ External triggers
•	✅ Single persona

👥 Team
Tech Titans
Sohini, Umesh, Manideep, Koushik
SRMIST

Built for Guidewire DEVTrails 2026 🚀

