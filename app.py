"""
app.py  ─  ResumeIQ | AI Career Intelligence Platform
───────────────────────────────────────────────────────
Run with:   streamlit run app.py
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px

from resume_parser   import extract_text_from_pdf, detect_sections, extract_contact_info, clean_text
from skill_extractor import extract_skills_from_text, compute_skill_gap, group_skills_by_category
from ats_analyzer    import full_ats_report
from ai_resume_coach import (
    get_ats_feedback, rewrite_summary, generate_roadmap,
    improve_bullet_points, generate_cover_letter,
    generate_interview_questions, chat_with_resume, recommend_career_paths,
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

# ── Custom CSS (dark premium theme) ──────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;900&family=DM+Sans:wght@300;400;500;600&display=swap');

:root {
    --bg: #050810; --surface: #0d1117; --surface2: #161b27;
    --accent: #4f9eff; --accent2: #a78bfa; --accent3: #34d399;
    --gold: #f5c842; --danger: #f87171; --text: #e8edf5; --muted: #6b7a99;
}

html, body, [class*="css"] { font-family: 'DM Sans', sans-serif !important; }
.stApp { background: var(--bg) !important; }
section[data-testid="stSidebar"] { background: #0d1117 !important; border-right: 1px solid rgba(99,179,255,0.12); }
section[data-testid="stSidebar"] * { color: #e8edf5 !important; }
.block-container { padding-top: 1.5rem !important; }

/* Metric cards */
[data-testid="stMetric"] {
    background: #0d1117;
    border: 1px solid rgba(99,179,255,0.12);
    border-radius: 16px;
    padding: 1rem 1.2rem;
}
[data-testid="stMetricValue"] { font-family: 'Playfair Display', serif !important; font-size: 2.2rem !important; color: #4f9eff !important; }
[data-testid="stMetricDelta"] { font-size: 0.75rem !important; }

/* Buttons */
.stButton > button {
    background: linear-gradient(135deg, #4f9eff, #a78bfa) !important;
    border: none !important; color: white !important;
    border-radius: 10px !important; font-weight: 600 !important;
    font-family: 'DM Sans', sans-serif !important;
    transition: all 0.2s !important;
}
.stButton > button:hover { opacity: 0.88 !important; transform: translateY(-1px) !important; }

/* Tabs */
.stTabs [data-baseweb="tab-list"] { background: #0d1117 !important; border-radius: 12px; gap: 4px; }
.stTabs [data-baseweb="tab"] { border-radius: 10px !important; color: #6b7a99 !important; }
.stTabs [aria-selected="true"] { background: linear-gradient(135deg, #4f9eff22, #a78bfa22) !important; color: #4f9eff !important; }

/* File uploader */
[data-testid="stFileUploader"] {
    background: rgba(79,158,255,0.04) !important;
    border: 1.5px dashed rgba(79,158,255,0.3) !important;
    border-radius: 14px !important;
}

/* Text areas & inputs */
textarea, input[type="text"] {
    background: #161b27 !important;
    border: 1px solid rgba(99,179,255,0.2) !important;
    border-radius: 10px !important;
    color: #e8edf5 !important;
}

/* Chat messages */
.chat-ai   { background: #161b27; border-radius: 12px; padding: 12px 16px; margin: 6px 0; border-left: 3px solid #4f9eff; }
.chat-user { background: rgba(79,158,255,0.12); border-radius: 12px; padding: 12px 16px; margin: 6px 0; text-align: right; border-right: 3px solid #a78bfa; }
.metric-chip { display:inline-block; padding:4px 12px; border-radius:99px; font-size:12px; font-weight:600; margin:3px; }
.chip-green  { background:rgba(52,211,153,0.12); color:#34d399; border:1px solid rgba(52,211,153,0.3); }
.chip-red    { background:rgba(248,113,113,0.12); color:#f87171; border:1px solid rgba(248,113,113,0.3); }
.chip-blue   { background:rgba(79,158,255,0.10); color:#4f9eff;  border:1px solid rgba(79,158,255,0.25); }
.section-title { font-family:'Playfair Display',serif; font-size:1.4rem; color:#e8edf5; margin-bottom:0.5rem; }
.muted { color:#6b7a99; font-size:0.85rem; }
</style>
""", unsafe_allow_html=True)


