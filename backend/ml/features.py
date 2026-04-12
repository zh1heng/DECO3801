"""Feature vector for cognitive-load regression; column order must match training."""

from __future__ import annotations

from typing import Any, Mapping

import numpy as np

FEATURE_NAMES: list[str] = [
    "h1_count",
    "h2_count",
    "h3_count",
    "total_headings",
    "heading_jump_count",
    "header_link_count",
    "nav_link_count",
    "footer_link_count",
    "main_nav_link_count",
    "has_breadcrumb",
    "word_count",
    "sentence_count",
    "paragraph_count",
    "avg_sentence_length",
    "avg_word_length",
    "avg_paragraph_length",
]


def _get(d: Mapping[str, Any], key: str, default: float = 0.0) -> float:
    v = d.get(key, default)
    if v is None:
        return float(default)
    if isinstance(v, bool):
        return 1.0 if v else 0.0
    return float(v)


def vector_from_components(
    heading_features: Mapping[str, Any],
    nav_features: Mapping[str, Any],
    text_features: Mapping[str, Any],
) -> np.ndarray:
    return np.asarray(
        [
            [
                _get(heading_features, "h1_count"),
                _get(heading_features, "h2_count"),
                _get(heading_features, "h3_count"),
                _get(heading_features, "total_headings"),
                _get(heading_features, "heading_jump_count"),
                _get(nav_features, "header_link_count"),
                _get(nav_features, "nav_link_count"),
                _get(nav_features, "footer_link_count"),
                _get(nav_features, "main_nav_link_count"),
                _get(nav_features, "has_breadcrumb", 0.0),
                _get(text_features, "word_count"),
                _get(text_features, "sentence_count"),
                _get(text_features, "paragraph_count"),
                _get(text_features, "avg_sentence_length"),
                _get(text_features, "avg_word_length"),
                _get(text_features, "avg_paragraph_length"),
            ]
        ],
        dtype=np.float32,
    )


def vector_from_analysis_result(analysis: Mapping[str, Any]) -> np.ndarray:
    return vector_from_components(
        analysis["heading_features"],
        analysis["nav_features"],
        analysis["text_features"],
    )
