import google.generativeai as genai

genai.configure(api_key="AIzaSyCk7H4mo6pFLYlQLKK7NCMs_dY9mCumdN0")
model = genai.GenerativeModel("gemini-1.5-flash")

def _ask(system, user, max_tokens=1024):
    prompt = f"{system}\n\n{user}"
    response = model.generate_content(prompt)
    return response.text.strip()

def get_ats_feedback(resume_text, jd_text, ats_score):
    system = "You are an expert ATS specialist and resume coach. Give concise, actionable feedback in bullet points. Use emojis for clarity."
    user = f"ATS SCORE: {ats_score}/100\nRESUME:\n{resume_text[:3000]}\nJOB DESCRIPTION:\n{jd_text[:2000]}\nGive 5 specific actionable improvements. Each bullet starts with an emoji."
    return _ask(system, user)

def rewrite_summary(resume_text, jd_text, candidate_name=""):
    system = "You are a professional resume writer. Write punchy ATS-optimized summaries. 2-3 sentences max."
    user = f"Write a tailored summary.\nRESUME:\n{resume_text[:2500]}\nJOB DESCRIPTION:\n{jd_text[:1500]}\nOutput ONLY the summary, no labels."
    return _ask(system, user)

def generate_roadmap(missing_skills, target_role):
    system = "You are a senior tech career coach. Create realistic specific learning plans as numbered list."
    skills_str = ", ".join(missing_skills) if missing_skills else "No major gaps found"
    user = f"TARGET ROLE: {target_role}\nSKILLS TO LEARN: {skills_str}\nCreate 3-month roadmap with resources, time estimate, and project idea per skill."
    return _ask(system, user)

def improve_bullet_points(bullets_text, target_role):
    system = "You are a resume expert. Transform weak bullets into powerful quantified achievements."
    user = f"TARGET ROLE: {target_role}\nORIGINAL:\n{bullets_text}\nRewrite with action verb, metric, and impact. Output ONLY rewritten bullets."
    return _ask(system, user)

def generate_cover_letter(resume_text, jd_text, company, role):
    system = "You are an expert cover letter writer. Write compelling personalized letters under 350 words."
    user = f"COMPANY: {company}\nROLE: {role}\nRESUME:\n{resume_text[:2500]}\nJD:\n{jd_text[:1500]}\nWrite 3-paragraph cover letter. Sound human."
    return _ask(system, user)

def generate_interview_questions(resume_text, jd_text, role, difficulty):
    system = "You are an expert interviewer at a top tech company. Generate exactly 5 interview questions as a numbered list only. No extra text or explanation."
    user = f"Generate 5 {difficulty} level interview questions for: {role}\nCandidate background: {resume_text[:1000]}\nJob context: {jd_text[:500]}"
    return _ask(system, user)

def get_interview_feedback(question, answer, role):
    system = "You are an expert interview coach. Give constructive feedback on the answer. Be specific and encouraging."
    user = f"Role: {role}\nQuestion: {question}\nCandidate Answer: {answer}\n\nGive feedback in this format:\n⭐ Score: X/10\n✅ Strengths: (2 points)\n🔧 Improvements: (2 points)\n💡 Better approach: (1 sentence)"
    return _ask(system, user)

def chat_with_resume(message, resume_text, jd_text, chat_history, ats_score):
    system = f"You are ResumeIQ, expert AI career coach.\nRESUME:\n{resume_text[:2500]}\nJD:\n{jd_text[:1500]}\nATS SCORE: {ats_score}/100\nBe specific and encouraging. Under 200 words."
    return _ask(system, message)

def recommend_career_paths(resume_text, matched_skills):
    system = "You are a senior career strategist. Suggest realistic career paths."
    user = f"RESUME:\n{resume_text[:2000]}\nSKILLS: {', '.join(matched_skills[:20])}\nRecommend 3 career paths with title, salary range in INR LPA, why fit, one skill gap, top 2 companies hiring."
    return _ask(system, user)

def estimate_salary(role, city, experience, skills):
    system = "You are a salary expert for Indian job market. Give realistic, data-driven salary information in INR LPA."
    user = f"""Role: {role}
City: {city or 'India (Average)'}
Experience: {experience} years
Skills: {', '.join(skills[:15]) if skills else 'General'}

Provide:
1. 💰 Fresher (0-1 yr): salary range
2. 📈 Mid-level (2-4 yr): salary range
3. 🚀 Senior (5+ yr): salary range
4. 🏢 Top 5 companies hiring for this role in India with their pay range
5. 💡 One salary negotiation tip specific to this role
6. 📊 Market demand: High / Medium / Low — with reason"""
    return _ask(system, user)

def optimize_linkedin(resume_text, target_role):
    system = "You are a LinkedIn optimization expert. Write compelling, keyword-rich LinkedIn content."
    user = f"""Based on this resume, write optimized LinkedIn content:

RESUME:
{resume_text[:2500]}

TARGET ROLE: {target_role}

Provide:
1. 🎯 Optimized LinkedIn Headline (under 220 chars, keyword-rich)
2. 📝 About Section (3 paragraphs, first-person, ATS-optimized, engaging)
3. 🔑 Top 10 Skills to add on LinkedIn for this target role
4. 💼 One tip to improve LinkedIn profile visibility"""
    return _ask(system, user)

def realtime_resume_tailor(resume_text, jd_text):
    system = "You are an expert resume tailoring specialist. Rewrite resume content to perfectly match a job description."
    user = f"""ORIGINAL RESUME:
{resume_text[:2500]}

TARGET JOB DESCRIPTION:
{jd_text[:1500]}

Provide:
1. ✅ Tailored Professional Summary (3 sentences, JD keywords included)
2. 🔑 Top 10 keywords from JD to add to resume
3. 💪 3 bullet points rewritten to match JD requirements
4. ⚠️ 3 things to remove or change in current resume
5. 📊 Estimated ATS match improvement (current % → projected %)"""
    return _ask(system, user)
