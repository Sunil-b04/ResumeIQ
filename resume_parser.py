"""
resume_parser.py
────────────────
Extracts raw text from uploaded PDF resumes using pdfminer.six.
Also provides section-detection helpers.
"""

import re
from io import BytesIO
from pdfminer.high_level import extract_text_to_fp
from pdfminer.layout import LAParams


# ── Section header keywords ───────────────────────────────────────────────────
SECTION_KEYWORDS = {
    "summary":     ["summary", "objective", "profile", "about"],
    "experience":  ["experience", "employment", "work history", "career"],
    "education":   ["education", "academic", "qualification", "degree"],
    "skills":      ["skills", "technical skills", "competencies", "technologies"],
    "projects":    ["projects", "portfolio", "open source"],
    "certifications": ["certifications", "licenses", "awards", "achievements"],
    "contact":     ["contact", "personal info", "links"],
}


def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    """Return all text from a PDF given its raw bytes."""
    output = BytesIO()
    extract_text_to_fp(
        BytesIO(pdf_bytes),
        output,
        laparams=LAParams(),
        output_type="text",
        codec="utf-8",
    )
    return output.getvalue().decode("utf-8", errors="replace")


def detect_sections(text: str) -> dict:
    """
    Split resume text into named sections.
    Returns a dict: { section_name: text_block }
    """
    lines = text.splitlines()
    sections = {}
    current = "header"
    buffer = []

    for line in lines:
        stripped = line.strip().lower()
        matched = False
        for sec, keywords in SECTION_KEYWORDS.items():
            if any(stripped.startswith(kw) or stripped == kw for kw in keywords):
                if buffer:
                    sections[current] = "\n".join(buffer).strip()
                current = sec
                buffer = []
                matched = True
                break
        if not matched:
            buffer.append(line)

    if buffer:
        sections[current] = "\n".join(buffer).strip()

    return sections


def extract_contact_info(text: str) -> dict:
    """Pull email, phone, LinkedIn, GitHub from raw text."""
    email   = re.findall(r"[\w.+-]+@[\w-]+\.[a-zA-Z]{2,}", text)
    phone   = re.findall(r"[\+]?[(]?[0-9]{1,4}[)]?[-\s\./0-9]{7,14}", text)
    linkedin = re.findall(r"linkedin\.com/in/[\w-]+", text, re.I)
    github   = re.findall(r"github\.com/[\w-]+", text, re.I)
    return {
        "email":    email[0]    if email    else "",
        "phone":    phone[0]    if phone    else "",
        "linkedin": linkedin[0] if linkedin else "",
        "github":   github[0]   if github   else "",
    }


def clean_text(text: str) -> str:
    """Remove excessive whitespace and non-printable chars."""
    text = re.sub(r"\s{3,}", "\n\n", text)
    text = re.sub(r"[^\x20-\x7E\n]", " ", text)
    return text.strip()
