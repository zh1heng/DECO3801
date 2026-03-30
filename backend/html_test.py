import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse


def fetch_html(url: str, timeout: int = 10) -> str:
    """
    Fetch HTML content from a webpage.
    """
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/123.0.0.0 Safari/537.36"
        )
    }

    response = requests.get(url, headers=headers, timeout=timeout)
    response.raise_for_status()
    return response.text


def parse_html(html: str) -> BeautifulSoup:
    """
    Parse HTML into a BeautifulSoup object.
    """
    return BeautifulSoup(html, "html.parser")


def extract_headings(soup: BeautifulSoup) -> dict:
    """
    Extract heading-related features for a simple Visual Hierarchy estimate.
    """
    h1_count = len(soup.find_all("h1"))
    h2_count = len(soup.find_all("h2"))
    h3_count = len(soup.find_all("h3"))

    heading_tags = soup.find_all(re.compile("^h[1-6]$"))
    heading_levels = []

    for tag in heading_tags:
        try:
            heading_levels.append(int(tag.name[1]))
        except (ValueError, IndexError):
            continue

    heading_jump_count = 0
    for i in range(1, len(heading_levels)):
        if heading_levels[i] - heading_levels[i - 1] > 1:
            heading_jump_count += 1

    return {
        "h1_count": h1_count,
        "h2_count": h2_count,
        "h3_count": h3_count,
        "total_headings": len(heading_tags),
        "heading_jump_count": heading_jump_count,
    }


def extract_navigation(soup: BeautifulSoup) -> dict:
    """
    Extract simple navigation-related features.
    """
    nav_links = soup.select("nav a")
    nav_link_count = len(nav_links)

    breadcrumb_keywords = ["breadcrumb", "breadcrumbs"]
    has_breadcrumb = False

    for tag in soup.find_all(True, class_=True):
        classes = " ".join(tag.get("class", [])).lower()
        if any(keyword in classes for keyword in breadcrumb_keywords):
            has_breadcrumb = True
            break

    return {
        "nav_link_count": nav_link_count,
        "has_breadcrumb": has_breadcrumb,
    }


def clean_text(text: str) -> str:
    """
    Normalize whitespace.
    """
    return re.sub(r"\s+", " ", text).strip()


def extract_text_features(soup: BeautifulSoup) -> dict:
    """
    Extract simple language-related features from paragraph text.
    """
    paragraphs = soup.find_all("p")
    paragraph_texts = [clean_text(p.get_text(" ", strip=True)) for p in paragraphs]
    paragraph_texts = [p for p in paragraph_texts if p]

    full_text = " ".join(paragraph_texts)
    full_text = clean_text(full_text)

    words = re.findall(r"\b[\w'-]+\b", full_text)
    sentences = re.split(r"[.!?]+", full_text)
    sentences = [s.strip() for s in sentences if s.strip()]

    word_count = len(words)
    sentence_count = len(sentences)
    paragraph_count = len(paragraph_texts)

    avg_sentence_length = word_count / sentence_count if sentence_count > 0 else 0
    avg_word_length = (
        sum(len(word) for word in words) / word_count if word_count > 0 else 0
    )
    avg_paragraph_length = word_count / paragraph_count if paragraph_count > 0 else 0

    return {
        "word_count": word_count,
        "sentence_count": sentence_count,
        "paragraph_count": paragraph_count,
        "avg_sentence_length": round(avg_sentence_length, 2),
        "avg_word_length": round(avg_word_length, 2),
        "avg_paragraph_length": round(avg_paragraph_length, 2),
    }


def score_visual_hierarchy(heading_features: dict) -> tuple[int, list[str]]:
    """
    Rule-based score for Visual Hierarchy.
    Higher score = more cognitively complex.
    """
    score = 0
    reasons = []

    if heading_features["h1_count"] == 0:
        score += 20
        reasons.append("No h1 found")

    if heading_features["h1_count"] > 2:
        score += 15
        reasons.append("Too many h1 headings")

    if heading_features["total_headings"] == 0:
        score += 25
        reasons.append("No heading structure detected")

    if heading_features["heading_jump_count"] > 0:
        penalty = min(heading_features["heading_jump_count"] * 5, 20)
        score += penalty
        reasons.append(f"Heading level jumps detected ({heading_features['heading_jump_count']})")

    return min(score, 40), reasons


