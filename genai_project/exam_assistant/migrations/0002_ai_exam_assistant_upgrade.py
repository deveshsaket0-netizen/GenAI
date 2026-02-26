from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


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
                default=1,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="questions",
                to="exam_assistant.quizsession",
            ),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="question",
            name="explanation",
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name="attempt",
            name="quiz_session",
            field=models.ForeignKey(
                default=1,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="attempts",
                to="exam_assistant.quizsession",
            ),
            preserve_default=False,
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