# ── Session State ─────────────────────────────────────────────────────────────
def _init_state():
    defaults = {
        "resume_text":    "",
        "jd_text":        "",
        "ats_report":     None,
        "contact_info":   {},
        "sections":       {},
        "resume_skills":  [],
        "jd_skills":      [],
        "chat_history":   [],
        "analyzed":       False,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

_init_state()


# ────────────────────────────────────────────────────────────────────────────
#  SIDEBAR
# ────────────────────────────────────────────────────────────────────────────
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

    # Navigation
    page = st.radio(
        "Navigation",
        ["⚡ Dashboard", "🎯 ATS Analysis", "🔧 Skill Gap",
         "💼 Career Match", "🗺️ Learning Roadmap", "📝 Resume Feedback",
         "🌐 Live Jobs", "💬 Resume Chatbot", "🏗️ Resume Builder"],
        label_visibility="visible",
    )

    st.markdown("---")

    # Upload
    st.markdown("**Upload Resume**")
    pdf_file = st.file_uploader("", type=["pdf"], label_visibility="collapsed")
    if pdf_file:
        raw_bytes = pdf_file.read()
        text = clean_text(extract_text_from_pdf(raw_bytes))
        st.session_state.resume_text  = text
        st.session_state.sections     = detect_sections(text)
        st.session_state.contact_info = extract_contact_info(text)
        st.session_state.resume_skills = extract_skills_from_text(text)
        st.success(f"✅ {pdf_file.name}")

    st.markdown("**Job Description**")
    jd = st.text_area("", placeholder="Paste the target JD here…",
                       height=120, label_visibility="collapsed",
                       key="jd_input")
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


# ── Helper: require analysis ───────────────────────────────────────────────────
def need_analysis():
    st.info("⬆️ Upload your resume and click **Analyze Now** to get started.")


# ────────────────────────────────────────────────────────────────────────────
#  PAGES
# ────────────────────────────────────────────────────────────────────────────

# ── DASHBOARD ────────────────────────────────────────────────────────────────
if page == "⚡ Dashboard":
    st.markdown('<div class="section-title">Career Intelligence Dashboard</div>', unsafe_allow_html=True)

    if not st.session_state.analyzed:
        need_analysis()
        # Show feature preview
        st.markdown("---")
        st.markdown("#### 🚀 What ResumeIQ can do for you")
        cols = st.columns(4)
        feats = [
            ("🎯", "ATS Scoring", "Know exactly why ATS rejects your resume"),
            ("🔧", "Skill Gap Analysis", "See what skills you're missing for your dream job"),
            ("🗺️", "Learning Roadmap", "Get a 3-month plan to close every skill gap"),
            ("💬", "AI Coach", "Chat with an AI that knows your resume inside-out"),
        ]
        for col, (icon, title, desc) in zip(cols, feats):
            col.markdown(f"**{icon} {title}**\n\n{desc}")
    else:
        r = st.session_state.ats_report
        gap = r["skills"]

        # Score cards
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("🎯 ATS Score",     f"{r['overall']}%",   "vs 60% avg")
        c2.metric("🔧 Skills Matched", f"{len(gap['matched'])}/{len(gap['matched'])+len(gap['missing'])}", "keyword match")
        c3.metric("📊 Keyword Match",  f"{r['keyword']['score']}%", "")
        c4.metric("💪 Impact Score",   f"{r['impact']['score']}%",  "")

        st.markdown("---")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### 🎯 ATS Breakdown")
            cats = ["Keywords", "Format", "Sections", "Impact", "Skills"]
            vals = [r["keyword"]["score"], r["format"]["score"],
                    r["sections"]["score"], r["impact"]["score"], gap["score_pct"]]
            fig = go.Figure(go.Bar(
                x=vals, y=cats, orientation="h",
                marker=dict(color=["#4f9eff","#a78bfa","#34d399","#f5c842","#4f9eff"],
                            line=dict(width=0)),
                text=[f"{v}%" for v in vals], textposition="outside",
            ))
            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#e8edf5", size=12), margin=dict(l=10,r=30,t=10,b=10),
                xaxis=dict(range=[0, 115], showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(showgrid=False), height=220,
            )
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.markdown("#### 🔧 Skill Match")
            fig2 = go.Figure(go.Pie(
                labels=["Matched", "Missing"],
                values=[len(gap["matched"]), max(len(gap["missing"]), 1)],
                hole=0.7,
                marker=dict(colors=["#34d399", "#f87171"]),
                textinfo="none",
            ))
            fig2.add_annotation(
                text=f"{gap['score_pct']}%",
                x=0.5, y=0.5, showarrow=False,
                font=dict(size=28, color="#e8edf5", family="Playfair Display"),
            )
            fig2.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                showlegend=True, height=220,
                font=dict(color="#e8edf5"),
                margin=dict(l=10,r=10,t=10,b=10),
                legend=dict(orientation="h", y=-0.1),
            )
            st.plotly_chart(fig2, use_container_width=True)

        # Recommendations
        if r["recommendations"]:
            st.markdown("#### ⚡ Top Recommendations")
            for rec in r["recommendations"]:
                st.markdown(f"- {rec}")


