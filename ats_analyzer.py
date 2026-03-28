"""
ats_analyzer.py
───────────────
Scores a resume against a job description for ATS compatibility.
Returns a structured report with sub-scores and recommendations.
"""

import re
from skill_extractor import extract_skills_from_text, compute_skill_gap


# ── ATS Format checks ─────────────────────────────────────────────────────────
REQUIRED_SECTIONS = ["experience", "education", "skills"]
GOOD_ACTION_VERBS = [
    "achieved", "built", "created", "delivered", "designed", "developed",
    "drove", "engineered", "established", "implemented", "improved", "increased",
    "launched", "led", "managed", "optimized", "produced", "reduced", "scaled",
    "shipped", "spearheaded", "streamlined", "transformed",
]
BAD_PATTERNS = [
    r"<[^>]+>",        # HTML tags
    r"\|{3,}",         # Table pipes
    r"_{5,}",          # Long underlines (often header artifacts)
]


def score_keywords(resume_text: str, jd_text: str) -> dict:
    """Keyword overlap between resume and JD."""
    resume_words = set(re.findall(r"\b\w{4,}\b", resume_text.lower()))
    jd_words     = set(re.findall(r"\b\w{4,}\b", jd_text.lower()))
    overlap      = resume_words & jd_words
    pct = round(len(overlap) / len(jd_words) * 100) if jd_words else 0
    return {"score": min(pct, 100), "matched": len(overlap), "total_jd": len(jd_words)}


def score_format(resume_text: str) -> dict:
    """Heuristic format score — penalizes ATS-unfriendly patterns."""
    penalty = 0
    issues  = []

    for pat in BAD_PATTERNS:
        if re.search(pat, resume_text):
            penalty += 15
            issues.append(f"Detected problematic pattern: {pat}")

    # Check length (too short or too long hurts)
    word_count = len(resume_text.split())
    if word_count < 200:
        penalty += 20
        issues.append("Resume is too short (<200 words)")
    elif word_count > 1200:
        penalty += 10
        issues.append("Resume may be too long (>1200 words)")

    score = max(0, 100 - penalty)
    return {"score": score, "issues": issues, "word_count": word_count}


def score_sections(resume_text: str, detected_sections: dict) -> dict:
    """Check presence of critical resume sections."""
    present = []
    missing = []
    for sec in REQUIRED_SECTIONS:
        if sec in detected_sections and len(detected_sections[sec]) > 30:
            present.append(sec)
        else:
            missing.append(sec)

    score = round(len(present) / len(REQUIRED_SECTIONS) * 100)
    return {"score": score, "present": present, "missing": missing}


def score_impact(resume_text: str) -> dict:
    """Check for strong action verbs and quantified achievements."""
    lower = resume_text.lower()
    found_verbs = [v for v in GOOD_ACTION_VERBS if v in lower]
    numbers     = re.findall(r"\b\d+[\%xX]?\b", resume_text)
    has_metrics = len(numbers) >= 3

    verb_score   = min(len(found_verbs) * 5, 60)
    metric_score = 40 if has_metrics else 10
    score        = min(verb_score + metric_score, 100)

    return {
        "score":       score,
        "action_verbs": found_verbs,
        "metrics_count": len(numbers),
        "has_metrics": has_metrics,
    }


def full_ats_report(resume_text: str, jd_text: str, detected_sections: dict) -> dict:
    """
    Master function — returns complete ATS analysis dict.
    Keys: overall, keyword, format, sections, impact, skills, recommendations
    """
    kw  = score_keywords(resume_text, jd_text)
    fmt = score_format(resume_text)
    sec = score_sections(resume_text, detected_sections)
    imp = score_impact(resume_text)

    resume_skills = extract_skills_from_text(resume_text)
    jd_skills     = extract_skills_from_text(jd_text)
    gap           = compute_skill_gap(resume_skills, jd_skills)

    # Weighted overall
    overall = round(
        kw["score"]  * 0.30 +
        fmt["score"] * 0.20 +
        sec["score"] * 0.20 +
        imp["score"] * 0.15 +
        gap["score_pct"] * 0.15
    )

    # Build recommendations
    recs = []
    if kw["score"] < 70:
        recs.append("🔤 Add more JD keywords — especially in your summary and skills sections.")
    if gap["missing"]:
        recs.append(f"🔧 Missing skills to add: {', '.join(gap['missing'][:5])}")
    if not imp["has_metrics"]:
        recs.append("📊 Quantify achievements with numbers (%, $, users, time saved).")
    if sec["missing"]:
        recs.append(f"📋 Add missing sections: {', '.join(sec['missing'])}")
    if fmt["score"] < 80:
        recs.append(f"📐 Fix formatting issues: {'; '.join(fmt['issues'])}")
    if len(imp["action_verbs"]) < 5:
        recs.append("💪 Use stronger action verbs (led, built, delivered, optimized).")

    return {
        "overall":         overall,
        "keyword":         kw,
        "format":          fmt,
        "sections":        sec,
        "impact":          imp,
        "skills":          gap,
        "recommendations": recs,
        "resume_skills":   resume_skills,
        "jd_skills":       jd_skills,
    }
