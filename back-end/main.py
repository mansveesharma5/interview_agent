from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime

import google.generativeai as genai

import os
import json

from pathlib import Path

from dotenv import load_dotenv

import pdfplumber

from gemini_service import (
    analyze_resume,
    generate_interview_question,
    generate_resume_question,
    evaluate_answer
)

from fastapi.responses import FileResponse

from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer
)

from reportlab.lib.styles import (
    getSampleStyleSheet
)

# ---------------- LOAD ENV ----------------

load_dotenv()

genai.configure(
    api_key=os.getenv("GEMINI_API_KEY")
)

model = genai.GenerativeModel(
    "gemini-2.5-flash"
)

# ---------------- JSON STORAGE ----------------

CHAT_FILE = "chats.json"


def load_chats():

    if not Path(CHAT_FILE).exists():

        with open(
            CHAT_FILE,
            "w",
            encoding="utf-8"
        ) as f:

            json.dump([], f)

        return []

    try:

        with open(
            CHAT_FILE,
            "r",
            encoding="utf-8"
        ) as f:

            return json.load(f)

    except Exception:

        return []


def save_chats(chats):

    with open(
        CHAT_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            chats,
            f,
            indent=4,
            ensure_ascii=False
        )

# ---------------- FASTAPI ----------------

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------- MEMORY + JSON ----------------

all_chats = load_chats()

for chat in all_chats:

    chat.setdefault(
        "resume_text",
        ""
    )

    chat.setdefault(
        "mock_interview",
        False
    )

    chat.setdefault(
        "resume_interview",
        False
    )

    chat.setdefault(
        "interview_topic",
        ""
    )
    chat.setdefault(
        "last_topic",
        ""
    )

    chat.setdefault(
        "current_question",
        ""
    )

    chat.setdefault(
        "question_number",
        0
    )

    chat.setdefault(
        "scores",
        []
    )

    chat.setdefault(
        "evaluations",
        []
    )

    chat.setdefault(
        "average_score",
        0
    )

    chat.setdefault(
        "progress",
        0
    )

    chat.setdefault(
        "recommendation",
        "Pending"
    )

    # NEW FIELD
    chat.setdefault(
        "analytics_generated",
        False
    )

    # Recalculate analytics for old chats

    if len(chat["scores"]) > 0:

        avg = round(
            sum(chat["scores"]) /
            len(chat["scores"]),
            2
        )

        chat["average_score"] = avg

        chat["progress"] = round(
            (len(chat["scores"]) / 10) * 100,
            2
        )

        if avg >= 8:

            chat["recommendation"] = (
                "Excellent"
            )

        elif avg >= 6:

            chat["recommendation"] = (
                "Good"
            )

        else:

            chat["recommendation"] = (
                "Needs Improvement"
            )

save_chats(all_chats)
        
# ---------------- REQUEST MODEL ----------------

class MessageRequest(BaseModel):

    chatId: int
    message: str

# ---------------- CREATE CHAT ----------------

@app.post("/chat/create")
def create_chat():

    new_id = (
        max(
            [
                chat["id"]
                for chat in all_chats
            ],
            default=0
        ) + 1
    )

    new_chat = {

        "id": new_id,

        "title": "New Chat",

        "messages": [],

        "resume_text": "",

        "mock_interview": False,

        "resume_interview": False,

        "interview_topic": "",
        "last_topic": "",

        "current_question": "",

        "question_number": 0,

        "scores": [],

        "evaluations": [],

        "average_score": 0,

        "progress": 0,

        "recommendation": "",
        "analytics_generated": False
    }
    
    all_chats.append(
        new_chat
    )

    save_chats(all_chats)

    return {

        "chat_id": new_chat["id"],

        "chat": new_chat
    }

# ---------------- GET ALL CHATS ----------------

@app.get("/chat/all")
def get_chats():

    chats = {}

    for chat in all_chats:

        chats[str(chat["id"])] = chat

    return {
        "chats": chats
    }

# ---------------- RESUME UPLOAD ----------------

