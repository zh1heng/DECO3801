"""Synthetic tabular samples; labels from rule_based_cognitive_load."""

from __future__ import annotations

import random
from typing import Any

import numpy as np

from backend.ml.features import vector_from_components
from backend.ml.labels import rule_based_cognitive_load


def _random_heading(rng: random.Random) -> dict[str, Any]:
    h1 = rng.randint(0, 4)
    h2 = rng.randint(0, 12)
    h3 = rng.randint(0, 20)
    total = rng.randint(0, 40)
    jump = rng.randint(0, 8)
    return {
        "h1_count": h1,
        "h2_count": h2,
        "h3_count": h3,
        "total_headings": max(total, h1 + h2 + h3),
        "heading_jump_count": jump,
    }


def _random_nav(rng: random.Random) -> dict[str, Any]:
    header_n = rng.randint(0, 15)
    nav_n = rng.randint(0, 35)
    footer_n = rng.randint(0, 45)
    main_nav = max(header_n, nav_n)
    return {
        "header_link_count": header_n,
        "nav_link_count": nav_n,
        "footer_link_count": footer_n,
        "main_nav_link_count": main_nav,
        "has_breadcrumb": rng.random() < 0.35,
    }


def _random_text(rng: random.Random) -> dict[str, Any]:
    wc = rng.randint(0, 8000)
    sc = rng.randint(0, max(1, wc // 12))
    pc = rng.randint(0, max(1, wc // 80))
    avg_sent = wc / sc if sc > 0 else 0.0
    awl = rng.uniform(3.5, 7.5)
    avg_par = wc / pc if pc > 0 else 0.0
    return {
        "word_count": wc,
        "sentence_count": sc,
        "paragraph_count": pc,
        "avg_sentence_length": round(avg_sent, 2),
        "avg_word_length": round(awl, 2),
        "avg_paragraph_length": round(avg_par, 2),
    }


def generate_dataset(
    n_samples: int = 8000,
    seed: int = 42,
) -> tuple[np.ndarray, np.ndarray]:
    rng = random.Random(seed)
    X_list: list[np.ndarray] = []
    y_list: list[float] = []

    for _ in range(n_samples):
        h = _random_heading(rng)
        n = _random_nav(rng)
        t = _random_text(rng)
        y = rule_based_cognitive_load(h, n, t)
        X_list.append(vector_from_components(h, n, t)[0])
        y_list.append(y)

    X = np.stack(X_list, axis=0).astype(np.float32)
    y = np.asarray(y_list, dtype=np.float32)
    return X, y