def score_navigation(nav_features: dict) -> tuple[int, list[str]]:
    """
    Rule-based score for Navigation Depth/Complexity.
    """
    score = 0
    reasons = []

    if nav_features["nav_link_count"] > 10:
        score += 10
        reasons.append("Navigation has many links")

    if nav_features["nav_link_count"] > 20:
        score += 10
        reasons.append("Navigation is very dense")

    if not nav_features["has_breadcrumb"]:
        score += 5
        reasons.append("No breadcrumb detected")

    return min(score, 25), reasons


def score_language(text_features: dict) -> tuple[int, list[str]]:
    """
    Rule-based score for Language Simplicity.
    Higher score = more difficult language / reading burden.
    """
    score = 0
    reasons = []

    if text_features["avg_sentence_length"] > 20:
        score += 10
        reasons.append("Sentences are relatively long")

    if text_features["avg_sentence_length"] > 30:
        score += 10
        reasons.append("Sentences are very long")

    if text_features["avg_word_length"] > 5:
        score += 8
        reasons.append("Average word length is high")

    if text_features["avg_paragraph_length"] > 80:
        score += 7
        reasons.append("Paragraphs are relatively long")

    return min(score, 35), reasons


def compute_cognitive_complexity_score(
    heading_features: dict,
    nav_features: dict,
    text_features: dict
) -> dict:
    """
    Combine all rule-based sub-scores into a final cognitive complexity score (0-100).
    """
    vh_score, vh_reasons = score_visual_hierarchy(heading_features)
    nav_score, nav_reasons = score_navigation(nav_features)
    lang_score, lang_reasons = score_language(text_features)

    total_score = vh_score + nav_score + lang_score
    total_score = min(total_score, 100)

    if total_score < 34:
        level = "Low"
    elif total_score < 67:
        level = "Medium"
    else:
        level = "High"

    return {
        "visual_hierarchy_score": vh_score,
        "navigation_score": nav_score,
        "language_score": lang_score,
        "total_score": total_score,
        "complexity_level": level,
        "reasons": vh_reasons + nav_reasons + lang_reasons,
    }


def analyze_webpage(url: str) -> dict:
    """
    Complete analysis pipeline for one webpage.
    """
    html = fetch_html(url)
    soup = parse_html(html)

    heading_features = extract_headings(soup)
    nav_features = extract_navigation(soup)
    text_features = extract_text_features(soup)

    score_result = compute_cognitive_complexity_score(
        heading_features, nav_features, text_features
    )

    domain = urlparse(url).netloc

    return {
        "url": url,
        "domain": domain,
        "heading_features": heading_features,
        "nav_features": nav_features,
        "text_features": text_features,
        "score_result": score_result,
    }


def print_report(result: dict) -> None:
    """
    Print a readable report.
    """
    print("=" * 60)
    print("COGNITIVE ACCESSIBILITY - MINIMAL ANALYSIS REPORT")
    print("=" * 60)
    print(f"URL: {result['url']}")
    print(f"Domain: {result['domain']}")
    print()

    print("[1] Heading / Hierarchy Features")
    for key, value in result["heading_features"].items():
        print(f"  - {key}: {value}")
    print()

    print("[2] Navigation Features")
    for key, value in result["nav_features"].items():
        print(f"  - {key}: {value}")
    print()

    print("[3] Language Features")
    for key, value in result["text_features"].items():
        print(f"  - {key}: {value}")
    print()

    print("[4] Cognitive Complexity Score")
    for key, value in result["score_result"].items():
        if key != "reasons":
            print(f"  - {key}: {value}")

    print("  - reasons:")
    if result["score_result"]["reasons"]:
        for reason in result["score_result"]["reasons"]:
            print(f"    * {reason}")
    else:
        print("    * No major issues detected by current rules")

    print("=" * 60)


if __name__ == "__main__":
    test_url = input("Enter a webpage URL: ").strip()

    try:
        analysis_result = analyze_webpage(test_url)
        print_report(analysis_result)
    except requests.RequestException as e:
        print(f"[ERROR] Failed to fetch webpage: {e}")
    except Exception as e:
        print(f"[ERROR] Unexpected issue: {e}")