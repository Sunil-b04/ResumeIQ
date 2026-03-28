"""
resume_builder.py
─────────────────
Generates a polished PDF resume from structured data using ReportLab.
"""

from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, HRFlowable, Table, TableStyle
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER


# ── Color palette ─────────────────────────────────────────────────────────────
ACCENT = colors.HexColor("#4f9eff")
DARK   = colors.HexColor("#1a1a2e")
GRAY   = colors.HexColor("#6b7a99")
LIGHT  = colors.HexColor("#f0f4f8")


def build_resume_pdf(data: dict) -> bytes:
    """
    Build a PDF resume from structured data dict.

    Expected keys:
        name, title, email, phone, linkedin, github, location,
        summary,
        experience: list of {role, company, duration, bullets: [str]}
        education:  list of {degree, school, year, gpa}
        skills:     list of str
        projects:   list of {name, description, tech, url}
        certifications: list of str
    """
    buf = BytesIO()
    doc = SimpleDocTemplate(
        buf,
        pagesize=A4,
        leftMargin=1.8*cm,
        rightMargin=1.8*cm,
        topMargin=1.5*cm,
        bottomMargin=1.5*cm,
    )

    styles = _build_styles()
    story  = []

    # ── Header ────────────────────────────────────────────────────────────────
    story.append(Paragraph(data.get("name", "Your Name"), styles["name"]))
    story.append(Paragraph(data.get("title", ""), styles["title"]))
    story.append(Spacer(1, 4))

    contact_parts = []
    if data.get("email"):    contact_parts.append(f"✉ {data['email']}")
    if data.get("phone"):    contact_parts.append(f"📞 {data['phone']}")
    if data.get("location"): contact_parts.append(f"📍 {data['location']}")
    if data.get("linkedin"): contact_parts.append(f"in/{data['linkedin']}")
    if data.get("github"):   contact_parts.append(f"github/{data['github']}")
    story.append(Paragraph("   |   ".join(contact_parts), styles["contact"]))
    story.append(_divider())

    # ── Summary ───────────────────────────────────────────────────────────────
    if data.get("summary"):
        story.append(Paragraph("PROFESSIONAL SUMMARY", styles["section_head"]))
        story.append(Paragraph(data["summary"], styles["body"]))
        story.append(_divider())

    # ── Experience ────────────────────────────────────────────────────────────
    if data.get("experience"):
        story.append(Paragraph("EXPERIENCE", styles["section_head"]))
        for exp in data["experience"]:
            _add_experience_entry(story, exp, styles)
        story.append(_divider())

    # ── Education ─────────────────────────────────────────────────────────────
    if data.get("education"):
        story.append(Paragraph("EDUCATION", styles["section_head"]))
        for edu in data["education"]:
            row = f"<b>{edu.get('degree','')}</b> — {edu.get('school','')}   <i>{edu.get('year','')}</i>"
            if edu.get("gpa"): row += f"   GPA: {edu['gpa']}"
            story.append(Paragraph(row, styles["body"]))
            story.append(Spacer(1, 4))
        story.append(_divider())

    # ── Skills ────────────────────────────────────────────────────────────────
    if data.get("skills"):
        story.append(Paragraph("SKILLS", styles["section_head"]))
        story.append(Paragraph(" • ".join(data["skills"]), styles["body"]))
        story.append(_divider())

    # ── Projects ─────────────────────────────────────────────────────────────
    if data.get("projects"):
        story.append(Paragraph("PROJECTS", styles["section_head"]))
        for proj in data["projects"]:
            name_line = f"<b>{proj.get('name','')}</b>"
            if proj.get("url"): name_line += f"  <i>({proj['url']})</i>"
            story.append(Paragraph(name_line, styles["job_role"]))
            if proj.get("description"):
                story.append(Paragraph(proj["description"], styles["body"]))
            if proj.get("tech"):
                story.append(Paragraph(f"Tech: {proj['tech']}", styles["muted"]))
            story.append(Spacer(1, 6))
        story.append(_divider())

    # ── Certifications ────────────────────────────────────────────────────────
    if data.get("certifications"):
        story.append(Paragraph("CERTIFICATIONS", styles["section_head"]))
        for cert in data["certifications"]:
            story.append(Paragraph(f"• {cert}", styles["body"]))

    doc.build(story)
    return buf.getvalue()


# ── Helpers ───────────────────────────────────────────────────────────────────
def _add_experience_entry(story, exp: dict, styles: dict):
    role_text  = f"<b>{exp.get('role','')}</b>"
    comp_text  = f"{exp.get('company','')}  —  <i>{exp.get('duration','')}</i>"
    story.append(Paragraph(role_text, styles["job_role"]))
    story.append(Paragraph(comp_text, styles["job_meta"]))
    for bullet in exp.get("bullets", []):
        story.append(Paragraph(f"• {bullet}", styles["bullet"]))
    story.append(Spacer(1, 8))


def _divider():
    return HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#e0e6ef"), spaceAfter=6, spaceBefore=2)


def _build_styles() -> dict:
    base = getSampleStyleSheet()
    return {
        "name": ParagraphStyle("name", parent=base["Normal"],
            fontSize=22, fontName="Helvetica-Bold", textColor=DARK,
            alignment=TA_CENTER, spaceAfter=2),
        "title": ParagraphStyle("title", parent=base["Normal"],
            fontSize=11, fontName="Helvetica", textColor=ACCENT,
            alignment=TA_CENTER, spaceAfter=4),
        "contact": ParagraphStyle("contact", parent=base["Normal"],
            fontSize=8.5, textColor=GRAY, alignment=TA_CENTER, spaceAfter=6),
        "section_head": ParagraphStyle("section_head", parent=base["Normal"],
            fontSize=9, fontName="Helvetica-Bold", textColor=ACCENT,
            spaceBefore=8, spaceAfter=5, letterSpacing=1.5),
        "job_role": ParagraphStyle("job_role", parent=base["Normal"],
            fontSize=10.5, fontName="Helvetica-Bold", textColor=DARK, spaceAfter=1),
        "job_meta": ParagraphStyle("job_meta", parent=base["Normal"],
            fontSize=9, textColor=GRAY, spaceAfter=3),
        "bullet": ParagraphStyle("bullet", parent=base["Normal"],
            fontSize=9.5, leftIndent=12, spaceAfter=2),
        "body": ParagraphStyle("body", parent=base["Normal"],
            fontSize=9.5, leading=14, spaceAfter=4),
        "muted": ParagraphStyle("muted", parent=base["Normal"],
            fontSize=8.5, textColor=GRAY, spaceAfter=3),
    }
