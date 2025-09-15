import re
from typing import List, Dict

COMMON_SECTIONS = ["summary", "experience", "education", "projects", "skills"]
QUANT_HINTS = ["%","percent","per cent","increased","decreased","reduced","improved","boosted","cut","saved","grew","growth","achieved","delivered"]

def detect_sections(text: str) -> List[str]:
    t = text.lower()
    present = []
    for sec in COMMON_SECTIONS:
        if re.search(rf"\b{re.escape(sec)}\b", t):
            present.append(sec)
    return present

def has_quantified_achievements(text: str) -> bool:
    t = text.lower()
    return any(k in t for k in QUANT_HINTS) or bool(re.search(r"\b\d+(\.\d+)?\b", t))

def analyze_resume(text: str, target_job_keywords: List[str]) -> Dict:
    suggestions = []

    present = detect_sections(text)
    missing = [s for s in COMMON_SECTIONS if s not in present]
    if missing:
        suggestions.append({"type":"structure","message":f"Add missing sections: {', '.join(missing)}"})

    if not has_quantified_achievements(text):
        suggestions.append({"type":"impact","message":"Add quantified outcomes (numbers, %, metrics) to achievements."})

    # Missing keywords
    t = text.lower()
    missing_kw = []
    for kw in target_job_keywords:
        if not re.search(rf"\b{re.escape(kw.lower())}\b", t):
            missing_kw.append(kw)
    if missing_kw:
        suggestions.append({"type":"keywords","message":f"Add relevant keywords: {', '.join(missing_kw[:15])}"})
    return {
        "suggestions": suggestions,
        "missing_keywords": missing_kw
    }
