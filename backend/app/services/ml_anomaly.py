"""
Isolation Forest anomaly detection on fraud feature vectors.
Trained on synthetic normals + historical feature rows; scores single samples safely.
"""
from __future__ import annotations

import logging
import threading
from pathlib import Path
from typing import List, Tuple

import numpy as np
import joblib
from sklearn.ensemble import IsolationForest

logger = logging.getLogger(__name__)

_lock = threading.Lock()
_model: IsolationForest | None = None


def _synthetic_training_matrix() -> np.ndarray:
    """Labeled-ish structure: mostly normal low-risk rows, some outliers."""
    rng = np.random.default_rng(42)
    normal = np.column_stack(
        [
            rng.integers(0, 4, size=120),
            rng.uniform(0, 0.2, size=120),
            rng.uniform(0, 0.2, size=120),
        ]
    )
    outliers = np.column_stack(
        [
            rng.integers(8, 25, size=25),
            rng.uniform(0.8, 1.0, size=25),
            rng.uniform(0.8, 1.0, size=25),
        ]
    )
    return np.vstack([normal, outliers])


def _ensure_model() -> IsolationForest:
    global _model
    with _lock:
        if _model is None:
            # Prefer a trained artifact if available; fall back to synthetic defaults.
            artifact = (
                Path(__file__).resolve().parents[2]
                / "ml"
                / "artifacts"
                / "fraud_anomaly_isolation_forest.joblib"
            )
            if artifact.exists():
                try:
                    loaded = joblib.load(artifact)
                    if isinstance(loaded, IsolationForest):
                        _model = loaded
                    else:
                        logger.warning("ML artifact is not an IsolationForest: %s", type(loaded))
                except Exception as exc:
                    logger.warning("Failed to load ML artifact (%s): %s", artifact, exc)

            if _model is None:
                X = _synthetic_training_matrix()
                _model = IsolationForest(
                    n_estimators=200,
                    contamination=0.12,
                    random_state=42,
                )
                _model.fit(X)
        return _model


def score_features(claims_count: float, gps_jump: float, weather_mismatch: float) -> Tuple[float, float]:
    """
    Returns (ml_anomaly_score, fraud_probability).
    Higher anomaly_score => more normal per sklearn convention for decision_function;
    we invert for intuitive "risk" display.
    """
    model = _ensure_model()
    x = np.array([[claims_count, gps_jump, weather_mismatch]], dtype=float)
    try:
        raw = float(model.decision_function(x)[0])
        pred = int(model.predict(x)[0])
    except Exception as e:
        logger.warning("IsolationForest scoring failed: %s", e)
        return 0.0, 0.5

    # Map decision_function to [0,1] fraud probability (heuristic blend)
    # Typical IF scores are negative for anomalies; lower => more fraudulent
    risk = 1.0 / (1.0 + np.exp(raw * 3.0))
    if pred == -1:
        risk = min(1.0, risk + 0.25)
    anomaly_display = raw
    return float(anomaly_display), float(risk)