@app.post("/resume/upload")
async def upload_resume(
    file: UploadFile = File(...),
    chatId: int = Form(...)
):

    chat = next(
        (
            c for c in all_chats
            if c["id"] == chatId
        ),
        None
    )

    if not chat:

        return {
            "error": "Chat not found"
        }

    # ---------------- EXTRACT PDF TEXT ----------------

    text = ""

    with pdfplumber.open(
        file.file
    ) as pdf:

        for page in pdf.pages:

            extracted = (
                page.extract_text()
            )

            if extracted:

                text += extracted

    print(
        "PDF TEXT LENGTH:",
        len(text)
    )

    # ---------------- SAVE RESUME ----------------

    chat["resume_text"] = text

    # ---------------- ANALYZE RESUME ----------------

    analysis = analyze_resume(
        text,
        "General"
    )

    print(
        "ANALYSIS:",
        analysis
    )

    # ---------------- RESUME CARD ----------------

    resume_message = {

        "sender": "system",

        "type": "resume_uploaded",

        "fileName": file.filename
    }

    chat["messages"].append(
        resume_message
    )

    # ---------------- BOT ANALYSIS ----------------

    bot_message = {

        "sender": "bot",

        "text": analysis
    }

    chat["messages"].append(
        bot_message
    )

    # ---------------- TITLE ----------------

    if (
        chat["title"]
        == "New Chat"
    ):

        chat["title"] = (
            "Resume Analysis"
        )

    save_chats(all_chats)

    return {

        "status": "success",

        "analysis": analysis,

        "chat": chat
    }

# ---------------- INTERVIEW QUESTION GENERATION ----------------
# ---------------- SEND MESSAGE ----------------

