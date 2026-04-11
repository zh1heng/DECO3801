from fastapi import APIRouter, HTTPException
from backend.schema.analyze import AnalyzeRequest, AnalyzeResponse
from backend.service.analysis_aggregator import compute_final_score

router = APIRouter()

@router.post("/analyze", response_model=AnalyzeResponse)
def analyze_url(request: AnalyzeRequest):
    try:
        result = compute_final_score(request.url)
        return AnalyzeResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
