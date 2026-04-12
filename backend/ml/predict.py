"""Load saved RF and predict cognitive load plus global feature importances."""

from __future__ import annotations

import os
from typing import Any, Mapping

import joblib

from backend.ml.features import FEATURE_NAMES, vector_from_analysis_result

_DEFAULT_MODEL_PATH = os.path.join(
    os.path.dirname(__file__), "artifacts", "cognitive_load_rf.joblib"
)


def _load_payload(path: str | None = None) -> dict[str, Any]:
    p = path or _DEFAULT_MODEL_PATH
    if not os.path.isfile(p):
        raise FileNotFoundError(
            f"Missing model file: {p}. From repo root run: python -m backend.ml.train"
        )
    return joblib.load(p)


def predict_cognitive_load(
    analysis: Mapping[str, Any],
    model_path: str | None = None,
) -> dict[str, Any]:
    from backend.ml.labels import rule_based_cognitive_load

    payload = _load_payload(model_path)
    model = payload["model"]
    names = list(payload.get("feature_names", FEATURE_NAMES))

    h = analysis["heading_features"]
    n = analysis["nav_features"]
    t = analysis["text_features"]
    X = vector_from_analysis_result(analysis)
    pred = float(model.predict(X)[0])
    pred = float(max(0.0, min(100.0, pred)))

    rule_load = rule_based_cognitive_load(h, n, t)
    imp = getattr(model, "feature_importances_", None)
    importance_list = (
        [float(x) for x in imp.tolist()] if imp is not None else [0.0] * len(names)
    )

    top_idx = sorted(
        range(len(names)), key=lambda i: importance_list[i], reverse=True
    )[:5]

    return {
        "cognitive_load_ml": round(pred, 3),
        "cognitive_load_rule": round(rule_load, 3),
        "delta_ml_minus_rule": round(pred - rule_load, 3),
        "feature_names": names,
        "feature_importances": importance_list,
        "top_features": [
            {"name": names[i], "importance": round(importance_list[i], 5)}
            for i in top_idx
        ],
        "model_meta": {
            "artifact": payload.get("label", "unknown"),
            "train_samples": payload.get("train_samples"),
            "test_mae": payload.get("test_mae"),
            "test_r2": payload.get("test_r2"),
        },
    }