@app.post("/chat")
def send_message(payload: MessageRequest):

    # ---------------- FIND CHAT ----------------

    chat = next(
        (
            c for c in all_chats
            if c["id"] == payload.chatId
        ),
        None
    )

    if not chat:

        return {
            "error": "Chat not found"
        }

    # ---------------- SAVE USER MESSAGE ----------------

    user_message = {
        "sender": "user",
        "text": payload.message
    }

    chat["messages"].append(
        user_message
    )

    clean_message = payload.message.strip()
    lower_message = clean_message.lower()

    # =====================================================
    # START MOCK INTERVIEW
    # =====================================================

    if (
        "start a mock interview" in lower_message
        or
        "start mock interview" in lower_message
    ):

        topic = lower_message

        for phrase in [
            "start a mock interview on",
            "start mock interview on",
            "start a mock interview",
            "start mock interview"
        ]:

            topic = topic.replace(
                phrase,
                ""
            )

        topic = topic.strip()

        if not topic:

            topic = chat.get(
                "last_topic",
                ""
            )

        if not topic:

            topic = "General"

        chat["mock_interview"] = True

        chat["interview_topic"] = topic
        
        chat["title"] = (
            f"🎤 {topic} Mock Interview"
        )

        chat["question_number"] = 1

        first_question = generate_interview_question(
            topic
        )

        chat["current_question"] = first_question

        chat["messages"].append(
            {
                "sender": "bot",
                "text":
                f"🎤 Mock Interview Started ({topic.title()})\n\n"
                f"Question 1/10\n\n"
                f"{first_question}"
            }
        )

        save_chats(all_chats)

        return {
            "reply": first_question,
            "chat": chat
        }
        
    if "start resume interview" in lower_message:

        if not chat["resume_text"]:

            return {
                "reply":
                "Please upload a resume first."
            }

        chat["mock_interview"] = True

        chat["resume_interview"] = True

        chat["interview_topic"] = (
            "Resume Based"
        )

        chat["question_number"] = 1

        first_question = (
            generate_resume_question(
                chat["resume_text"]
            )
        )

        chat["current_question"] = (
            first_question
        )

        chat["title"] = (
            "📄 Resume-based Interview"
        )

        chat["messages"].append(
            {
                "sender": "bot",
                "text":
                f"📄 Resume-Based Interview Started\n\n"
                f"Question 1/10\n\n"
                f"{first_question}"
            }
        )

        save_chats(all_chats)

        return {
            "reply":
            first_question,
            "chat":
            chat
        }

    # =====================================================
    # MOCK INTERVIEW ANSWER EVALUATION
    # =====================================================

    if chat.get("mock_interview", False):

        result = evaluate_answer(
            chat["current_question"],
            payload.message
        )

        evaluation = result["evaluation"]
        score = result["score"]

        chat["evaluations"].append(
            evaluation
        )

        chat["scores"].append(
            score
        )

        chat["messages"].append(
            {
                "sender": "bot",
                "text": evaluation
            }
        )

        # ---------- INTERVIEW COMPLETE ----------

        if chat["question_number"] >= 10:
            chat["mock_interview"] = False
            chat["resume_interview"] = False

            avg_score = round(
                sum(chat["scores"]) /
                len(chat["scores"]),
                2
            )
            chat["average_score"] = avg_score

            chat["progress"] = 100

            if avg_score >= 8:

                chat["recommendation"] = "Excellent"

            elif avg_score >= 6:

                chat["recommendation"] = "Good"

            else:

                chat["recommendation"] = "Needs Improvement"
            report = f"""
📊 INTERVIEW REPORT

━━━━━━━━━━━━━━━━━━━━━━

🎯 Topic:
{chat['interview_topic']}

📝 Questions Attempted:
{len(chat['scores'])}/10

📊 Progress:
100%

⭐ Average Score:
{avg_score}/10

🏆 Recommendation:
{chat['recommendation']}

━━━━━━━━━━━━━━━━━━━━━━

You can now download the complete report.
"""
            chat["messages"].append(
                {
                    "sender": "bot",
                    "text": report
                }
            )

            save_chats(all_chats)

            return {
                "reply":
                "Interview Completed",
                "chat":
                chat
            }

        # ---------- NEXT QUESTION ----------

        if chat.get(
            "resume_interview",
            False
        ):

            next_question = (
                generate_resume_question(
                    chat["resume_text"]
                )
            )

        else:

            next_question = (
                generate_interview_question(
                    chat["interview_topic"]
                )
            )

        chat["question_number"] += 1

        chat["current_question"] = (
            next_question
        )

        chat["messages"].append(
            {
                "sender": "bot",
                "text":
                f"Question {chat['question_number']}/10\n\n"
                f"{next_question}"
            }
        )

        save_chats(all_chats)

        return {
            "reply": evaluation,
            "chat": chat
        }

    # =====================================================
    # NORMAL CHAT MODE
    # =====================================================

    greetings = [
        "hello",
        "hi",
        "hey",
        "hii",
        "hola"
    ]

    if (
        chat["title"] in
        ["New Chat", "Resume Analysis"]
        and
        lower_message not in greetings
    ):

        title = clean_message

        if len(title) > 35:

            title = (
                title[:35] + "..."
            )

        chat["title"] = title

    # ---------------- RESUME CONTEXT ----------------

    resume_context = ""

    if chat.get("resume_text"):

        resume_context = f"""
Candidate Resume:

{chat["resume_text"]}
"""

    # ---------------- CHAT HISTORY ----------------

    history_context = ""

    recent_messages = (
        chat["messages"][-16:-1]
    )

    for msg in recent_messages:

        if msg.get("sender") == "user":

            history_context += (
                f"User: {msg.get('text', '')}\n"
            )

        elif msg.get("sender") == "bot":

            history_context += (
                f"Assistant: {msg.get('text', '')}\n"
            )

    # ---------------- PROMPT ----------------

    final_prompt = f"""
You are an AI Interview Preparation Agent.

Continue the conversation naturally.

Use previous conversation context whenever the user says:

- above topic
- previous answer
- explain more
- continue
- elaborate
- examples
- summarize

{resume_context}

Conversation History:

{history_context}

Latest User Message:

{payload.message}

Instructions:

- Maintain conversation memory
- Be professional
- Give interview-focused answers
- Use resume context if available
- Use previous chat context
- Format answers properly
"""

    # ---------------- GEMINI ----------------

    response = model.generate_content(
        final_prompt
    )

    bot_reply = response.text
    topic_prompt = f"""
Identify the main topic of this user message.

Message:
{payload.message}

Return ONLY the topic name.
"""

    try:

        topic_response = model.generate_content(
            topic_prompt
        )

        chat["last_topic"] = (
            topic_response.text.strip()
        )

    except:

        pass

    chat["messages"].append(
        {
            "sender": "bot",
            "text": bot_reply
        }
    )

    save_chats(all_chats)

    return {
        "reply": bot_reply,
        "chat": chat
    }
    
