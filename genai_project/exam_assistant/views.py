from collections import Counter
from datetime import timedelta

from django.contrib.auth.decorators import login_required
from django.db.models import Avg
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import GenerateForm, MindMapForm, ProfileForm
from .models import Attempt, MindMap, Question, QuizSession, UserProfile
from .utils import (
    generate_mind_map,
    generate_performance_review,
    generate_questions,
    generate_revision_plan,
)


def _get_profile(user):
    return UserProfile.objects.get_or_create(
        user=user,
        defaults={"full_name": user.get_full_name() or user.username},
    )[0]


def _calculate_streak(user):
    days = sorted(
        {
            attempt.attempted_at.date()
            for attempt in Attempt.objects.filter(user=user).only("attempted_at")
        },
        reverse=True,
    )
    if not days:
        return 0

    streak = 0
    current = timezone.localdate()
    for day in days:
        if day == current:
            streak += 1
            current -= timedelta(days=1)
        elif day == current - timedelta(days=1) and streak == 0:
            streak = 1
            current = day - timedelta(days=1)
        else:
            break
    return streak


@login_required
def home(request):
    profile = _get_profile(request.user)
    if request.method == "POST":
        profile.target_exam = request.POST.get("target_exam", profile.target_exam)
        profile.save(update_fields=["target_exam"])
        return redirect("home")

    latest_sessions = QuizSession.objects.filter(user=request.user).order_by("-created_at")[:5]

    return render(
        request,
        "home.html",
        {
            "profile": profile,
            "latest_sessions": latest_sessions,
        },
    )


@login_required
def profile_settings(request):
    profile = _get_profile(request.user)
    if request.method == "POST":
        form = ProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            return redirect("home")
    else:
        form = ProfileForm(instance=profile)
    return render(request, "profile_settings.html", {"form": form})


@login_required
def generate(request):
    profile = _get_profile(request.user)
    if request.method == "POST":
        form = GenerateForm(request.POST)
        if form.is_valid():
            exam = form.cleaned_data["exam"]
            subject = form.cleaned_data["subject"]
            topics = form.cleaned_data["topics"]
            difficulty = form.cleaned_data["difficulty"]
            questions_data = generate_questions(exam, subject, topics, difficulty)

            if questions_data:
                quiz_session = QuizSession.objects.create(
                    user=request.user,
                    exam=exam,
                    subject=subject,
                    topics=topics,
                    difficulty=difficulty,
                    total_questions=20,
                )

                for q in questions_data:
                    Question.objects.create(
                        quiz_session=quiz_session,
                        exam=exam,
                        subject=subject,
                        topic=q.get("topic") or topics,
                        difficulty=difficulty,
                        question_text=q.get("question", ""),
                        option_a=q.get("option_a", ""),
                        option_b=q.get("option_b", ""),
                        option_c=q.get("option_c", ""),
                        option_d=q.get("option_d", ""),
                        correct_answer=(q.get("correct_answer", "A") or "A")[0],
                        explanation=q.get("explanation", ""),
                    )
                return redirect("quiz", session_id=quiz_session.id)
    else:
        form = GenerateForm(initial={"exam": profile.target_exam})

    return render(request, "generate.html", {"form": form})


@login_required
def quiz(request, session_id):
    session = get_object_or_404(QuizSession, id=session_id, user=request.user)
    questions = session.questions.all().order_by("id")

    if request.method == "POST":
        Attempt.objects.filter(quiz_session=session, user=request.user).delete()
        score = 0
        weak_topics = []

        for question in questions:
            selected = request.POST.get(str(question.id), "")
            is_correct = selected == question.correct_answer
            score += 1 if is_correct else 0
            if not is_correct:
                weak_topics.append(question.topic)

            Attempt.objects.create(
                user=request.user,
                quiz_session=session,
                question=question,
                selected_option=selected,
                is_correct=is_correct,
            )

        session.score = score
        weak_summary = ", ".join([t for t, _ in Counter(weak_topics).most_common(5)]) or "None"
        session.performance_review = generate_performance_review(
            session.exam,
            session.subject,
            score,
            session.total_questions,
            weak_summary,
        )
        session.save(update_fields=["score", "performance_review"])

        question_results = [
            {
                "question": q,
                "selected": request.POST.get(str(q.id), ""),
                "is_correct": request.POST.get(str(q.id), "") == q.correct_answer,
            }
            for q in questions
        ]

        return render(
            request,
            "quiz_result.html",
            {
                "session": session,
                "question_results": question_results,
                "weak_summary": weak_summary,
            },
        )

    return render(request, "quiz.html", {"questions": questions, "session": session})


@login_required
def dashboard(request):
    sessions = QuizSession.objects.filter(user=request.user).order_by("-created_at")
    avg_score = sessions.aggregate(avg=Avg("score"))["avg"] or 0

    subject_scores = {}
    weak_topics = Counter()
    for session in sessions:
        subject_scores.setdefault(session.subject, []).append(session.score)
        for attempt in session.attempts.filter(is_correct=False).select_related("question"):
            weak_topics[attempt.question.topic] += 1

    subject_avg = {
        subject: sum(scores) / max(len(scores), 1)
        for subject, scores in subject_scores.items()
    }
    strong_subjects = sorted(subject_avg, key=subject_avg.get, reverse=True)[:3]
    weak_subjects = sorted(subject_avg, key=subject_avg.get)[:3]

    activity_history = sessions[:10]
    streak = _calculate_streak(request.user)

    chart_labels = list(subject_avg.keys())
    chart_values = [round(subject_avg[key], 2) for key in chart_labels]

    return render(
        request,
        "dashboard.html",
        {
            "average_score": round(avg_score, 2),
            "strong_subjects": strong_subjects,
            "weak_subjects": weak_subjects,
            "study_streak": streak,
            "activity_history": activity_history,
            "chart_labels": chart_labels,
            "chart_values": chart_values,
            "top_weak_topics": [topic for topic, _ in weak_topics.most_common(5)],
        },
    )


@login_required
def mind_map(request):
    profile = _get_profile(request.user)
    generated_map = None

    if request.method == "POST":
        form = MindMapForm(request.POST)
        if form.is_valid():
            subject = form.cleaned_data["subject"]
            topic = form.cleaned_data["topic"]
            generated_map = generate_mind_map(profile.target_exam, subject, topic)
            MindMap.objects.create(
                user=request.user,
                exam=profile.target_exam,
                subject=subject,
                topic=topic,
                content=generated_map,
            )
    else:
        form = MindMapForm()

    history = MindMap.objects.filter(user=request.user).order_by("-created_at")[:10]
    return render(
        request,
        "mind_map.html",
        {"form": form, "generated_map": generated_map, "history": history},
    )


@login_required
def revision_plan(request):
    profile = _get_profile(request.user)
    sessions = QuizSession.objects.filter(user=request.user)
    avg_score = sessions.aggregate(avg=Avg("score"))["avg"] or 0

    weak_topic_counter = Counter(
        Attempt.objects.filter(user=request.user, is_correct=False)
        .select_related("question")
        .values_list("question__topic", flat=True)
    )
    weak_topics = ", ".join([topic for topic, _ in weak_topic_counter.most_common(8)]) or "General revision"

    plan = generate_revision_plan(profile.target_exam, weak_topics, avg_score)
    return render(
        request,
        "revision_plan.html",
        {
            "plan": plan,
            "weak_topics": weak_topics,
            "average_score": round(avg_score, 2),
        },
    )
