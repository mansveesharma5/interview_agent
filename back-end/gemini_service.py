import google.generativeai as genai
from dotenv import load_dotenv
import os
import re

# LOAD ENV
load_dotenv()

# CONFIGURE GEMINI
genai.configure(
    api_key=os.getenv("GEMINI_API_KEY")
)

# LOAD MODEL
model = genai.GenerativeModel(
    "gemini-2.5-flash"
)

# ---------------- CHAT RESPONSE ----------------

def generate_ai_response(
    user_message,
    interview_type,
    company_name
):

    try:

        prompt = f"""
You are an AI Interview Preparation Agent.

Interview Type:
{interview_type}

Company:
{company_name}

User Question:
{user_message}

Provide professional,
clear and interview-focused answers.
"""

        response = model.generate_content(
            prompt
        )

        return response.text

    except Exception as e:

        print(
            "Gemini Chat Error:",
            e
        )

        return (
            "Error generating response."
        )

# ---------------- RESUME ANALYSIS ----------------

def analyze_resume(
    resume_text,
    company_name,
):

    try:

        # EMPTY CHECK
        if not resume_text.strip():

            return (
                "Could not extract text "
                "from resume."
            )

        prompt = f"""
You are an expert AI Interview Coach.

Analyze this resume briefly and professionally.

Resume:
{resume_text}

Provide:

# Resume Summary

## Strengths
(3-5 bullet points)

## Weaknesses
(3-5 bullet points)

## Skills Found

## Suggested Interview Focus Areas

## 10 Important Interview Questions

Keep response concise and structured.
"""

        response = model.generate_content(
            prompt
        )

        print(
            "Resume Analysis Generated"
        )

        if hasattr(response, "text"):

            return response.text

        return (
            "No analysis generated."
        )

    except Exception as e:

        print(
            "Resume Analysis Error:",
            e
        )

        return (
            f"Resume analysis failed: {str(e)}"
        )

def generate_interview_question(topic):
    prompt = f"""
You are an interviewer.

Generate ONE interview question.

Topic:
{topic}

Return only question.
"""

    response = model.generate_content(
        prompt
    )

    return response.text


def evaluate_answer(question, answer):

    prompt = f"""
You are a senior interviewer.

Question:
{question}

Candidate Answer:
{answer}

Evaluate and provide EXACTLY in this format:

Communication Score: X/10
Technical Score: X/10
Confidence Score: X/10

Strengths:
- point

Weaknesses:
- point

Improvement:
- point

Overall Score: X/10
"""

    response = model.generate_content(
        prompt
    )

    evaluation_text = response.text

    try:

        score_match = re.search(
            r"Overall Score:\s*(\d+(\.\d+)?)",
            evaluation_text
        )

        overall_score = (
            float(score_match.group(1))
            if score_match
            else 0
        )

    except:

        overall_score = 0

    return {
        "evaluation": evaluation_text,
        "score": overall_score
    }
    
def generate_resume_question(resume_text):

    prompt = f"""
You are a technical interviewer.

The candidate's resume is:

{resume_text}

Generate ONE interview question based ONLY on the resume.

Rules:
- Ask about projects
- Ask about technologies
- Ask about skills
- Ask about experience

Return ONLY the question.
"""

    response = model.generate_content(
        prompt
    )

    return response.text