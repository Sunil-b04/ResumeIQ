"""
app.py  —  ResumeIQ | AI Career Intelligence Platform
Run with: streamlit run app.py
"""

import streamlit as st
import plotly.graph_objects as go
import pandas as pd

from resume_parser   import extract_text_from_pdf, detect_sections, extract_contact_info, clean_text
from skill_extractor import extract_skills_from_text, compute_skill_gap, group_skills_by_category
from ats_analyzer    import full_ats_report
from ai_resume_coach import (
    get_ats_feedback, rewrite_summary, generate_roadmap,
    improve_bullet_points, generate_cover_letter,
    generate_interview_questions, get_interview_feedback,
    chat_with_resume, recommend_career_paths,
    estimate_salary, optimize_linkedin, realtime_resume_tailor,
)
from job_search      import search_jobs
from resume_builder  import build_resume_pdf

# ── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="ResumeIQ – AI Career Intelligence",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;900&family=DM+Sans:wght@300;400;500;600&display=swap');

html, body, [class*="css"] { font-family: 'DM Sans', sans-serif !important; }
.stApp { background: #050810 !important; }
section[data-testid="stSidebar"] { background: #0d1117 !important; border-right: 1px solid rgba(99,179,255,0.12); }
section[data-testid="stSidebar"] * { color: #e8edf5 !important; }
.block-container { padding-top: 1.5rem !important; }
[data-testid="stMetric"] { background: #0d1117; border: 1px solid rgba(99,179,255,0.12); border-radius: 16px; padding: 1rem 1.2rem; }
[data-testid="stMetricValue"] { font-family: 'Playfair Display', serif !important; font-size: 2.2rem !important; color: #4f9eff !important; }
.stButton > button { background: linear-gradient(135deg, #4f9eff, #a78bfa) !important; border: none !important; color: white !important; border-radius: 10px !important; font-weight: 600 !important; }
.stButton > button:hover { opacity: 0.88 !important; }
.stTabs [data-baseweb="tab-list"] { background: #0d1117 !important; border-radius: 12px; }
.stTabs [aria-selected="true"] { background: linear-gradient(135deg, #4f9eff22, #a78bfa22) !important; color: #4f9eff !important; }
[data-testid="stFileUploader"] { background: rgba(79,158,255,0.04) !important; border: 1.5px dashed rgba(79,158,255,0.3) !important; border-radius: 14px !important; }
textarea, input[type="text"] { background: #161b27 !important; border: 1px solid rgba(99,179,255,0.2) !important; border-radius: 10px !important; color: #e8edf5 !important; }
.chat-ai   { background: #161b27; border-radius: 12px; padding: 12px 16px; margin: 6px 0; border-left: 3px solid #4f9eff; color: #e8edf5; }
.chat-user { background: rgba(79,158,255,0.12); border-radius: 12px; padding: 12px 16px; margin: 6px 0; text-align: right; border-right: 3px solid #a78bfa; color: #e8edf5; }
.metric-chip { display:inline-block; padding:4px 12px; border-radius:99px; font-size:12px; font-weight:600; margin:3px; }
.chip-green { background:rgba(52,211,153,0.12); color:#34d399; border:1px solid rgba(52,211,153,0.3); }
.chip-red   { background:rgba(248,113,113,0.12); color:#f87171; border:1px solid rgba(248,113,113,0.3); }
.chip-blue  { background:rgba(79,158,255,0.10); color:#4f9eff;  border:1px solid rgba(79,158,255,0.25); }
.feature-card { background: #0d1117; border: 1px solid rgba(99,179,255,0.12); border-radius: 16px; padding: 20px; margin: 8px 0; }
</style>
""", unsafe_allow_html=True)

# ── Session State ─────────────────────────────────────────────────────────────
def _init_state():
    defaults = {
        "resume_text":          "",
        "jd_text":              "",
        "ats_report":           None,
        "contact_info":         {},
        "sections":             {},
        "resume_skills":        [],
        "jd_skills":            [],
        "chat_history":         [],
        "analyzed":             False,
        "interview_questions":  [],
        "interview_answers":    [],
        "current_q":            0,
        "interview_role":       "",
        "applications":         [],
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

_init_state()

# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='padding:8px 0 16px'>
      <div style='font-family:"Playfair Display",serif;font-size:1.5rem;
                  background:linear-gradient(90deg,#e8edf5,#4f9eff);
                  -webkit-background-clip:text;-webkit-text-fill-color:transparent;
                  font-weight:700'>🧠 ResumeIQ</div>
      <div style='font-size:10px;letter-spacing:2px;color:#6b7a99;text-transform:uppercase'>
        AI Career Intelligence</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    page = st.radio(
        "Navigation",
        [
            "⚡ Dashboard",
            "🎯 ATS Analysis",
            "🔧 Skill Gap",
            "💼 Career Match",
            "🗺️ Learning Roadmap",
            "📝 Resume Feedback",
            "🌐 Live Jobs",
            "💬 Resume Chatbot",
            "🏗️ Resume Builder",
            "🎤 Mock Interview",
            "💰 Salary Estimator",
            "🔗 LinkedIn Optimizer",
            "⚡ Real-time Tailoring",
            "📊 Application Tracker",
        ],
    )

    st.markdown("---")
    st.markdown("**Upload Resume**")
    pdf_file = st.file_uploader("", type=["pdf"], label_visibility="collapsed")
    if pdf_file:
        raw_bytes = pdf_file.read()
        text = clean_text(extract_text_from_pdf(raw_bytes))
        st.session_state.resume_text   = text
        st.session_state.sections      = detect_sections(text)
        st.session_state.contact_info  = extract_contact_info(text)
        st.session_state.resume_skills = extract_skills_from_text(text)
        st.success(f"✅ {pdf_file.name}")

    st.markdown("**Job Description**")
    jd = st.text_area("", placeholder="Paste the target JD here…",
                      height=100, label_visibility="collapsed", key="jd_input")
    if jd:
        st.session_state.jd_text   = jd
        st.session_state.jd_skills = extract_skills_from_text(jd)

    if st.button("⚡ Analyze Now", use_container_width=True):
        if not st.session_state.resume_text:
            st.error("Please upload a resume first.")
        else:
            with st.spinner("Analyzing your resume…"):
                st.session_state.ats_report = full_ats_report(
                    st.session_state.resume_text,
                    st.session_state.jd_text or "general tech role",
                    st.session_state.sections,
                )
                st.session_state.analyzed = True
            st.success("Analysis complete!")

def need_analysis():
    st.info("⬆️ Upload your resume and click **Analyze Now** to get started.")


# ══════════════════════════════════════════════════════════════════════════════
# DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════
if page == "⚡ Dashboard":
    st.markdown("### Career Intelligence Dashboard")

    if not st.session_state.analyzed:
        need_analysis()
        st.markdown("---")
        st.markdown("#### 🚀 What ResumeIQ can do for you")
        cols = st.columns(4)
        feats = [
            ("🎯", "ATS Scoring",      "Know exactly why ATS rejects your resume"),
            ("🔧", "Skill Gap",        "See what skills you're missing"),
            ("🎤", "Mock Interview",   "AI interviews you and gives feedback"),
            ("💰", "Salary Estimator", "Know your market worth in India"),
        ]
        for col, (icon, title, desc) in zip(cols, feats):
            col.markdown(f"**{icon} {title}**\n\n{desc}")
    else:
        r   = st.session_state.ats_report
        gap = r["skills"]

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("🎯 ATS Score",      f"{r['overall']}%",   "vs 60% avg")
        c2.metric("🔧 Skills Matched",  f"{len(gap['matched'])}/{len(gap['matched'])+len(gap['missing'])}")
        c3.metric("📊 Keyword Match",   f"{r['keyword']['score']}%")
        c4.metric("💪 Impact Score",    f"{r['impact']['score']}%")

        st.markdown("---")
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### 🎯 ATS Breakdown")
            cats = ["Keywords","Format","Sections","Impact","Skills"]
            vals = [r["keyword"]["score"], r["format"]["score"],
                    r["sections"]["score"], r["impact"]["score"], gap["score_pct"]]
            fig = go.Figure(go.Bar(
                x=vals, y=cats, orientation="h",
                marker=dict(color=["#4f9eff","#a78bfa","#34d399","#f5c842","#4f9eff"]),
                text=[f"{v}%" for v in vals], textposition="outside",
            ))
            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#e8edf5", size=12),
                margin=dict(l=10,r=40,t=10,b=10),
                xaxis=dict(range=[0,115], showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(showgrid=False), height=220,
            )
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.markdown("#### 🔧 Skill Match")
            fig2 = go.Figure(go.Pie(
                labels=["Matched","Missing"],
                values=[len(gap["matched"]), max(len(gap["missing"]),1)],
                hole=0.7,
                marker=dict(colors=["#34d399","#f87171"]),
                textinfo="none",
            ))
            fig2.add_annotation(
                text=f"{gap['score_pct']}%",
                x=0.5, y=0.5, showarrow=False,
                font=dict(size=28, color="#e8edf5"),
            )
            fig2.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                showlegend=True, height=220,
                font=dict(color="#e8edf5"),
                margin=dict(l=10,r=10,t=10,b=10),
                legend=dict(orientation="h", y=-0.1),
            )
            st.plotly_chart(fig2, use_container_width=True)

        if r["recommendations"]:
            st.markdown("#### ⚡ Top Recommendations")
            for rec in r["recommendations"]:
                st.markdown(f"- {rec}")


# ══════════════════════════════════════════════════════════════════════════════
# ATS ANALYSIS
# ══════════════════════════════════════════════════════════════════════════════
elif page == "🎯 ATS Analysis":
    st.markdown("### ATS Analysis")
    if not st.session_state.analyzed:
        need_analysis()
    else:
        r = st.session_state.ats_report
        c1,c2,c3,c4,c5 = st.columns(5)
        c1.metric("Overall",  f"{r['overall']}%")
        c2.metric("Keywords", f"{r['keyword']['score']}%")
        c3.metric("Format",   f"{r['format']['score']}%")
        c4.metric("Sections", f"{r['sections']['score']}%")
        c5.metric("Impact",   f"{r['impact']['score']}%")
        st.markdown("---")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("#### ✅ What's Working")
            for s in r["sections"]["present"]:
                st.markdown(f"✅ **{s.title()}** section detected")
            if r["impact"]["has_metrics"]:
                st.markdown("✅ Quantified achievements found")
            if r["impact"]["action_verbs"]:
                st.markdown(f"✅ Action verbs: {', '.join(r['impact']['action_verbs'][:6])}")
        with col2:
            st.markdown("#### ❌ Issues Found")
            for issue in r["format"]["issues"]:
                st.markdown(f"⚠️ {issue}")
            for missing in r["sections"]["missing"]:
                st.markdown(f"❌ Missing: **{missing.title()}**")
        st.markdown("---")
        if st.button("🤖 Get AI Feedback"):
            with st.spinner("Gemini is reviewing…"):
                feedback = get_ats_feedback(
                    st.session_state.resume_text,
                    st.session_state.jd_text,
                    r["overall"],
                )
            st.markdown(feedback)


# ══════════════════════════════════════════════════════════════════════════════
# SKILL GAP
# ══════════════════════════════════════════════════════════════════════════════
elif page == "🔧 Skill Gap":
    st.markdown("### Skill Gap Analysis")
    if not st.session_state.resume_skills:
        need_analysis()
    else:
        gap = compute_skill_gap(
            st.session_state.resume_skills,
            st.session_state.jd_skills
        ) if st.session_state.jd_skills else {
            "matched": st.session_state.resume_skills,
            "missing": [], "extra": [], "score_pct": 100
        }
        c1,c2,c3 = st.columns(3)
        c1.metric("Matched",   len(gap["matched"]))
        c2.metric("Missing",   len(gap["missing"]))
        c3.metric("Match Rate",f"{gap['score_pct']}%")
        st.markdown("---")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("#### ✅ Your Skills")
            grouped = group_skills_by_category(st.session_state.resume_skills)
            for cat, skills in grouped.items():
                st.markdown(f"**{cat}**")
                chips = " ".join(f'<span class="metric-chip chip-green">{s}</span>' for s in skills)
                st.markdown(chips, unsafe_allow_html=True)
                st.markdown("")
        with col2:
            st.markdown("#### ❌ Missing Skills" if gap["missing"] else "#### 🎉 No Gaps!")
            if gap["missing"]:
                for s in gap["missing"]:
                    st.markdown(f'<span class="metric-chip chip-red">{s}</span>', unsafe_allow_html=True)
            else:
                st.success("Your skills fully cover the JD!")


# ══════════════════════════════════════════════════════════════════════════════
# CAREER MATCH
# ══════════════════════════════════════════════════════════════════════════════
elif page == "💼 Career Match":
    st.markdown("### Career Match")
    if not st.session_state.resume_text:
        need_analysis()
    else:
        if st.button("🤖 Generate Career Recommendations"):
            with st.spinner("Analyzing your career potential…"):
                recs = recommend_career_paths(
                    st.session_state.resume_text,
                    st.session_state.resume_skills,
                )
            st.markdown(recs)


# ══════════════════════════════════════════════════════════════════════════════
# LEARNING ROADMAP
# ══════════════════════════════════════════════════════════════════════════════
elif page == "🗺️ Learning Roadmap":
    st.markdown("### Learning Roadmap")
    target_role = st.text_input("Target Role", placeholder="e.g. Senior ML Engineer")
    missing = st.session_state.ats_report["skills"]["missing"] if st.session_state.ats_report else []
    if st.button("🗺️ Generate Roadmap"):
        if not target_role:
            st.warning("Please enter your target role.")
        else:
            with st.spinner("Building your roadmap…"):
                roadmap = generate_roadmap(missing, target_role)
            st.markdown(roadmap)


# ══════════════════════════════════════════════════════════════════════════════
# RESUME FEEDBACK
# ══════════════════════════════════════════════════════════════════════════════
elif page == "📝 Resume Feedback":
    st.markdown("### Resume Feedback")
    if not st.session_state.resume_text:
        need_analysis()
    else:
        tab1, tab2, tab3 = st.tabs(["✍️ Rewrite Summary", "💪 Improve Bullets", "📄 Cover Letter"])

        with tab1:
            if st.button("✨ Rewrite My Summary"):
                with st.spinner("Writing…"):
                    s = rewrite_summary(st.session_state.resume_text, st.session_state.jd_text)
                st.success(s)

        with tab2:
            role    = st.text_input("Target role", placeholder="Senior ML Engineer")
            bullets = st.text_area("Paste your bullets", height=150)
            if st.button("💪 Improve Bullets"):
                if bullets and role:
                    with st.spinner("Rewriting…"):
                        improved = improve_bullet_points(bullets, role)
                    st.success(improved)

        with tab3:
            col1, col2 = st.columns(2)
            company = col1.text_input("Company", placeholder="Google")
            role    = col2.text_input("Role",    placeholder="ML Engineer")
            if st.button("📄 Generate Cover Letter"):
                if company and role:
                    with st.spinner("Writing…"):
                        letter = generate_cover_letter(
                            st.session_state.resume_text,
                            st.session_state.jd_text,
                            company, role,
                        )
                    st.markdown(letter)
                    st.download_button("📥 Download", letter, file_name="cover_letter.txt")


# ══════════════════════════════════════════════════════════════════════════════
# LIVE JOBS
# ══════════════════════════════════════════════════════════════════════════════
elif page == "🌐 Live Jobs":
    st.markdown("### Live Jobs")
    col1, col2, col3 = st.columns([2,1,1])
    query    = col1.text_input("Search", placeholder="ML Engineer", label_visibility="collapsed")
    location = col2.text_input("Location", value="Remote",          label_visibility="collapsed")
    search   = col3.button("🔍 Search", use_container_width=True)

    if search or not query:
        q = query or "machine learning engineer"
        with st.spinner("Fetching jobs…"):
            jobs = search_jobs(q, location)
        for job in jobs:
            col1, col2 = st.columns([4,1])
            with col1:
                st.markdown(f"**{job['title']}** — {job['company']}")
                st.caption(f"📍 {job['location']}  |  💰 {job['salary']}  |  ⏰ {job['posted']}")
            with col2:
                if job.get("url") and job["url"] != "#":
                    st.link_button("Apply →", job["url"])
            st.markdown("---")


# ══════════════════════════════════════════════════════════════════════════════
# RESUME CHATBOT
# ══════════════════════════════════════════════════════════════════════════════
elif page == "💬 Resume Chatbot":
    st.markdown("### AI Resume Coach")
    if not st.session_state.resume_text:
        need_analysis()
    else:
        for msg in st.session_state.chat_history:
            if msg["role"] == "user":
                st.markdown(f'<div class="chat-user">👤 {msg["content"]}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="chat-ai">🧠 {msg["content"]}</div>', unsafe_allow_html=True)

        user_msg = st.chat_input("Ask me anything about your resume…")
        if user_msg:
            st.session_state.chat_history.append({"role": "user", "content": user_msg})
            with st.spinner("Thinking…"):
                ats_score = st.session_state.ats_report["overall"] if st.session_state.ats_report else 0
                reply = chat_with_resume(
                    user_msg,
                    st.session_state.resume_text,
                    st.session_state.jd_text,
                    st.session_state.chat_history[:-1],
                    ats_score,
                )
            st.session_state.chat_history.append({"role": "assistant", "content": reply})
            st.rerun()

        if st.button("🗑️ Clear Chat"):
            st.session_state.chat_history = []
            st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# RESUME BUILDER
# ══════════════════════════════════════════════════════════════════════════════
elif page == "🏗️ Resume Builder":
    st.markdown("### Resume Builder")
    tab1, tab2, tab3, tab4 = st.tabs(["👤 Personal", "💼 Experience", "🎓 Education & Skills", "📥 Export"])

    with tab1:
        col1, col2 = st.columns(2)
        name     = col1.text_input("Full Name",    key="b_name",  placeholder="Jane Smith")
        title    = col2.text_input("Job Title",    key="b_title", placeholder="ML Engineer")
        email    = col1.text_input("Email",        key="b_email", placeholder="jane@email.com")
        phone    = col2.text_input("Phone",        key="b_phone", placeholder="+91 9876543210")
        linkedin = col1.text_input("LinkedIn",     key="b_li",    placeholder="janesmith")
        github   = col2.text_input("GitHub",       key="b_gh",    placeholder="janesmith")
        location = st.text_input("Location",       key="b_loc",   placeholder="Pune, India")
        summary  = st.text_area("Summary",         key="b_sum",   height=100,
                                placeholder="2-3 sentences about your expertise…")

    with tab2:
        exp_entries = []
        n_exp = st.number_input("Number of positions", 1, 6, 2, key="n_exp")
        for i in range(int(n_exp)):
            with st.expander(f"Position {i+1}", expanded=(i==0)):
                role     = st.text_input("Role",     key=f"e_role_{i}", placeholder="ML Engineer")
                company  = st.text_input("Company",  key=f"e_comp_{i}", placeholder="Google")
                duration = st.text_input("Duration", key=f"e_dur_{i}",  placeholder="Jan 2022 – Present")
                bullets  = st.text_area("Achievements", key=f"e_bul_{i}", height=100,
                                        placeholder="• Reduced latency by 40%")
                exp_entries.append({
                    "role": role, "company": company, "duration": duration,
                    "bullets": [b.lstrip("•- ").strip() for b in bullets.splitlines() if b.strip()]
                })

    with tab3:
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("#### Education")
            edu_entries = []
            n_edu = st.number_input("Degrees", 1, 4, 1, key="n_edu")
            for i in range(int(n_edu)):
                degree = st.text_input("Degree", key=f"d_deg_{i}", placeholder="B.Tech CS")
                school = st.text_input("School", key=f"d_sch_{i}", placeholder="IIT Bombay")
                year   = st.text_input("Year",   key=f"d_yr_{i}",  placeholder="2021")
                gpa    = st.text_input("GPA",    key=f"d_gpa_{i}", placeholder="8.9/10")
                edu_entries.append({"degree": degree, "school": school, "year": year, "gpa": gpa})
        with col2:
            st.markdown("#### Skills")
            skills_raw = st.text_area("Skills (comma separated)", key="b_skills", height=100,
                                      placeholder="Python, TensorFlow, Docker…")
            st.markdown("#### Certifications")
            certs_raw = st.text_area("Certifications", key="b_certs", height=80,
                                     placeholder="AWS ML Specialty\nGoogle Cloud")

    with tab4:
        if st.button("📥 Generate & Download PDF", use_container_width=True):
            data = {
                "name":     st.session_state.get("b_name",""),
                "title":    st.session_state.get("b_title",""),
                "email":    st.session_state.get("b_email",""),
                "phone":    st.session_state.get("b_phone",""),
                "linkedin": st.session_state.get("b_li",""),
                "github":   st.session_state.get("b_gh",""),
                "location": st.session_state.get("b_loc",""),
                "summary":  st.session_state.get("b_sum",""),
                "experience": exp_entries,
                "education":  edu_entries,
                "skills": [s.strip() for s in st.session_state.get("b_skills","").split(",") if s.strip()],
                "certifications": [c.strip() for c in st.session_state.get("b_certs","").splitlines() if c.strip()],
            }
            with st.spinner("Building PDF…"):
                pdf_bytes = build_resume_pdf(data)
            st.download_button(
                "📄 Download Resume PDF",
                data=pdf_bytes,
                file_name="My_Resume.pdf",
                mime="application/pdf",
                use_container_width=True,
            )


# ══════════════════════════════════════════════════════════════════════════════
# MOCK INTERVIEW AI  (NEW)
# ══════════════════════════════════════════════════════════════════════════════
elif page == "🎤 Mock Interview":
    st.markdown("### Mock Interview AI")
    st.markdown("AI tumhara interview lega aur har answer pe **detailed feedback** dega! 🎯")

    if not st.session_state.resume_text:
        need_analysis()
    else:
        if not st.session_state.interview_questions:
            col1, col2, col3 = st.columns(3)
            role       = col1.text_input("Target Role", placeholder="Software Engineer at Google")
            difficulty = col2.select_slider("Difficulty", ["Easy", "Medium", "Hard"], value="Medium")
            q_type     = col3.selectbox("Question Type", ["Mixed", "Technical", "Behavioral", "HR"])

            if st.button("🎤 Start Interview", use_container_width=True):
                if not role:
                    st.warning("Role daalo pehle!")
                else:
                    with st.spinner("Interview questions generate ho rahe hain..."):
                        raw = generate_interview_questions(
                            st.session_state.resume_text,
                            st.session_state.jd_text,
                            role, difficulty
                        )
                        qs = [q.strip() for q in raw.split("\n") if q.strip() and q[0].isdigit()]
                        if not qs:
                            qs = [q.strip() for q in raw.split("\n") if q.strip()][:5]
                    st.session_state.interview_questions = qs[:5]
                    st.session_state.interview_answers   = [""] * len(qs[:5])
                    st.session_state.current_q           = 0
                    st.session_state.interview_role      = role
                    st.rerun()
        else:
            qs   = st.session_state.interview_questions
            curr = st.session_state.current_q
            role = st.session_state.interview_role

            # Progress bar
            st.progress((curr) / len(qs))
            st.markdown(f"**Question {curr+1} of {len(qs)}** — {role}")
            st.markdown("---")
            st.markdown(f"### 💬 {qs[curr]}")
            st.markdown("")

            answer = st.text_area(
                "Your Answer:",
                height=160,
                placeholder="Yahan apna jawab likho... (STAR format use karo: Situation, Task, Action, Result)",
                key=f"ans_{curr}"
            )

            col1, col2, col3 = st.columns(3)

            if col1.button("✅ Submit & Get Feedback"):
                if answer.strip():
                    with st.spinner("AI feedback aa raha hai..."):
                        feedback = get_interview_feedback(qs[curr], answer, role)
                    st.markdown("---")
                    st.markdown("#### 🧠 AI Feedback:")
                    st.info(feedback)
                    st.session_state.interview_answers[curr] = answer
                else:
                    st.warning("Pehle answer likho!")

            if col2.button("⏭️ Next Question"):
                if curr < len(qs) - 1:
                    st.session_state.current_q += 1
                    st.rerun()
                else:
                    st.warning("Ye last question hai! Finish karo.")

            if col3.button("🏁 Finish Interview"):
                st.balloons()
                st.success("🎉 Interview complete! Bahut achha kiya bhai!")
                answered = sum(1 for a in st.session_state.interview_answers if a)
                st.metric("Questions Answered", f"{answered}/{len(qs)}")
                st.session_state.interview_questions = []
                st.session_state.current_q = 0
                st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# SALARY ESTIMATOR  (NEW)
# ══════════════════════════════════════════════════════════════════════════════
elif page == "💰 Salary Estimator":
    st.markdown("### Salary Estimator")
    st.markdown("Indian job market ke liye **realistic salary range** jaano! 💰")

    col1, col2 = st.columns(2)
    role       = col1.text_input("Target Role", placeholder="Software Engineer")
    city       = col2.text_input("City", placeholder="Bangalore / Mumbai / Remote / India")
    experience = st.slider("Years of Experience", 0, 20, 0)

    if st.button("💰 Estimate My Salary", use_container_width=True):
        if not role:
            st.warning("Role daalo pehle!")
        else:
            with st.spinner("Market data analyze ho raha hai..."):
                result = estimate_salary(
                    role, city, experience,
                    st.session_state.resume_skills
                )
            st.markdown("---")
            st.markdown(result)


# ══════════════════════════════════════════════════════════════════════════════
# LINKEDIN OPTIMIZER  (NEW)
# ══════════════════════════════════════════════════════════════════════════════
elif page == "🔗 LinkedIn Optimizer":
    st.markdown("### LinkedIn Profile Optimizer")
    st.markdown("AI tumhara **LinkedIn headline, About section aur skills** optimize karega! 🔗")

    if not st.session_state.resume_text:
        need_analysis()
    else:
        target_role = st.text_input(
            "Target Role for LinkedIn",
            placeholder="e.g. Machine Learning Engineer | Python Developer"
        )
        if st.button("🔗 Optimize My LinkedIn", use_container_width=True):
            if not target_role:
                st.warning("Target role daalo!")
            else:
                with st.spinner("LinkedIn content optimize ho raha hai..."):
                    result = optimize_linkedin(
                        st.session_state.resume_text,
                        target_role
                    )
                st.markdown("---")
                st.markdown(result)
                st.download_button(
                    "📥 Download LinkedIn Content",
                    data=result,
                    file_name="linkedin_optimized.txt",
                    mime="text/plain"
                )


# ══════════════════════════════════════════════════════════════════════════════
# REAL-TIME TAILORING  (NEW)
# ══════════════════════════════════════════════════════════════════════════════
elif page == "⚡ Real-time Tailoring":
    st.markdown("### Real-time Resume Tailoring")
    st.markdown("**1-click mein apna resume target JD ke liye tailor karo!** ⚡")

    if not st.session_state.resume_text:
        need_analysis()
    elif not st.session_state.jd_text:
        st.warning("⬅️ Pehle sidebar mein Job Description paste karo!")
    else:
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("#### 📄 Your Current Resume")
            st.text_area("", value=st.session_state.resume_text[:800] + "...",
                         height=200, disabled=True, label_visibility="collapsed")
        with col2:
            st.markdown("#### 📋 Target Job Description")
            st.text_area("", value=st.session_state.jd_text[:800] + "...",
                         height=200, disabled=True, label_visibility="collapsed")

        st.markdown("---")
        if st.button("⚡ Tailor My Resume Now", use_container_width=True):
            with st.spinner("AI tera resume tailor kar raha hai..."):
                result = realtime_resume_tailor(
                    st.session_state.resume_text,
                    st.session_state.jd_text
                )
            st.markdown("### ✅ Tailoring Results:")
            st.markdown(result)
            st.download_button(
                "📥 Download Tailoring Report",
                data=result,
                file_name="resume_tailoring_report.txt",
                mime="text/plain"
            )


# ══════════════════════════════════════════════════════════════════════════════
# APPLICATION TRACKER  (NEW)
# ══════════════════════════════════════════════════════════════════════════════
elif page == "📊 Application Tracker":
    st.markdown("### Application Tracker")
    st.markdown("Apni **sab job applications ek jagah** track karo! 📊")

    # Stats
    apps = st.session_state.applications
    if apps:
        df = pd.DataFrame(apps)
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("📨 Total Applied",  len(df))
        c2.metric("🎯 Interviews",     len(df[df.status.isin(["Interview Scheduled","Interview Done"])]))
        c3.metric("🎉 Offers",         len(df[df.status == "Offer Received"]))
        c4.metric("❌ Rejected",       len(df[df.status == "Rejected"]))
        st.markdown("---")

    # Add new application
    with st.expander("➕ New Application Add Karo", expanded=not apps):
        col1, col2 = st.columns(2)
        company  = col1.text_input("Company Name", placeholder="Google", key="app_co")
        role     = col2.text_input("Role Applied",  placeholder="Software Engineer", key="app_role")
        col3, col4 = st.columns(2)
        status   = col3.selectbox("Current Status", [
            "Applied", "Interview Scheduled", "Interview Done",
            "Offer Received", "Rejected", "Waitlisted"
        ], key="app_status")
        date     = col4.date_input("Applied Date", key="app_date")
        col5, col6 = st.columns(2)
        salary   = col5.text_input("Expected CTC", placeholder="12 LPA", key="app_sal")
        source   = col6.selectbox("Applied Via", ["LinkedIn", "Naukri", "Company Website", "Referral", "Other"], key="app_src")
        notes    = st.text_area("Notes", placeholder="HR name, next steps, follow-up date...", key="app_notes")

        if st.button("✅ Add Application", use_container_width=True):
            if company and role:
                st.session_state.applications.append({
                    "company": company, "role": role, "status": status,
                    "date": str(date), "salary": salary,
                    "source": source, "notes": notes
                })
                st.success(f"✅ {company} — {role} added!")
                st.rerun()

    # Display applications
    if apps:
        st.markdown("### 📋 All Applications")
        status_filter = st.selectbox("Filter by Status", ["All"] + ["Applied","Interview Scheduled","Interview Done","Offer Received","Rejected","Waitlisted"])

        filtered = apps if status_filter == "All" else [a for a in apps if a["status"] == status_filter]

        for i, app in enumerate(filtered):
            with st.container():
                col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
                col1.markdown(f"**{app['company']}** — {app['role']}")
                col2.markdown(f"📅 {app['date']}")
                status_colors = {
                    "Applied": "🔵", "Interview Scheduled": "🟡",
                    "Interview Done": "🟠", "Offer Received": "🟢",
                    "Rejected": "🔴", "Waitlisted": "⚪"
                }
                col3.markdown(f"{status_colors.get(app['status'],'⚪')} {app['status']}")
                if col4.button("🗑️", key=f"del_{i}"):
                    idx = st.session_state.applications.index(app)
                    st.session_state.applications.pop(idx)
                    st.rerun()
                if app.get("notes"):
                    st.caption(f"📝 {app['notes']}")
                st.markdown("---")

        # Export
        if st.button("📥 Export as CSV"):
            csv = pd.DataFrame(apps).to_csv(index=False)
            st.download_button(
                "📥 Download CSV",
                data=csv,
                file_name="job_applications.csv",
                mime="text/csv"
            )
