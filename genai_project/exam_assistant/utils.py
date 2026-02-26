import json
import os
from pathlib import Path

import google.generativeai as genai


BASE_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = BASE_DIR / ".env"


def _load_env_file() -> None:
    if not ENV_PATH.exists():
        return
    for line in ENV_PATH.read_text().splitlines():
        item = line.strip()
        if not item or item.startswith("#") or "=" not in item:
            continue
        key, value = item.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


_load_env_file()
api_key = os.getenv("GEMINI_API_KEY")

if api_key:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-1.5-flash")
else:
    model = None


def _extract_json_list(raw_text):
    if not raw_text:
        return []
    cleaned = raw_text.strip().replace("```json", "").replace("```", "").strip()
    start = cleaned.find("[")
    end = cleaned.rfind("]")
    if start == -1 or end == -1:
        return []
    try:
        return json.loads(cleaned[start : end + 1])
    except json.JSONDecodeError:
        return []


def generate_questions(exam, subject, topics, difficulty):
    if model is None:
        return []

    prompt = f"""
    You are a government exam prep assistant.
    Generate exactly 20 MCQs for {exam}.
    Subject: {subject}
    Topics: {topics}
    Difficulty: {difficulty}

    Return ONLY valid JSON as a list with this structure:
    [
      {{
        "question": "",
        "topic": "",
        "option_a": "",
        "option_b": "",
        "option_c": "",
        "option_d": "",
        "correct_answer": "A",
        "explanation": ""
      }}
    ]
    """

    try:
        response = model.generate_content(prompt)
        parsed = _extract_json_list(response.text)
        return parsed[:20]
    except Exception:
        return []


def generate_performance_review(exam, subject, score, total, weak_areas):
    if model is None:
        return "AI review unavailable right now."

    prompt = f"""
    For a {exam} aspirant, summarize quiz performance.
    Subject: {subject}
    Score: {score}/{total}
    Weak areas: {weak_areas}

    Give concise feedback with:
    1) performance summary
    2) immediate actions
    3) what to revise next
    """
    try:
        return model.generate_content(prompt).text
    except Exception:
        return "AI review unavailable right now."


def generate_mind_map(exam, subject, topic):
    if model is None:
        return "Mind map generation unavailable right now."

    prompt = f"""
    Create a hierarchical study mind map for a {exam} aspirant.
    Subject: {subject}
    Topic: {topic}

    Use a tree-like text layout:
    Main Topic
    - Subtopic
      - Key point
      - Key point
    """
    try:
        return model.generate_content(prompt).text
    except Exception:
        return "Mind map generation unavailable right now."


def generate_revision_plan(target_exam, weak_topics, avg_score):
    if model is None:
        return "Revision plan generation unavailable right now."

    prompt = f"""
    Build a personalized 7-day revision plan for {target_exam} exam preparation.
    Weak topics: {weak_topics}
    Current average score: {avg_score:.2f}

    Include daily goals, priority topics, and improvement strategy.
    """

    try:
        return model.generate_content(prompt).text
    except Exception:
        return "Revision plan generation unavailable right now."
