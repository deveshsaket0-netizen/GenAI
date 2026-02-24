from django.shortcuts import render

# Create your views here.
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from dotenv import load_dotenv
import os
import google.generativeai as genai

# Load .env
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Configure Gemini
genai.configure(api_key=GEMINI_API_KEY)


@csrf_exempt
def chatbot(request):
    response_text = ""

    if request.method == "POST":
        user_input = request.POST.get("user_input")

        try:
            model = genai.GenerativeModel(
                "gemini-2.5-flash",
                system_instruction="You are a helpful AI tutor for beginners.")
            response = model.generate_content(user_input)

            response_text = response.text

        except Exception as e:
            response_text = f"Error: {str(e)}"

    return render(request, "home.html", {"response": response_text})