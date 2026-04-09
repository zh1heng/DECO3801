import re
from bs4 import BeautifulSoup
from urllib.parse import urlparse

from page_crawling_pretender import SimpleNavigator


def parse_html(html: str) -> BeautifulSoup:
    """
    Parse HTML into a BeautifulSoup object.
    """
    return BeautifulSoup(html, "html.parser")


def clean_text(text: str) -> str:
    """
    Normalize whitespace.
    """
    return re.sub(r"\s+", " ", text).strip()


def extract_headings(soup: BeautifulSoup) -> dict:
    """
    Extract heading-related features for Visual Hierarchy.
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
    Extract more realistic navigation-related features.
    """
    # 主导航：优先 header 和 nav
    header_links = soup.select("header a")
    nav_links = soup.select("nav a")

    # footer 链接单独统计，后面不直接计入主导航复杂度
    footer_links = soup.select("footer a")

    # 去重
    def unique_links(tags):
        seen = set()
        results = []
        for tag in tags:
            href = tag.get("href", "").strip()
            text = clean_text(tag.get_text(" ", strip=True))
            key = (href, text)
            if key not in seen and (href or text):
                seen.add(key)
                results.append(tag)
        return results

    header_links = unique_links(header_links)
    nav_links = unique_links(nav_links)
    footer_links = unique_links(footer_links)

    # breadcrumb 检测
    breadcrumb_keywords = ["breadcrumb", "breadcrumbs"]
    has_breadcrumb = False

    for tag in soup.find_all(True, class_=True):
        classes = " ".join(tag.get("class", [])).lower()
        if any(keyword in classes for keyword in breadcrumb_keywords):
            has_breadcrumb = True
            break

    return {
        "header_link_count": len(header_links),
        "nav_link_count": len(nav_links),
        "footer_link_count": len(footer_links),
        "main_nav_link_count": max(len(header_links), len(nav_links)),
        "has_breadcrumb": has_breadcrumb,
    }

def extract_text_features(soup: BeautifulSoup) -> dict:
    """
    Extract language-related features from paragraph text.
    """
    paragraphs = soup.find_all("p")
    paragraph_texts = [clean_text(p.get_text(" ", strip=True)) for p in paragraphs]
    paragraph_texts = [p for p in paragraph_texts if p]

    full_text = clean_text(" ".join(paragraph_texts))

    words = re.findall(r"\b[\w'-]+\b", full_text)

    # 比原版更稳一点：先按标点切，再过滤掉特别短的碎片
    raw_sentences = re.split(r"[.!?]+", full_text)
    sentences = [s.strip() for s in raw_sentences if len(s.strip().split()) >= 3]

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
    Score for Visual Hierarchy.
    Higher score = better (less complex)
    Max score: 50
    """
    penalty = 0
    reasons = []

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
    """
    Higher score = better (less complex)
    Max score: 50
    """
    penalty = 0
    reasons = []

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

    # footer 太多，轻微扣分，但不要和主导航一样重
    if nav_features["footer_link_count"] > 20:
        penalty += 5
        reasons.append("Footer contains many additional links")

    if not nav_features["has_breadcrumb"]:
        penalty += 10
        reasons.append("No breadcrumb detected")

    score = max(0, 50 - penalty)
    return score, reasons


def score_language(text_features: dict) -> tuple[int, list[str]]:
    """
    Score for Language Simplicity.
    Higher score = better (easier to read)
    Max score: 50
    """
    penalty = 0
    reasons = []

    # Sentence length
    if text_features["avg_sentence_length"] > 18:
        penalty += 10
        reasons.append("Sentences are relatively long")

    if text_features["avg_sentence_length"] > 25:
        penalty += 10
        reasons.append("Sentences are long")

    if text_features["avg_sentence_length"] > 35:
        penalty += 10
        reasons.append("Sentences are very long")

    # Word length
    if text_features["avg_word_length"] > 4.8:
        penalty += 8
        reasons.append("Average word length is relatively high")

    if text_features["avg_word_length"] > 5.5:
        penalty += 6
        reasons.append("Average word length is high")

    # Paragraph length
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
    text_features: dict
) -> dict:
    """
    Compute three separate text-related feature scores.
    No total score for now.
    """
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


def analyze_html(html: str, url: str = "") -> dict:
    """
    Analyze already-fetched HTML.
    """
    soup = parse_html(html)

    heading_features = extract_headings(soup)
    nav_features = extract_navigation(soup)
    text_features = extract_text_features(soup)

    score_result = compute_text_feature_scores(
        heading_features, nav_features, text_features
    )

    domain = urlparse(url).netloc if url else ""

    return {
        "url": url,
        "domain": domain,
        "heading_features": heading_features,
        "nav_features": nav_features,
        "text_features": text_features,
        "score_result": score_result,
    }


def analyze_webpage_text(url: str, save_screenshot: bool = False) -> dict:
    """
    Open a webpage using Playwright, get HTML, and run text scoring.
    """
    navigator = SimpleNavigator(headless=False)

    try:
        navigator.open_url(url)
        html = navigator.get_html()

        if save_screenshot:
            navigator.save_screenshot("outputs/text_scoring_page.png")

        return analyze_html(html, url)

    finally:
        navigator.close()


def print_report(result: dict) -> None:
    """
    Print a readable report.
    """
    print("=" * 60)
    print("COGNITIVE ACCESSIBILITY - TEXT FEATURE REPORT")
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

    print("[4] Text Feature Scores (0-50 each)")
    print(f"  - visual_hierarchy_score: {result['score_result']['visual_hierarchy_score']}")
    print(f"  - navigation_score: {result['score_result']['navigation_score']}")
    print(f"  - language_score: {result['score_result']['language_score']}")
    print()

    print("[5] Reasons by Feature")

    print("  - visual_hierarchy:")
    if result["score_result"]["reasons"]["visual_hierarchy"]:
        for reason in result["score_result"]["reasons"]["visual_hierarchy"]:
            print(f"    * {reason}")
    else:
        print("    * No major issues detected")

    print("  - navigation:")
    if result["score_result"]["reasons"]["navigation"]:
        for reason in result["score_result"]["reasons"]["navigation"]:
            print(f"    * {reason}")
    else:
        print("    * No major issues detected")

    print("  - language:")
    if result["score_result"]["reasons"]["language"]:
        for reason in result["score_result"]["reasons"]["language"]:
            print(f"    * {reason}")
    else:
        print("    * No major issues detected")

    print("=" * 60)


if __name__ == "__main__":
    test_url = input("Enter a webpage URL: ").strip()

    try:
        analysis_result = analyze_webpage_text(test_url, save_screenshot=True)
        print_report(analysis_result)
    except Exception as e:
        print(f"[ERROR] Unexpected issue: {e}")