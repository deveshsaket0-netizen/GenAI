from django import forms


class GenerateForm(forms.Form):
    EXAM_CHOICES = (
        ('SSC CGL', 'SSC CGL'),
        ('UPSC', 'UPSC'),
        ('Banking', 'Banking'),
    )

    DIFFICULTY_CHOICES = (
        ('Easy', 'Easy'),
        ('Medium', 'Medium'),
        ('Hard', 'Hard'),
    )

    exam = forms.ChoiceField(choices=EXAM_CHOICES, required=True)
    subject = forms.CharField(max_length=100, required=True)
    topic = forms.CharField(max_length=100, required=True)
    difficulty = forms.ChoiceField(choices=DIFFICULTY_CHOICES, required=True)