# ── ATS ANALYSIS ─────────────────────────────────────────────────────────────
elif page == "🎯 ATS Analysis":
    st.markdown('<div class="section-title">ATS Analysis</div>', unsafe_allow_html=True)

    if not st.session_state.analyzed:
        need_analysis()
    else:
        r = st.session_state.ats_report

        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("Overall",   f"{r['overall']}%")
        c2.metric("Keywords",  f"{r['keyword']['score']}%")
        c3.metric("Format",    f"{r['format']['score']}%")
        c4.metric("Sections",  f"{r['sections']['score']}%")
        c5.metric("Impact",    f"{r['impact']['score']}%")

        st.markdown("---")
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### ✅ What's Working")
            if r["sections"]["present"]:
                for s in r["sections"]["present"]:
                    st.markdown(f"✅ **{s.title()}** section detected")
            if r["impact"]["has_metrics"]:
                st.markdown(f"✅ Quantified achievements found ({r['impact']['metrics_count']} numbers)")
            if r["impact"]["action_verbs"]:
                st.markdown(f"✅ Strong action verbs: {', '.join(r['impact']['action_verbs'][:6])}")

        with col2:
            st.markdown("#### ❌ Issues Found")
            for issue in r["format"]["issues"]:
                st.markdown(f"⚠️ {issue}")
            for missing in r["sections"]["missing"]:
                st.markdown(f"❌ Missing section: **{missing.title()}**")
            if not r["impact"]["has_metrics"]:
                st.markdown("❌ No quantified metrics found")

        st.markdown("---")
        if st.button("🤖 Get AI-Powered ATS Feedback"):
            with st.spinner("Claude is reviewing your resume…"):
                feedback = get_ats_feedback(
                    st.session_state.resume_text,
                    st.session_state.jd_text,
                    r["overall"],
                )
            st.markdown("#### 🧠 AI Feedback")
            st.markdown(feedback)


# ── SKILL GAP ────────────────────────────────────────────────────────────────
elif page == "🔧 Skill Gap":
    st.markdown('<div class="section-title">Skill Gap Analysis</div>', unsafe_allow_html=True)

    resume_skills = st.session_state.resume_skills
    jd_skills     = st.session_state.jd_skills

    if not resume_skills:
        need_analysis()
    else:
        gap = compute_skill_gap(resume_skills, jd_skills) if jd_skills else {
            "matched": resume_skills, "missing": [], "extra": [], "score_pct": 100
        }

        c1, c2, c3 = st.columns(3)
        c1.metric("Skills Matched", len(gap["matched"]))
        c2.metric("Skill Gaps",     len(gap["missing"]))
        c3.metric("Match Rate",     f"{gap['score_pct']}%")

        st.markdown("---")
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### ✅ Your Skills")
            grouped = group_skills_by_category(resume_skills)
            for cat, skills in grouped.items():
                st.markdown(f"**{cat}**")
                chips = " ".join(f'<span class="metric-chip chip-green">{s}</span>' for s in skills)
                st.markdown(chips, unsafe_allow_html=True)
                st.markdown("")

        with col2:
            st.markdown("#### ❌ Missing Skills" if gap["missing"] else "#### 🎉 No Skill Gaps!")
            if gap["missing"]:
                for s in gap["missing"]:
                    st.markdown(f'<span class="metric-chip chip-red">{s}</span>', unsafe_allow_html=True)
            else:
                st.success("Your skills fully cover the JD requirements!")


