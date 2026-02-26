from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


def backfill_quiz_sessions(apps, schema_editor):
    User = apps.get_model("auth", "User")
    QuizSession = apps.get_model("exam_assistant", "QuizSession")
    Question = apps.get_model("exam_assistant", "Question")
    Attempt = apps.get_model("exam_assistant", "Attempt")

    default_user = User.objects.order_by("id").first()
    if default_user is None:
        default_user = User.objects.create(username="migration_user")

    for question in Question.objects.filter(quiz_session__isnull=True):
        session = QuizSession.objects.create(
            user=default_user,
            exam=question.exam,
            subject=question.subject,
            topics=question.topic,
            difficulty=question.difficulty,
            score=0,
            total_questions=1,
            performance_review="",
        )
        question.quiz_session = session
        question.save(update_fields=["quiz_session"])

    for attempt in Attempt.objects.filter(quiz_session__isnull=True):
        if attempt.question and attempt.question.quiz_session_id:
            attempt.quiz_session_id = attempt.question.quiz_session_id
            attempt.save(update_fields=["quiz_session"])


class Migration(migrations.Migration):

    dependencies = [
        ("exam_assistant", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="QuizSession",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("exam", models.CharField(max_length=100)),
                ("subject", models.CharField(max_length=100)),
                ("topics", models.CharField(max_length=300)),
                ("difficulty", models.CharField(max_length=20)),
                ("score", models.PositiveIntegerField(default=0)),
                ("total_questions", models.PositiveIntegerField(default=20)),
                ("performance_review", models.TextField(blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "user",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
                ),
            ],
        ),
        migrations.CreateModel(
            name="UserProfile",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("full_name", models.CharField(blank=True, max_length=150)),
                ("profile_photo", models.URLField(blank=True)),
                (
                    "target_exam",
                    models.CharField(
                        choices=[
                            ("UPSC", "UPSC"),
                            ("SSC", "SSC"),
                            ("Banking", "Banking"),
                            ("Railways", "Railways"),
                            ("State PSC", "State PSC"),
                        ],
                        default="UPSC",
                        max_length=50,
                    ),
                ),
                (
                    "user",
                    models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
                ),
            ],
        ),
        migrations.CreateModel(
            name="MindMap",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("exam", models.CharField(max_length=100)),
                ("subject", models.CharField(max_length=100)),
                ("topic", models.CharField(max_length=200)),
                ("content", models.TextField()),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "user",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
                ),
            ],
        ),
        migrations.AddField(
            model_name="question",
            name="quiz_session",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="questions",
                to="exam_assistant.quizsession",
            ),
        ),
        migrations.AddField(
            model_name="attempt",
            name="quiz_session",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="attempts",
                to="exam_assistant.quizsession",
            ),
        ),
        migrations.RunPython(backfill_quiz_sessions, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="question",
            name="quiz_session",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="questions",
                to="exam_assistant.quizsession",
            ),
        ),
        migrations.AlterField(
            model_name="attempt",
            name="quiz_session",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="attempts",
                to="exam_assistant.quizsession",
            ),
        ),
        migrations.AlterField(
            model_name="question",
            name="explanation",
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name="attempt",
            name="selected_option",
            field=models.CharField(blank=True, max_length=1),
        ),
        migrations.AlterField(
            model_name="attempt",
            name="is_correct",
            field=models.BooleanField(default=False),
        ),
    ]
