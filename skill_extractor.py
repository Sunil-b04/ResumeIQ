"""
skill_extractor.py
──────────────────
Extracts skills from resume text and job descriptions,
then computes match/gap analysis using keyword matching +
optional sentence-transformers similarity.
"""

import re
from typing import Optional

# ── Master skill taxonomy (extend freely) ────────────────────────────────────
SKILL_TAXONOMY = {
    "Languages":       ["python", "java", "javascript", "typescript", "c++", "c#", "go",
                        "rust", "r", "scala", "kotlin", "swift", "php", "ruby", "matlab"],
    "ML / AI":         ["machine learning", "deep learning", "neural network", "nlp",
                        "computer vision", "reinforcement learning", "llm", "transformers",
                        "pytorch", "tensorflow", "keras", "scikit-learn", "xgboost",
                        "lightgbm", "hugging face", "langchain", "openai", "generative ai"],
    "Data":            ["sql", "nosql", "mongodb", "postgresql", "mysql", "sqlite",
                        "pandas", "numpy", "spark", "hadoop", "kafka", "airflow",
                        "dbt", "databricks", "snowflake", "bigquery", "redshift",
                        "data pipeline", "etl", "data warehouse"],
    "Cloud":           ["aws", "azure", "gcp", "google cloud", "sagemaker", "lambda",
                        "ec2", "s3", "vertex ai", "azure ml", "cloud functions"],
    "DevOps / MLOps":  ["docker", "kubernetes", "ci/cd", "github actions", "jenkins",
                        "mlflow", "kubeflow", "terraform", "ansible", "linux", "bash"],
    "Web / APIs":      ["rest api", "graphql", "fastapi", "flask", "django", "react",
                        "node.js", "html", "css", "websocket"],
    "Visualization":   ["matplotlib", "seaborn", "plotly", "tableau", "power bi",
                        "looker", "d3.js"],
    "Soft Skills":     ["leadership", "communication", "teamwork", "agile", "scrum",
                        "problem solving", "mentoring", "cross-functional"],
}

# Flat list for fast lookup
ALL_SKILLS = {s.lower() for group in SKILL_TAXONOMY.values() for s in group}


def _normalize(text: str) -> str:
    return text.lower()


def extract_skills_from_text(text: str) -> list[str]:
    """Return list of recognized skills found in text."""
    norm = _normalize(text)
    found = []
    for skill in ALL_SKILLS:
        # Use word-boundary-aware matching
        pattern = r"\b" + re.escape(skill) + r"\b"
        if re.search(pattern, norm):
            found.append(skill)
    return sorted(set(found))


def compute_skill_gap(resume_skills: list[str], jd_skills: list[str]) -> dict:
    """
    Compare resume skills vs JD skills.
    Returns:
        matched   – skills present in both
        missing   – skills in JD but not resume
        extra     – skills in resume not required by JD
        score_pct – match percentage
    """
    resume_set = set(resume_skills)
    jd_set     = set(jd_skills)

    matched = sorted(resume_set & jd_set)
    missing = sorted(jd_set - resume_set)
    extra   = sorted(resume_set - jd_set)
    score   = round(len(matched) / len(jd_set) * 100) if jd_set else 0

    return {
        "matched":   matched,
        "missing":   missing,
        "extra":     extra,
        "score_pct": score,
    }


def group_skills_by_category(skills: list[str]) -> dict:
    """Organize a flat skill list back into taxonomy categories."""
    grouped = {}
    for cat, cat_skills in SKILL_TAXONOMY.items():
        hits = [s for s in skills if s in {c.lower() for c in cat_skills}]
        if hits:
            grouped[cat] = hits
    return grouped


# ── Optional semantic similarity (requires sentence-transformers) ──────────────
def semantic_similarity(text_a: str, text_b: str) -> Optional[float]:
    """
    Returns cosine similarity [0-1] between two text chunks.
    Falls back to None if sentence-transformers is unavailable.
    """
    try:
        from sentence_transformers import SentenceTransformer, util
        model = SentenceTransformer("all-MiniLM-L6-v2")
        emb_a = model.encode(text_a, convert_to_tensor=True)
        emb_b = model.encode(text_b, convert_to_tensor=True)
        score = util.cos_sim(emb_a, emb_b).item()
        return round(score, 4)
    except Exception:
        return None
