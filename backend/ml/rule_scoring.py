"""
Heuristic scores mirroring backend.service.text_analysis_service (no Playwright).
Keep in sync if upstream scoring rules change.
"""

from __future__ import annotations


def score_visual_hierarchy(heading_features: dict) -> tuple[int, list[str]]:
    penalty = 0
    reasons: list[str] = []

    if heading_features["total_headings"] == 0:
        penalty += 25
        reasons.append("No heading structure detected")

    if heading_features["h1_count"] == 0:
        penalty += 10
        reasons.append("No h1 found")

    if heading_features["h1_count"] > 2:
        penalty += 10
        reasons.append("Too many h1 headings")

    if heading_features["heading_jump_count"] > 0:
        jump_penalty = min(heading_features["heading_jump_count"] * 5, 15)
        penalty += jump_penalty
        reasons.append(
            f"Heading level jumps detected ({heading_features['heading_jump_count']})"
        )

    score = max(0, 50 - penalty)
    return score, reasons


def score_navigation(nav_features: dict) -> tuple[int, list[str]]:
    penalty = 0
    reasons: list[str] = []

    main_links = nav_features["main_nav_link_count"]

    if main_links > 8:
        penalty += 10
        reasons.append("Main navigation has many links")

    if main_links > 15:
        penalty += 10
        reasons.append("Main navigation is dense")

    if main_links > 25:
        penalty += 10
        reasons.append("Main navigation may overwhelm users")

    if nav_features["footer_link_count"] > 20:
        penalty += 5
        reasons.append("Footer contains many additional links")

    if not nav_features["has_breadcrumb"]:
        penalty += 10
        reasons.append("No breadcrumb detected")

    score = max(0, 50 - penalty)
    return score, reasons


def score_language(text_features: dict) -> tuple[int, list[str]]:
    penalty = 0
    reasons: list[str] = []

    if text_features["avg_sentence_length"] > 18:
        penalty += 10
        reasons.append("Sentences are relatively long")

    if text_features["avg_sentence_length"] > 25:
        penalty += 10
        reasons.append("Sentences are long")

    if text_features["avg_sentence_length"] > 35:
        penalty += 10
        reasons.append("Sentences are very long")

    if text_features["avg_word_length"] > 4.8:
        penalty += 8
        reasons.append("Average word length is relatively high")

    if text_features["avg_word_length"] > 5.5:
        penalty += 6
        reasons.append("Average word length is high")

    if text_features["avg_paragraph_length"] > 60:
        penalty += 4
        reasons.append("Paragraphs are relatively long")

    if text_features["avg_paragraph_length"] > 100:
        penalty += 2
        reasons.append("Paragraphs are very long")

    score = max(0, 50 - penalty)
    return score, reasons


def compute_text_feature_scores(
    heading_features: dict,
    nav_features: dict,
    text_features: dict,
) -> dict:
    vh_score, vh_reasons = score_visual_hierarchy(heading_features)
    nav_score, nav_reasons = score_navigation(nav_features)
    lang_score, lang_reasons = score_language(text_features)

    return {
        "visual_hierarchy_score": vh_score,
        "navigation_score": nav_score,
        "language_score": lang_score,
        "reasons": {
            "visual_hierarchy": vh_reasons,
            "navigation": nav_reasons,
            "language": lang_reasons,
        },
    }