# ── CAREER MATCH ──────────────────────────────────────────────────────────────
elif page == "💼 Career Match":
    st.markdown('<div class="section-title">Career Match</div>', unsafe_allow_html=True)

    if not st.session_state.resume_text:
        need_analysis()
    else:
        if st.button("🤖 Generate Career Path Recommendations"):
            with st.spinner("Analyzing your career potential…"):
                recs = recommend_career_paths(
                    st.session_state.resume_text,
                    st.session_state.resume_skills,
                )
            st.markdown(recs)

        if st.session_state.analyzed:
            st.markdown("---")
            st.markdown("#### 📊 Skill Radar")
            cats   = list(group_skills_by_category(st.session_state.resume_skills).keys())
            counts = [len(v) for v in group_skills_by_category(st.session_state.resume_skills).values()]
            if cats:
                fig = go.Figure(go.Scatterpolar(
                    r=counts, theta=cats, fill="toself",
                    fillcolor="rgba(79,158,255,0.15)", line=dict(color="#4f9eff"),
                ))
                fig.update_layout(
                    polar=dict(bgcolor="rgba(0,0,0,0)",
                               radialaxis=dict(visible=True, color="#6b7a99"),
                               angularaxis=dict(color="#6b7a99")),
                    paper_bgcolor="rgba(0,0,0,0)", font=dict(color="#e8edf5"),
                    margin=dict(l=40,r=40,t=40,b=40), height=350,
                )
                st.plotly_chart(fig, use_container_width=True)


# ── LEARNING ROADMAP ──────────────────────────────────────────────────────────
elif page == "🗺️ Learning Roadmap":
    st.markdown('<div class="section-title">Learning Roadmap</div>', unsafe_allow_html=True)

    target_role = st.text_input("Target Role", placeholder="e.g. Senior ML Engineer at Google")
    missing = st.session_state.ats_report["skills"]["missing"] if st.session_state.ats_report else []

    if missing:
        st.markdown(f"**Skill gaps identified:** " + ", ".join(
            f'<span class="metric-chip chip-red">{s}</span>' for s in missing
        ), unsafe_allow_html=True)

    if st.button("🗺️ Generate My Learning Roadmap"):
        if not target_role:
            st.warning("Please enter your target role.")
        else:
            with st.spinner("Building your personalized roadmap…"):
                roadmap = generate_roadmap(missing, target_role)
            st.markdown("---")
            st.markdown(roadmap)


# ── RESUME FEEDBACK ───────────────────────────────────────────────────────────
elif page == "📝 Resume Feedback":
    st.markdown('<div class="section-title">Resume Feedback</div>', unsafe_allow_html=True)

    if not st.session_state.resume_text:
        need_analysis()
    else:
        tab1, tab2, tab3 = st.tabs(["✍️ Rewrite Summary", "💪 Improve Bullets", "📄 Cover Letter"])

        with tab1:
            st.markdown("#### AI-Powered Summary Rewrite")
            if st.button("✨ Rewrite My Summary"):
                with st.spinner("Crafting your new summary…"):
                    new_summary = rewrite_summary(
                        st.session_state.resume_text,
                        st.session_state.jd_text,
                    )
                st.markdown("**Suggested Summary:**")
                st.success(new_summary)

        with tab2:
            st.markdown("#### Bullet Point Enhancer")
            role = st.text_input("Target role", key="bp_role", placeholder="Senior ML Engineer")
            bullets = st.text_area("Paste your current bullet points", height=150,
                                   placeholder="• Responsible for building ML models\n• Worked on data pipelines")
            if st.button("💪 Improve Bullets"):
                if bullets and role:
                    with st.spinner("Rewriting with impact…"):
                        improved = improve_bullet_points(bullets, role)
                    st.markdown("**Improved Bullets:**")
                    st.success(improved)

        with tab3:
            st.markdown("#### Cover Letter Generator")
            col1, col2 = st.columns(2)
            company = col1.text_input("Company Name", placeholder="Google")
            role    = col2.text_input("Role",         placeholder="Senior ML Engineer")
            if st.button("📄 Generate Cover Letter"):
                if company and role:
                    with st.spinner("Writing your cover letter…"):
                        letter = generate_cover_letter(
                            st.session_state.resume_text,
                            st.session_state.jd_text,
                            company, role,
                        )
                    st.markdown("**Cover Letter:**")
                    st.markdown(letter)
                    st.download_button("📥 Download", letter, file_name="cover_letter.txt")


