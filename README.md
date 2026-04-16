# GigVault

GigVault is an AI-powered parametric insurance platform for gig workers.  
It combines disruption detection, fraud scoring, trust-based premium logic, and worker profile intelligence.

## Stack

- `backend`: FastAPI + scikit-learn + Firebase Admin (optional)
- `frontend`: React + Vite + Material UI + Firebase Auth
- `backend/ml`: data training scripts and model artifacts

## Key Features

- Disruption-driven claims (weather/social signal simulation)
- Hybrid fraud scoring (rules + Isolation Forest anomaly score)
- Worker trust score and premium recalculation
- Worker online/offline status included in claim context
- Auto offline logic: if user location does not change for 5 minutes, status flips to offline
- Profile management with company name + work status
- Dynamic social verification banner based on backend model readiness

## Project Structure

```text
GIGVAULT/
  backend/
    app/
    data/
    ml/
  frontend/
  README.md
```

## Local Setup

### 1) Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload --port 8000
```

Backend health check:

```bash
curl http://127.0.0.1:8000/health
```

### 2) Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at `http://localhost:5173` and proxies `/api` requests to backend (`127.0.0.1:8000` in dev).

## ML Training (Social Claims Data)

Training data is read from `backend/data/*.csv`.

Run:

```bash
cd backend
.\.venv\Scripts\python.exe ml/train_social_claims.py
```

Outputs:

- `backend/ml/artifacts/fraud_anomaly_isolation_forest.joblib`
- `backend/ml/artifacts/training_report.json`
- `backend/ml/artifacts/feature_preview.csv`

The runtime fraud service auto-loads this model artifact if present.

## Main API Endpoints

- `GET /health`
- `POST /auto-claim`
- `POST /fraud-score`
- `POST /simulate-disruption`
- `GET /disruption/latest`
- `GET /verification-status`
- `GET /user-profile/{user_id}`
- `PUT /user-profile`
- `POST /premium`
- `GET /fraud-rings`

## Environment Variables

### Backend (`backend/.env`)

- `OPENWEATHER_API_KEY`
- `CORS_ORIGINS`
- `FIREBASE_CREDENTIALS_PATH` or `FIREBASE_CREDENTIALS_JSON`
- `PORT`
- Razorpay keys if payments are enabled

### Frontend (`frontend/.env`)

- `VITE_API_URL` (optional; defaults to `/api` in dev)
- `VITE_FIREBASE_*` variables for web auth/firestore sync

## Notes

- If frontend shows proxy `ECONNREFUSED 127.0.0.1:8000`, backend is not running.
- Geolocation failures are handled gracefully with city fallback in claims/profile flows.
