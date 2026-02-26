from django.conf import settings
from django.db import models


EXAM_CHOICES = (
    ("UPSC", "UPSC"),
    ("SSC", "SSC"),
    ("Banking", "Banking"),
    ("Railways", "Railways"),
    ("State PSC", "State PSC"),
)


class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=150, blank=True)
    profile_photo = models.URLField(blank=True)
    target_exam = models.CharField(max_length=50, choices=EXAM_CHOICES, default="UPSC")

    def __str__(self):
        return self.full_name or self.user.username


class QuizSession(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    exam = models.CharField(max_length=100)
    subject = models.CharField(max_length=100)
    topics = models.CharField(max_length=300)
    difficulty = models.CharField(max_length=20)
    score = models.PositiveIntegerField(default=0)
    total_questions = models.PositiveIntegerField(default=20)
    performance_review = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.subject} ({self.created_at.date()})"


class Question(models.Model):
    quiz_session = models.ForeignKey(QuizSession, on_delete=models.CASCADE, related_name="questions")
    exam = models.CharField(max_length=100)
    subject = models.CharField(max_length=100)
    topic = models.CharField(max_length=100)
    difficulty = models.CharField(max_length=20)
    question_text = models.TextField()
    option_a = models.CharField(max_length=300)
    option_b = models.CharField(max_length=300)
    option_c = models.CharField(max_length=300)
    option_d = models.CharField(max_length=300)
    correct_answer = models.CharField(max_length=1)
    explanation = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.question_text[:50]


class Attempt(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    quiz_session = models.ForeignKey(QuizSession, on_delete=models.CASCADE, related_name="attempts")
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_option = models.CharField(max_length=1, blank=True)
    is_correct = models.BooleanField(default=False)
    attempted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - Q{self.question.id}"


class MindMap(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    exam = models.CharField(max_length=100)
    subject = models.CharField(max_length=100)
    topic = models.CharField(max_length=200)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.subject}: {self.topic}"