# ── LIVE JOBS ─────────────────────────────────────────────────────────────────
elif page == "🌐 Live Jobs":
    st.markdown('<div class="section-title">Live Job Listings</div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns([2, 1, 1])
    query    = col1.text_input("Search", placeholder="Machine Learning Engineer", label_visibility="collapsed")
    location = col2.text_input("Location", value="Remote", label_visibility="collapsed")
    search   = col3.button("🔍 Search Jobs", use_container_width=True)

    if search or not query:
        q = query or "machine learning engineer"
        with st.spinner("Fetching live listings…"):
            jobs = search_jobs(q, location)

        st.markdown(f"**{len(jobs)} roles found**")
        for job in jobs:
            with st.container():
                c1, c2 = st.columns([4, 1])
                with c1:
                    st.markdown(f"**{job['title']}** — {job['company']}")
                    st.markdown(f'<span class="muted">📍 {job["location"]} &nbsp;|&nbsp; 💰 {job["salary"]} &nbsp;|&nbsp; ⏰ {job["posted"]}</span>', unsafe_allow_html=True)
                    if job.get("description"):
                        st.caption(job["description"][:180] + "…")
                with c2:
                    if job.get("url") and job["url"] != "#":
                        st.link_button("Apply →", job["url"])
                    remote_tag = "🟢 Remote" if job.get("remote") else "🔵 On-site"
                    st.caption(remote_tag)
                st.markdown("---")


# ── RESUME CHATBOT ────────────────────────────────────────────────────────────
elif page == "💬 Resume Chatbot":
    st.markdown('<div class="section-title">AI Resume Coach</div>', unsafe_allow_html=True)

    if not st.session_state.resume_text:
        need_analysis()
    else:
        # Display chat history
        for msg in st.session_state.chat_history:
            if msg["role"] == "user":
                st.markdown(f'<div class="chat-user">👤 {msg["content"]}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="chat-ai">🧠 {msg["content"]}</div>', unsafe_allow_html=True)

        # Input
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

        # Quick prompts
        st.markdown("**Quick prompts:**")
        prompts = ["How do I improve my ATS score?", "What skills should I learn next?",
                   "Rewrite my professional summary", "What jobs am I best suited for?"]
        cols = st.columns(4)
        for col, prompt in zip(cols, prompts):
            if col.button(prompt, use_container_width=True):
                st.session_state.chat_history.append({"role": "user", "content": prompt})
                ats_score = st.session_state.ats_report["overall"] if st.session_state.ats_report else 0
                with st.spinner("Thinking…"):
                    reply = chat_with_resume(
                        prompt,
                        st.session_state.resume_text,
                        st.session_state.jd_text,
                        st.session_state.chat_history[:-1],
                        ats_score,
                    )
                st.session_state.chat_history.append({"role": "assistant", "content": reply})
                st.rerun()


# ── RESUME BUILDER ────────────────────────────────────────────────────────────
elif page == "🏗️ Resume Builder":
    st.markdown('<div class="section-title">Resume Builder</div>', unsafe_allow_html=True)

    tab1, tab2, tab3, tab4 = st.tabs(["👤 Personal", "💼 Experience", "🎓 Education & Skills", "📥 Export"])

    with tab1:
        col1, col2 = st.columns(2)
        name     = col1.text_input("Full Name",      key="b_name",  placeholder="Jane Smith")
        title    = col2.text_input("Job Title",       key="b_title", placeholder="Senior ML Engineer")
        email    = col1.text_input("Email",           key="b_email", placeholder="jane@email.com")
        phone    = col2.text_input("Phone",           key="b_phone", placeholder="+1 555-0100")
        linkedin = col1.text_input("LinkedIn handle", key="b_li",    placeholder="janesmith")
        github   = col2.text_input("GitHub handle",   key="b_gh",    placeholder="janesmith")
        location = st.text_input("Location",          key="b_loc",   placeholder="San Francisco, CA")
        summary  = st.text_area("Professional Summary", key="b_sum", height=100,
                                placeholder="2-3 sentences about your expertise and value…")
        if st.button("✨ AI Generate Summary") and st.session_state.resume_text:
            with st.spinner("Writing…"):
                s = rewrite_summary(st.session_state.resume_text, st.session_state.jd_text)
            st.session_state["b_sum"] = s
            st.rerun()

    with tab2:
        st.markdown("#### Work Experience")
        exp_entries = []
        n_exp = st.number_input("Number of positions", 1, 6, 2, key="n_exp")
        for i in range(int(n_exp)):
            with st.expander(f"Position {i+1}", expanded=(i==0)):
                role     = st.text_input("Role",     key=f"e_role_{i}",  placeholder="ML Engineer")
                company  = st.text_input("Company",  key=f"e_comp_{i}",  placeholder="Google")
                duration = st.text_input("Duration", key=f"e_dur_{i}",   placeholder="Jan 2022 – Present")
                bullets  = st.text_area("Achievements (one per line)", key=f"e_bul_{i}", height=100,
                                        placeholder="• Reduced latency by 40%\n• Led team of 4")
                exp_entries.append({
                    "role": role, "company": company, "duration": duration,
                    "bullets": [b.lstrip("•- ").strip() for b in bullets.splitlines() if b.strip()]
                })

    with tab3:
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("#### Education")
            edu_entries = []
            n_edu = st.number_input("Number of degrees", 1, 4, 1, key="n_edu")
            for i in range(int(n_edu)):
                degree = st.text_input("Degree",  key=f"d_deg_{i}", placeholder="B.Tech Computer Science")
                school = st.text_input("School",  key=f"d_sch_{i}", placeholder="IIT Bombay")
                year   = st.text_input("Year",    key=f"d_yr_{i}",  placeholder="2021")
                gpa    = st.text_input("GPA",     key=f"d_gpa_{i}", placeholder="8.9/10")
                edu_entries.append({"degree": degree, "school": school, "year": year, "gpa": gpa})
        with col2:
            st.markdown("#### Skills")
            skills_raw = st.text_area("Skills (comma-separated)", key="b_skills", height=100,
                                      placeholder="Python, TensorFlow, Docker, AWS…")
            st.markdown("#### Certifications")
            certs_raw = st.text_area("Certifications (one per line)", key="b_certs", height=80,
                                     placeholder="AWS ML Specialty\nGoogle Cloud Professional")

    with tab4:
        st.markdown("#### Preview & Export")
        if st.button("📥 Generate & Download PDF", use_container_width=True):
            data = {
                "name":     st.session_state.get("b_name", ""),
                "title":    st.session_state.get("b_title", ""),
                "email":    st.session_state.get("b_email", ""),
                "phone":    st.session_state.get("b_phone", ""),
                "linkedin": st.session_state.get("b_li", ""),
                "github":   st.session_state.get("b_gh", ""),
                "location": st.session_state.get("b_loc", ""),
                "summary":  st.session_state.get("b_sum", ""),
                "experience": exp_entries,
                "education":  edu_entries,
                "skills": [s.strip() for s in st.session_state.get("b_skills","").split(",") if s.strip()],
                "certifications": [c.strip() for c in st.session_state.get("b_certs","").splitlines() if c.strip()],
            }
            with st.spinner("Building your PDF…"):
                pdf_bytes = build_resume_pdf(data)
            st.download_button(
                "📄 Download Resume PDF",
                data=pdf_bytes,
                file_name=f"{data['name'].replace(' ','_')}_Resume.pdf",
                mime="application/pdf",
                use_container_width=True,
            )
