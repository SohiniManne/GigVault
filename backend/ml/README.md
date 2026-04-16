# Social Claims ML Training

This module trains an anomaly model from all CSV files in `backend/data/`.

## What it trains

- Model: `IsolationForest` (hyperparameter search over multiple candidates)
- Output artifact: `backend/ml/artifacts/fraud_anomaly_isolation_forest.joblib`
- Output report: `backend/ml/artifacts/training_report.json`

The training script engineers 3 stable numeric features per row so the saved model remains compatible with the runtime scoring function used in `app/services/ml_anomaly.py`.

## Run training

From `backend/`:

```powershell
python ml/train_social_claims.py
```

If you use the local venv:

```powershell
.\.venv\Scripts\python.exe ml/train_social_claims.py
```