class StartInterviewRequest(BaseModel):
    chatId: int
    topic: str
    
@app.post("/interview/start")
def start_interview(payload: StartInterviewRequest):
    chat = next(
        (
            c for c in all_chats
            if c["id"] == payload.chatId
        ),
        None
    )

    if not chat:

        return {
            "error":
            "Chat not found"
        }

    question = generate_interview_question(
        payload.topic
    )

    chat["mock_interview"] = True

    chat["interview_topic"] = (
        payload.topic
    )

    chat["current_question"] = (
        question
    )

    chat["question_number"] = 1

    chat["messages"].append(
        {
            "sender": "bot",
            "text": question
        }
    )
    chat["title"] = (
        f"🎤 {payload.topic} Mock Interview"
    )

    save_chats(all_chats)

    return {
        "question": question
    }
    
@app.get("/report/{chat_id}")
def generate_report(chat_id: int):

    chat = next(
        (
            c for c in all_chats
            if c["id"] == chat_id
        ),
        None
    )

    if not chat:

        return {
            "error": "Chat not found"
        }

    filename = (
        f"Interview_Report_{chat_id}.pdf"
    )

    doc = SimpleDocTemplate(
        filename
    )

    styles = getSampleStyleSheet()

    content = []

    # ==========================
    # TITLE
    # ==========================

    content.append(
        Paragraph(
            "AI Interview Preparation Agent",
            styles["Title"]
        )
    )

    content.append(
        Paragraph(
            "Interview Performance Report",
            styles["Heading2"]
        )
    )

    content.append(
        Spacer(1, 20)
    )

    # ==========================
    # DATE
    # ==========================

    current_date = datetime.now().strftime(
        "%d-%m-%Y %H:%M"
    )

    content.append(
        Paragraph(
            f"<b>Generated On:</b> {current_date}",
            styles["Normal"]
        )
    )

    content.append(
        Spacer(1, 12)
    )

    # ==========================
    # INTERVIEW TYPE
    # ==========================

    interview_type = (
        "Resume Interview"
        if chat.get(
            "interview_topic"
        ) == "Resume Based"
        else "Mock Interview"
    )

    content.append(
        Paragraph(
            f"<b>Interview Type:</b> {interview_type}",
            styles["Normal"]
        )
    )

    content.append(
        Paragraph(
            f"<b>Topic:</b> {chat['interview_topic']}",
            styles["Normal"]
        )
    )

    content.append(
        Paragraph(
            f"<b>Questions Attempted:</b> {chat['question_number']}",
            styles["Normal"]
        )
    )

    content.append(
        Spacer(1, 20)
    )

    # ==========================
    # AVERAGE SCORE
    # ==========================

    avg_score = 0

    if len(chat["scores"]) > 0:

        avg_score = round(
            sum(chat["scores"])
            /
            len(chat["scores"]),
            2
        )

    recommendation = (
        "Excellent"
        if avg_score >= 8
        else "Good"
        if avg_score >= 6
        else "Needs Improvement"
    )
    # ==========================
    # PERFORMANCE ANALYTICS
    # ==========================

    highest_score = 0
    lowest_score = 0

    best_question = "-"
    weakest_question = "-"

    if len(chat["scores"]) > 0:

        highest_score = max(
            chat["scores"]
        )

        lowest_score = min(
            chat["scores"]
        )

        best_question = (
            chat["scores"].index(
                highest_score
            ) + 1
        )

        weakest_question = (
            chat["scores"].index(
                lowest_score
            ) + 1
        )

    content.append(
        Paragraph(
            "<b>Overall Performance</b>",
            styles["Heading2"]
        )
    )

    content.append(
        Paragraph(
            f"<b>Average Score:</b> {avg_score}/10",
            styles["Normal"]
        )
    )

    content.append(
        Paragraph(
            f"<b>Recommendation:</b> {recommendation}",
            styles["Normal"]
        )
    )
    content.append(
        Paragraph(
            f"<b>Highest Score:</b> {highest_score}/10",
            styles["Normal"]
        )
    )

    content.append(
        Paragraph(
            f"<b>Lowest Score:</b> {lowest_score}/10",
            styles["Normal"]
        )
    )

    content.append(
        Paragraph(
            f"<b>Best Performance:</b> Question {best_question}",
            styles["Normal"]
        )
    )

    content.append(
        Paragraph(
            f"<b>Needs Most Improvement:</b> Question {weakest_question}",
            styles["Normal"]
        )
    )

    content.append(
        Spacer(1, 20)
    )

    # ==========================
    # EVALUATIONS
    # ==========================

    content.append(
        Paragraph(
            "Question-wise Evaluation",
            styles["Heading2"]
        )
    )

    content.append(
        Spacer(1, 10)
    )

    for index, evaluation in enumerate(
        chat["evaluations"],
        start=1
    ):

        score = (
            chat["scores"][index - 1]
            if index - 1 <
            len(chat["scores"])
            else 0
        )

        content.append(
            Paragraph(
                f"<b>Question {index}</b>",
                styles["Heading3"]
            )
        )

        content.append(
            Paragraph(
                f"<b>Score:</b> {score}/10",
                styles["Normal"]
            )
        )

        content.append(
            Paragraph(
                evaluation.replace(
                    "\n",
                    "<br/>"
                ),
                styles["Normal"]
            )
        )

        content.append(
            Spacer(1, 12)
        )
    doc.build(content)

    return FileResponse(
        filename,
        media_type="application/pdf",
        filename=filename
    )

