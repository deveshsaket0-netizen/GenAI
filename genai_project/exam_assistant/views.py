from django.shortcuts import render, redirect
from .forms import GenerateForm
from .models import Question
from .utils import generate_questions, generate_revision_plan


def home(request):
    return render(request, "home.html")


def generate(request):
    if request.method == "POST":
        form = GenerateForm(request.POST)
        if form.is_valid():

            exam = form.cleaned_data["exam"]
            subject = form.cleaned_data["subject"]
            topic = form.cleaned_data["topic"]
            difficulty = form.cleaned_data["difficulty"]

            questions_data = generate_questions(exam, subject, topic, difficulty)

            if questions_data:
                for q in questions_data:
                    Question.objects.create(
                        exam=exam,
                        subject=subject,
                        topic=topic,
                        difficulty=difficulty,
                        question_text=q["question"],
                        option_a=q["option_a"],
                        option_b=q["option_b"],
                        option_c=q["option_c"],
                        option_d=q["option_d"],
                        correct_answer=q["correct_answer"],
                        explanation=q["explanation"],
                    )

                return redirect("quiz")

    else:
        form = GenerateForm()

    return render(request, "generate.html", {"form": form})


def quiz(request):
    questions = Question.objects.order_by("-created_at")[:5]

    if request.method == "POST":
        score = 0

        for question in questions:
            selected = request.POST.get(str(question.id))
            if selected and selected == question.correct_answer:
                score += 1

        return render(request, "result.html", {
            "score": score,
            "questions": questions
        })

    return render(request, "quiz.html", {"questions": questions})


def dashboard(request):
    total = Question.objects.count()

    return render(request, "dashboard.html", {
        "total": total,
        "correct": 0,
        "accuracy": 0
    })


def revision_plan(request):
    weak_topics = "Polity, Economy"
    plan = generate_revision_plan(weak_topics)

    return render(request, "revision_plan.html", {"plan": plan})