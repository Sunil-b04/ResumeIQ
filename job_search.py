"""
job_search.py
─────────────
Searches live job listings via JSearch (RapidAPI).
Falls back to curated mock data if no API key is set.
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY", "")
JSEARCH_HOST = "jsearch.p.rapidapi.com"


def search_jobs(query: str, location: str = "Remote", num_pages: int = 1) -> list[dict]:
    """
    Search live jobs. Returns list of job dicts.
    Falls back to mock data if RAPIDAPI_KEY is not set.
    """
    if not RAPIDAPI_KEY:
        return _mock_jobs(query)

    url = f"https://{JSEARCH_HOST}/search"
    headers = {
        "X-RapidAPI-Key":  RAPIDAPI_KEY,
        "X-RapidAPI-Host": JSEARCH_HOST,
    }
    params = {
        "query":     f"{query} {location}",
        "page":      "1",
        "num_pages": str(num_pages),
    }

    try:
        resp = requests.get(url, headers=headers, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json().get("data", [])
        return [_normalize_job(j) for j in data]
    except Exception as e:
        print(f"JSearch error: {e}")
        return _mock_jobs(query)


def _normalize_job(raw: dict) -> dict:
    """Map RapidAPI response to our internal schema."""
    return {
        "title":     raw.get("job_title", "Unknown Role"),
        "company":   raw.get("employer_name", "Unknown Company"),
        "location":  raw.get("job_city", "") + ", " + raw.get("job_country", ""),
        "type":      raw.get("job_employment_type", "Full-time"),
        "salary":    _format_salary(raw),
        "posted":    raw.get("job_posted_at_datetime_utc", ""),
        "url":       raw.get("job_apply_link", "#"),
        "description": raw.get("job_description", "")[:500],
        "remote":    raw.get("job_is_remote", False),
    }


def _format_salary(raw: dict) -> str:
    lo = raw.get("job_min_salary")
    hi = raw.get("job_max_salary")
    if lo and hi:
        return f"${int(lo):,} – ${int(hi):,}"
    return "Not disclosed"


def _mock_jobs(query: str) -> list[dict]:
    """Curated mock listings used when no API key is available."""
    return [
        {"title": "Senior ML Engineer",       "company": "Google DeepMind",  "location": "Remote",         "type": "Full-time", "salary": "$180K – $240K", "posted": "2h ago",  "url": "#", "description": "Build production ML systems at scale.", "remote": True},
        {"title": "Data Scientist II",         "company": "Meta AI",          "location": "Menlo Park, US", "type": "Hybrid",    "salary": "$160K – $210K", "posted": "5h ago",  "url": "#", "description": "Drive data-driven decisions across products.", "remote": False},
        {"title": "Applied Scientist",         "company": "Amazon AWS",       "location": "Seattle, US",    "type": "Hybrid",    "salary": "$155K – $200K", "posted": "1d ago",  "url": "#", "description": "Research and deploy ML solutions for AWS customers.", "remote": False},
        {"title": "AI Research Scientist",     "company": "Anthropic",        "location": "San Francisco",  "type": "Full-time", "salary": "$190K – $260K", "posted": "2d ago",  "url": "#", "description": "Safety-focused AI research and model development.", "remote": True},
        {"title": "ML Platform Engineer",      "company": "Stripe",           "location": "Remote",         "type": "Full-time", "salary": "$170K – $220K", "posted": "3d ago",  "url": "#", "description": "Build ML infrastructure and tooling for payment fraud detection.", "remote": True},
        {"title": "Research Engineer, NLP",    "company": "OpenAI",           "location": "San Francisco",  "type": "Full-time", "salary": "$200K – $300K", "posted": "1w ago",  "url": "#", "description": "Advance state-of-the-art language model capabilities.", "remote": False},
    ]