@app.post("/interview/stop/{chat_id}")
def stop_interview(chat_id: int):

    chat = next(
        (
            c for c in all_chats
            if c["id"] == chat_id
        ),
        None
    )

    if not chat:

        return {
            "error": "Chat not found"
        }

    if not chat.get(
        "mock_interview",
        False
    ):

        return {
            "message":
            "No active interview."
        }

    # ---------------- STOP INTERVIEW ----------------

    chat["mock_interview"] = False
    chat["resume_interview"] = False

    # ---------------- CALCULATE STATS ----------------

    total_questions = 10

    attempted = len(
        chat["scores"]
    )

    avg_score = 0

    if attempted > 0:

        avg_score = round(
            sum(chat["scores"])
            /
            attempted,
            2
        )

    progress = round(
        (attempted / total_questions)
        * 100,
        2
    )

    # ---------------- RECOMMENDATION ----------------

    if avg_score >= 8:

        recommendation = (
            "Excellent"
        )

    elif avg_score >= 6:

        recommendation = (
            "Good"
        )

    else:

        recommendation = (
            "Needs Improvement"
        )

    # ---------------- SAVE REPORT DATA ----------------

    chat["average_score"] = avg_score

    chat["progress"] = progress

    chat["recommendation"] = (
        recommendation
    )

    # ---------------- CHAT REPORT ----------------

    report = f"""
🎯 INTERVIEW STOPPED

━━━━━━━━━━━━━━━━━━━━━━

📚 Topic:
{chat['interview_topic']}

📝 Questions Attempted:
{attempted}/10

📊 Progress:
{progress}%

⭐ Average Score:
{avg_score}/10

🏆 Recommendation:
{recommendation}

━━━━━━━━━━━━━━━━━━━━━━

You can now download the complete report.
"""

    chat["messages"].append(
        {
            "sender": "bot",
            "text": report
        }
    )

    save_chats(all_chats)

    return {
        "status": "stopped",
        "average_score": avg_score,
        "progress": progress,
        "recommendation": recommendation,
        "chat": chat
    }