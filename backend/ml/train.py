"""Train RandomForest regressor and save to backend/ml/artifacts/. Run: python -m backend.ml.train"""

from __future__ import annotations

import os

import joblib
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.model_selection import train_test_split

from backend.ml.features import FEATURE_NAMES
from backend.ml.synthetic_data import generate_dataset

ARTIFACT_DIR = os.path.join(os.path.dirname(__file__), "artifacts")
DEFAULT_MODEL_PATH = os.path.join(ARTIFACT_DIR, "cognitive_load_rf.joblib")


def train_and_save(
    n_samples: int = 8000,
    seed: int = 42,
    model_path: str | None = None,
) -> dict:
    out_path = model_path or DEFAULT_MODEL_PATH
    os.makedirs(os.path.dirname(out_path), exist_ok=True)

    X, y = generate_dataset(n_samples=n_samples, seed=seed)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=seed
    )

    model = RandomForestRegressor(
        n_estimators=120,
        max_depth=14,
        min_samples_leaf=2,
        random_state=seed,
        n_jobs=-1,
    )
    model.fit(X_train, y_train)
    pred = model.predict(X_test)
    mae = float(mean_absolute_error(y_test, pred))
    r2 = float(r2_score(y_test, pred))

    payload = {
        "model": model,
        "feature_names": FEATURE_NAMES,
        "train_samples": int(X_train.shape[0]),
        "test_mae": mae,
        "test_r2": r2,
        "label": "rule_based_cognitive_load_v1",
    }
    joblib.dump(payload, out_path, compress=("zlib", 3))

    return {
        "path": out_path,
        "test_mae": mae,
        "test_r2": r2,
    }


if __name__ == "__main__":
    info = train_and_save()
    print("Saved:", info["path"])
    print("Test MAE:", info["test_mae"])
    print("Test R2:", info["test_r2"])
