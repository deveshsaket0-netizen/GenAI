from django import forms
from .models import EXAM_CHOICES, UserProfile


DIFFICULTY_CHOICES = (
    ("Easy", "Easy"),
    ("Medium", "Medium"),
    ("Hard", "Hard"),
)


class GenerateForm(forms.Form):
    exam = forms.ChoiceField(choices=EXAM_CHOICES, required=True)
    subject = forms.CharField(max_length=100, required=True)
    topics = forms.CharField(
        max_length=250,
        required=True,
        help_text="Add multiple topics separated by commas.",
    )
    difficulty = forms.ChoiceField(choices=DIFFICULTY_CHOICES, required=True)


class PDFQuizForm(forms.Form):
    pdf_file = forms.FileField(
        label="Upload PDF",
        help_text="Upload a PDF and we'll generate quiz questions from its content.",
    )
    num_questions = forms.ChoiceField(
        choices=[("3", "3 questions"), ("5", "5 questions"), ("8", "8 questions")],
        initial="5",
        label="Number of questions",
    )
    difficulty = forms.ChoiceField(choices=DIFFICULTY_CHOICES, required=True)

    def clean_pdf_file(self):
        f = self.cleaned_data["pdf_file"]
        if not f.name.endswith(".pdf"):
            raise forms.ValidationError("Only PDF files are supported.")
        if f.size > 5 * 1024 * 1024:  # 5 MB limit
            raise forms.ValidationError("PDF must be under 5 MB.")
        return f


class MindMapForm(forms.Form):
    subject = forms.CharField(max_length=100, required=True)
    topic = forms.CharField(max_length=200, required=True)


class ProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ["full_name", "profile_photo", "target_exam"]