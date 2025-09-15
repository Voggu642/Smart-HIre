import json
import os
import re
from typing import List, Dict, Tuple
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

def load_json(path: str):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def normalize_text(s: str) -> str:
    s = s.lower()
    s = re.sub(r"[^a-z0-9\s\+\#\.\-]", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s

class SkillGraph:
    def __init__(self, path: str):
        self.graph = load_json(path)  # {"canonical_skill": ["synonym1", "synonym2"]}
        self.syn_to_canonical = {}
        for canon, syns in self.graph.items():
            self.syn_to_canonical[canon.lower()] = canon
            for s in syns:
                self.syn_to_canonical[s.lower()] = canon

    def expand(self, skills: List[str]) -> List[str]:
        expanded = set()
        for s in skills:
            k = s.lower().strip()
            canon = self.syn_to_canonical.get(k, s)
            expanded.add(canon)
        return sorted(expanded)

    def canonicalize_text(self, text: str) -> str:
        t = text
        # Replace synonyms with canonical forms for better matching
        for syn, canon in self.syn_to_canonical.items():
            t = re.sub(rf"\b{re.escape(syn)}\b", canon, t, flags=re.IGNORECASE)
        return t

class JobRecommender:
    def __init__(self, jobs_path: str, skills_graph_path: str):
        self.jobs = load_json(jobs_path)  # list of jobs
        self.skill_graph = SkillGraph(skills_graph_path)

        # Preprocess job corpus
        corpus = []
        self.job_ids = []
        self.job_titles = []
        self.job_skills = []
        for j in self.jobs:
            self.job_ids.append(j["id"])
            self.job_titles.append(j["title"])
            self.job_skills.append([s.lower() for s in j.get("skills", [])])
            text = f"{j['title']} {j['description']} {' '.join(j.get('skills', []))}"
            text = self.skill_graph.canonicalize_text(text)
            corpus.append(normalize_text(text))

        self.vectorizer = TfidfVectorizer(max_features=3000, ngram_range=(1,2))
        self.job_matrix = self.vectorizer.fit_transform(corpus)

        # Store top terms per job for explanations
        self.feature_names = np.array(self.vectorizer.get_feature_names_out())
        self.job_top_terms = self._compute_job_top_terms(top_n=10)

    def _compute_job_top_terms(self, top_n=10):
        top_terms = {}
        for idx in range(self.job_matrix.shape[0]):
            row = self.job_matrix[idx].toarray().ravel()
            if row.sum() == 0:
                top_terms[self.job_ids[idx]] = []
                continue
            top_idx = row.argsort()[-top_n:][::-1]
            top_terms[self.job_ids[idx]] = [self.feature_names[i] for i in top_idx]
        return top_terms

    def recommend(self, resume_text: str, skills: List[str], top_k: int = 5):
        # Canonicalize + normalize candidate text
        resume_text = self.skill_graph.canonicalize_text(resume_text)
        expanded_skills = self.skill_graph.expand(skills)
        candidate_text = f"{resume_text} {' '.join(expanded_skills)}"
        candidate_vec = self.vectorizer.transform([normalize_text(candidate_text)])

        sims = cosine_similarity(candidate_vec, self.job_matrix).ravel()
        top_idx = sims.argsort()[-top_k:][::-1]

        results = []
        for i in top_idx:
            job_id = self.job_ids[i]
            title = self.job_titles[i]
            score = float(sims[i])
            job_skillset = set(self.job_skills[i])
            matched_skills = sorted(list(job_skillset.intersection({s.lower() for s in expanded_skills})))

            overlap_terms = list(set(self.job_top_terms.get(job_id, [])) & set(normalize_text(candidate_text).split()))
            why = f"Matched on skills {matched_skills[:5]} and terms {overlap_terms[:5]}."

            results.append({
                "job_id": job_id,
                "title": title,
                "score": round(score, 4),
                "matched_skills": matched_skills,
                "key_terms_overlap": overlap_terms[:10],
                "why": why
            })

        debug = {
            "expanded_skills": expanded_skills,
        }
        return results, debug
