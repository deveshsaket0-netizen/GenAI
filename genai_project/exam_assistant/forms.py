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


class MindMapForm(forms.Form):
    subject = forms.CharField(max_length=100, required=True)
    topic = forms.CharField(max_length=200, required=True)


class ProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ["full_name", "profile_photo", "target_exam"]
