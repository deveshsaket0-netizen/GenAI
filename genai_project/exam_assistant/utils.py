import google.generativeai as genai
import os
import json

api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-pro")
else:
    model = None


def generate_questions(exam, subject, topic, difficulty):
    if model is None:
        return None
    
    prompt = f"""
    Generate 5 MCQs for {exam}.
    Subject: {subject}
    Topic: {topic}
    Difficulty: {difficulty}

    Format in JSON like:
    [
      {{
        "question": "",
        "option_a": "",
        "option_b": "",
        "option_c": "",
        "option_d": "",
        "correct_answer": "A/B/C/D",
        "explanation": ""
      }}
    ]
    """

    try:
        response = model.generate_content(prompt)
        questions = json.loads(response.text)
        return questions
    except:
        return None


def generate_revision_plan(weak_topics):
    if model is None:
        return None
    
    prompt = f"""
    Create a 7-day revision plan.
    Weak topics: {weak_topics}
    Study time: 3 hours per day.
    """

    try:
        response = model.generate_content(prompt)
        return response.text
    except:
        return None