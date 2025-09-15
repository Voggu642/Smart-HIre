from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from models import CandidateProfile, RecommendRequest, RecommendResponse, AnalyzeRequest, AnalyzeResponse, Suggestion
from recommender import JobRecommender
from resume_analyzer import analyze_resume
import os, json

BASE_DIR = os.path.dirname(__file__)
DATA_DIR = os.path.join(BASE_DIR, "sample_data")
JOBS_PATH = os.path.join(DATA_DIR, "jobs.json")
SKILLS_GRAPH_PATH = os.path.join(DATA_DIR, "skills_graph.json")

app = FastAPI(title="SmartHire MVP API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

reco = JobRecommender(JOBS_PATH, SKILLS_GRAPH_PATH)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/jobs")
def get_jobs():
    with open(JOBS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

@app.post("/recommend", response_model=RecommendResponse)
def recommend(req: RecommendRequest):
    results, debug = reco.recommend(req.candidate.resume_text, req.candidate.skills, top_k=req.top_k)
    return {"results": results, "debug": debug}

@app.post("/analyze", response_model=AnalyzeResponse)
def analyze(req: AnalyzeRequest):
    # If target_job_id provided, pull its keywords from jobs dataset
    target_keywords = []
    if req.target_job_id:
        with open(JOBS_PATH, "r", encoding="utf-8") as f:
            jobs = json.load(f)
            for j in jobs:
                if j["id"] == req.target_job_id:
                    target_keywords = j.get("skills", []) + j.get("keywords", [])
                    break
    report = analyze_resume(req.resume_text, target_keywords)
    return {
        "suggestions": report["suggestions"],
        "detected_skills": [],  # kept simple for MVP
        "missing_keywords": report["missing_keywords"]
    }
