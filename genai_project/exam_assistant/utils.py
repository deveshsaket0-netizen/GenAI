import json
import re
import os
from pathlib import Path

# Load .env manually
_BASE_DIR = Path(__file__).resolve().parent.parent
_ENV_PATH = _BASE_DIR / ".env"

def _load_env():
    if not _ENV_PATH.exists():
        print(f"[utils] WARNING: .env not found at {_ENV_PATH}")
        return
    for line in _ENV_PATH.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))

_load_env()  # Must be called BEFORE reading env vars

from groq import Groq

_groq_key = os.getenv("GROQ_API_KEY")
if not _groq_key:
    print("[utils] ERROR: GROQ_API_KEY not found in .env")
    groq_client = None
else:
    print(f"[utils] Groq key loaded OK ({_groq_key[:8]}...)")
    groq_client = Groq(api_key=_groq_key)


def _call_gemini(prompt: str) -> str:
    if groq_client is None:
        raise RuntimeError("GROQ_API_KEY not found in .env")
    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content


def _extract_json_list(text: str) -> list:
    cleaned = re.sub(r"```(?:json)?", "", text).replace("```", "").strip()
    start = cleaned.find("[")
    end = cleaned.rfind("]")
    if start == -1 or end == -1:
        return []
    return json.loads(cleaned[start:end + 1])


def _extract_pdf_text(pdf_bytes: bytes, max_chars: int = 2000) -> str:
    try:
        import fitz  # PyMuPDF
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        text = ""
        for page in doc:
            text += page.get_text()
            if len(text) >= max_chars:
                break
        doc.close()
        return text[:max_chars].strip()
    except Exception as e:
        print(f"[_extract_pdf_text] Error: {e}")
        return ""


def generate_questions(exam: str, subject: str, topics: str, difficulty: str) -> list:
    prompt = f"""Generate exactly 5 multiple-choice questions for a {exam} exam.
Subject: {subject}, Topics: {topics}, Difficulty: {difficulty}

Return ONLY a valid JSON list, no markdown:
[
  {{
    "topic": "topic name",
    "question": "Question text?",
    "option_a": "Option A",
    "option_b": "Option B",
    "option_c": "Option C",
    "option_d": "Option D",
    "correct_answer": "A",
    "explanation": "One sentence explanation."
  }}
]"""
    try:
        raw = _call_gemini(prompt)
        result = _extract_json_list(raw)[:5]
        print(f"[generate_questions] Got {len(result)} questions OK")
        return result
    except Exception as e:
        print(f"[generate_questions] Error: {e}")
        return []


def generate_questions_from_pdf(pdf_bytes: bytes, num_questions: int, difficulty: str) -> list:
    text = _extract_pdf_text(pdf_bytes, max_chars=2000)
    if not text:
        print("[generate_questions_from_pdf] Could not extract text from PDF")
        return []

    print(f"[generate_questions_from_pdf] Extracted {len(text)} chars from PDF")

    prompt = f"""Based on the following text, generate exactly {num_questions} multiple-choice questions.
Difficulty: {difficulty}

TEXT:
{text}

Return ONLY a valid JSON list, no markdown:
[
  {{
    "topic": "short topic from the text",
    "question": "Question based on the text?",
    "option_a": "Option A",
    "option_b": "Option B",
    "option_c": "Option C",
    "option_d": "Option D",
    "correct_answer": "A",
    "explanation": "One sentence explanation."
  }}
]"""
    try:
        raw = _call_gemini(prompt)
        result = _extract_json_list(raw)[:num_questions]
        print(f"[generate_questions_from_pdf] Got {len(result)} questions OK")
        return result
    except Exception as e:
        print(f"[generate_questions_from_pdf] Error: {e}")
        return []


def generate_performance_review(exam: str, subject: str, score: int, total: int, weak_topics: str) -> str:
    prompt = f"""Write a 3-sentence performance review for a {exam} student.
Subject: {subject}, Score: {score}/{total}, Weak topics: {weak_topics}
Be encouraging. Plain text only."""
    try:
        return _call_gemini(prompt).strip()
    except Exception as e:
        print(f"[generate_performance_review] Error: {e}")
        return "Could not generate performance review."


def generate_mind_map(exam: str, subject: str, topic: str) -> str:
    prompt = f"""Create a concise mind map for {exam} - {subject} - {topic}.
Use indented text with dashes. Keep it brief. Plain text only."""
    try:
        return _call_gemini(prompt).strip()
    except Exception as e:
        print(f"[generate_mind_map] Error: {e}")
        return "Could not generate mind map."


def generate_revision_plan(exam: str, weak_topics: str, avg_score: float) -> str:
    prompt = f"""Create a 7-day revision plan for {exam}.
Weak topics: {weak_topics}, Average score: {avg_score:.1f}%
One line per day. Plain text only."""
    try:
        return _call_gemini(prompt).strip()
    except Exception as e:
        print(f"[generate_revision_plan] Error: {e}")
        return "Could not generate revision plan."