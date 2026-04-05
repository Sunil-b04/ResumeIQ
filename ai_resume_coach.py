from groq import Groq
import os

client = Groq(api_key="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")

def _ask(system: str, user: str, max_tokens: int = 1024) -> str:
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": system},
            {"role": "user",   "content": user}
        ],
        max_tokens=max_tokens,
    )
    return response.choices[0].message.content.strip()

def get_ats_feedback(resume_text: str, jd_text: str, ats_score: int) -> str:
    system = "You are an expert ATS specialist and resume coach. Give concise, actionable feedback in bullet points. Use emojis for clarity."
    user = f"ATS SCORE: {ats_score}/100\nRESUME:\n{resume_text[:3000]}\nJOB DESCRIPTION:\n{jd_text[:2000]}\nGive 5 specific actionable improvements. Each bullet starts with an emoji."
    return _ask(system, user)

def rewrite_summary(resume_text: str, jd_text: str, candidate_name: str = "") -> str:
    system = "You are a professional resume writer. Write punchy ATS-optimized summaries. 2-3 sentences max."
    user = f"Write a tailored summary.\nRESUME:\n{resume_text[:2500]}\nJOB DESCRIPTION:\n{jd_text[:1500]}\nOutput ONLY the summary, no labels."
    return _ask(system, user)

def generate_roadmap(missing_skills: list, target_role: str) -> str:
    system = "You are a senior tech career coach. Create realistic specific learning plans as numbered list."
    skills_str = ", ".join(missing_skills) if missing_skills else "No major gaps found"
    user = f"TARGET ROLE: {target_role}\nSKILLS TO LEARN: {skills_str}\nCreate 3-month roadmap with resources, time estimate, and project idea per skill."
    return _ask(system, user)

def improve_bullet_points(bullets_text: str, target_role: str) -> str:
    system = "You are a resume expert. Transform weak bullets into powerful quantified achievements."
    user = f"TARGET ROLE: {target_role}\nORIGINAL:\n{bullets_text}\nRewrite with action verb, metric, and impact. Output ONLY rewritten bullets."
    return _ask(system, user)

def generate_cover_letter(resume_text: str, jd_text: str, company: str, role: str) -> str:
    system = "You are an expert cover letter writer. Write compelling personalized letters under 350 words."
    user = f"COMPANY: {company}\nROLE: {role}\nRESUME:\n{resume_text[:2500]}\nJD:\n{jd_text[:1500]}\nWrite 3-paragraph cover letter. Sound human."
    return _ask(system, user)

def generate_interview_questions(resume_text: str, jd_text: str) -> str:
    system = "You are an expert interviewer. Generate realistic challenging questions."
    user = f"RESUME:\n{resume_text[:2000]}\nJD:\n{jd_text[:1000]}\nGenerate 10 questions — behavioral, technical, situational."
    return _ask(system, user)

def chat_with_resume(message: str, resume_text: str, jd_text: str, chat_history: list, ats_score: int) -> str:
    system = f"You are ResumeIQ, expert AI career coach.\nRESUME:\n{resume_text[:2500]}\nJD:\n{jd_text[:1500]}\nATS SCORE: {ats_score}/100\nBe specific and encouraging. Under 200 words."
    return _ask(system, message)

def recommend_career_paths(resume_text: str, matched_skills: list) -> str:
    system = "You are a senior career strategist. Suggest realistic career paths."
    user = f"RESUME:\n{resume_text[:2000]}\nSKILLS: {', '.join(matched_skills[:20])}\nRecommend 3 career paths with title, salary, why fit, skill gap, top 2 companies."
    return _ask(system, user)
