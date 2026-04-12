"""Rule-derived cognitive load label (0-100, higher = more load)."""

from __future__ import annotations

from typing import Any, Mapping

from backend.ml.rule_scoring import compute_text_feature_scores


def rule_based_cognitive_load(
    heading_features: Mapping[str, Any],
    nav_features: Mapping[str, Any],
    text_features: Mapping[str, Any],
) -> float:
    sr = compute_text_feature_scores(
        dict(heading_features), dict(nav_features), dict(text_features)
    )
    vh = float(sr["visual_hierarchy_score"])
    nav = float(sr["navigation_score"])
    lang = float(sr["language_score"])
    goodness = (vh + nav + lang) / 150.0
    load = (1.0 - goodness) * 100.0
    return float(round(load, 4))
