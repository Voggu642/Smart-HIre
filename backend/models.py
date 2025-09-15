from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class CandidateProfile(BaseModel):
    name: Optional[str] = None
    resume_text: str = Field(..., description="Raw text of the resume/profile")
    skills: List[str] = Field(default_factory=list)

class RecommendRequest(BaseModel):
    candidate: CandidateProfile
    top_k: int = 5

class Recommendation(BaseModel):
    job_id: str
    title: str
    score: float
    matched_skills: List[str] = []
    key_terms_overlap: List[str] = []
    why: str = ""

class RecommendResponse(BaseModel):
    results: List[Recommendation]
    debug: Optional[Dict[str, Any]] = None

class AnalyzeRequest(BaseModel):
    resume_text: str
    target_job_id: Optional[str] = None

class Suggestion(BaseModel):
    type: str
    message: str
    details: Optional[Dict[str, Any]] = None

class AnalyzeResponse(BaseModel):
    suggestions: List[Suggestion]
    detected_skills: List[str] = []
    missing_keywords: List[str] = []
