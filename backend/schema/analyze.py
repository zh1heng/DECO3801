from pydantic import BaseModel, HttpUrl
from typing import List

class AnalyzeRequest(BaseModel):
    url: str

class AnalyzeResponse(BaseModel):
    vh_score: float
    nav_score: float
    lang_score: float
    visual_score: float
    total_score: float
    reasons: List[str]
