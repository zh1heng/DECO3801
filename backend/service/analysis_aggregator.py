from backend.service.text_analysis_service import analyze_webpage_text
from backend.service.visual_analysis_service import score_visual

def compute_final_score(url: str) -> dict:
    """
    统一计算 final_score，接合 text_scoring 和预留的 visual_scoring 等
    """
    # 预留 crawler：analyze_webpage_text 中通过 page_crawling_pretender 调用了 playwright 抓取数据
    text_result = analyze_webpage_text(url, save_screenshot=False)
    text_scores = text_result.get("score_result", {})
    
    # 调用 visual_scoring 接口
    visual_result = score_visual("outputs/text_scoring_page.png")
    
    vh_score = text_scores.get("visual_hierarchy_score", 50.0)
    nav_score = text_scores.get("navigation_score", 50.0)
    lang_score = text_scores.get("language_score", 50.0)
    
    # 没公式的分数：预设为 10分
    visual_score = visual_result.get("visual_score", 10.0)
    other_fixed_score = 10.0

    # final_score 计算
    total_score = vh_score + nav_score + lang_score + visual_score + other_fixed_score

    # 提取 reasons
    reasons_dict = text_scores.get("reasons", {})
    reasons = []
    if isinstance(reasons_dict, dict):
        for k, v in reasons_dict.items():
            if isinstance(v, list):
                reasons.extend(v)
            else:
                reasons.append(str(v))
    
    visual_reasons = visual_result.get("reasons", [])
    if isinstance(visual_reasons, list):
        reasons.extend(visual_reasons)
    
    # 添加预设分数的说明
    reasons.append("Other scores without formulas defaulted to 10.")

    return {
        "vh_score": vh_score,
        "nav_score": nav_score,
        "lang_score": lang_score,
        "visual_score": visual_score,
        "total_score": total_score,
        "reasons": reasons
    }
