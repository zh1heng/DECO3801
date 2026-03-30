from fastapi import APIRouter, HTTPException
from backend.schema.analyze import AnalyzeRequest, AnalyzeResponse
from backend.html_test import analyze_webpage
import requests

router = APIRouter()

@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze_url(request: AnalyzeRequest):
    try:
        # Calls the function from the existing script
        result = analyze_webpage(request.url)
        score_result = result.get("score_result", {})
        
        # Extract the required fields, setting default to 5 if somehow missing
        vh_score = score_result.get("visual_hierarchy_score", 50.0)
        nav_score = score_result.get("navigation_score", 50.0)
        lang_score = score_result.get("language_score", 50.0)
        total_score = score_result.get("total_score", 50.0)
        reasons = score_result.get("reasons", [])
        
        return AnalyzeResponse(
            vh_score=vh_score,
            nav_score=nav_score,
            lang_score=lang_score,
            total_score=total_score,
            reasons=reasons
        )
    except requests.RequestException as e:
        raise HTTPException(status_code=400, detail=f"Failed to fetch webpage: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
