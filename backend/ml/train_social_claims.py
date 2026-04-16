from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest


@dataclass(frozen=True)
class TrainConfig:
    random_state: int = 42
    target_anomaly_rate: float = 0.12


def _read_all_csvs(data_dir: Path) -> pd.DataFrame:
    csv_paths = sorted(data_dir.glob("*.csv"))
    if not csv_paths:
        raise FileNotFoundError(f"No CSV files found in {data_dir}")

    frames: list[pd.DataFrame] = []
    for csv_path in csv_paths:
        try:
            df = pd.read_csv(csv_path)
        except Exception:
            df = pd.read_csv(csv_path, engine="python", on_bad_lines="skip")
        if df.empty:
            continue
        df["__source_file"] = csv_path.name
        frames.append(df)

    if not frames:
        raise ValueError("CSV files were found, but all parsed into empty dataframes.")

    return pd.concat(frames, axis=0, ignore_index=True)


def _to_numeric_dataframe(raw_df: pd.DataFrame) -> pd.DataFrame:
    df = raw_df.copy()
    for col in df.columns:
        if col == "__source_file":
            continue
        df[col] = pd.to_numeric(df[col], errors="coerce")
    numeric_df = df.select_dtypes(include=[np.number]).copy()
    numeric_df = numeric_df.replace([np.inf, -np.inf], np.nan)
    return numeric_df


def _build_three_features(numeric_df: pd.DataFrame) -> pd.DataFrame:
    if numeric_df.empty:
        raise ValueError("No numeric columns found in source CSVs.")

    row_sum = numeric_df.sum(axis=1, skipna=True).fillna(0.0)
    row_mean = numeric_df.mean(axis=1, skipna=True).fillna(0.0)
    row_std = numeric_df.std(axis=1, skipna=True).fillna(0.0)
    row_max = numeric_df.max(axis=1, skipna=True).fillna(0.0)

    # Keep features compatible with the API's 3-input ML scoring shape.
    claims_count_proxy = np.log1p(np.clip(row_sum, a_min=0.0, a_max=None))
    gps_jump_proxy = np.clip(row_std / (np.abs(row_mean) + 1.0), 0.0, 5.0)
    weather_mismatch_proxy = np.clip(row_max / (np.abs(row_sum) + 1.0), 0.0, 1.0)

    return pd.DataFrame(
        {
            "claims_count_proxy": claims_count_proxy.astype(float),
            "gps_jump_proxy": gps_jump_proxy.astype(float),
            "weather_mismatch_proxy": weather_mismatch_proxy.astype(float),
        }
    )


def _iter_candidates() -> Iterable[dict]:
    for n_estimators in (200, 400, 600):
        for contamination in (0.08, 0.1, 0.12, 0.15):
            for max_samples in ("auto", 0.7, 0.9):
                yield {
                    "n_estimators": n_estimators,
                    "contamination": contamination,
                    "max_samples": max_samples,
                }


def _evaluate_unsupervised(model: IsolationForest, x_val: np.ndarray, target_anomaly_rate: float) -> dict:
    pred = model.predict(x_val)
    decision = model.decision_function(x_val)
    anomaly_mask = pred == -1
    anomaly_rate = float(np.mean(anomaly_mask))

    if anomaly_mask.any() and (~anomaly_mask).any():
        sep = float(np.mean(decision[~anomaly_mask]) - np.mean(decision[anomaly_mask]))
    else:
        sep = 0.0

    penalty = abs(anomaly_rate - target_anomaly_rate)
    final_score = sep - penalty
    return {
        "score": final_score,
        "anomaly_rate": anomaly_rate,
        "separation": sep,
        "penalty": penalty,
    }


def train_and_save(
    *,
    data_dir: Path,
    output_dir: Path,
    config: TrainConfig = TrainConfig(),
) -> dict:
    raw_df = _read_all_csvs(data_dir)
    numeric_df = _to_numeric_dataframe(raw_df)
    features_df = _build_three_features(numeric_df).dropna()
    if len(features_df) < 20:
        raise ValueError("Not enough usable rows to train. Need at least 20 rows.")

    x = features_df.to_numpy(dtype=float)
    split_idx = max(10, int(len(x) * 0.8))
    x_train, x_val = x[:split_idx], x[split_idx:]
    if len(x_val) == 0:
        x_train, x_val = x[:-1], x[-1:]

    best_payload: dict | None = None
    best_model: IsolationForest | None = None
    for params in _iter_candidates():
        model = IsolationForest(
            n_estimators=params["n_estimators"],
            contamination=params["contamination"],
            max_samples=params["max_samples"],
            random_state=config.random_state,
            n_jobs=-1,
        )
        model.fit(x_train)
        metrics = _evaluate_unsupervised(model, x_val, config.target_anomaly_rate)
        payload = {"params": params, "metrics": metrics}
        if best_payload is None or metrics["score"] > best_payload["metrics"]["score"]:
            best_payload = payload
            best_model = model

    if best_payload is None or best_model is None:
        raise RuntimeError("Model selection failed unexpectedly.")

    output_dir.mkdir(parents=True, exist_ok=True)
    model_path = output_dir / "fraud_anomaly_isolation_forest.joblib"
    report_path = output_dir / "training_report.json"
    feature_preview_path = output_dir / "feature_preview.csv"

    joblib.dump(best_model, model_path)
    features_df.head(250).to_csv(feature_preview_path, index=False)

    report = {
        "rows_total": int(len(raw_df)),
        "rows_with_numeric_features": int(len(features_df)),
        "feature_columns": list(features_df.columns),
        "best_candidate": best_payload,
        "model_path": str(model_path),
        "feature_preview_path": str(feature_preview_path),
    }
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    data_dir = root / "data"
    output_dir = root / "ml" / "artifacts"
    report = train_and_save(data_dir=data_dir, output_dir=output_dir)
    print("Training completed.")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
