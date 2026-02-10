from django import forms
from .models import Question, Choice


class QuestionForm(forms.ModelForm):
    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user is not None and getattr(user, 'role', None) == 'instructor':
            from exams.models import Exam
            self.fields['exam'].queryset = Exam.objects.by_instructor(user)

    class Meta:
        model = Question
        fields = ['exam', 'text', 'question_type', 'score']
        widgets = {
            'exam': forms.Select(attrs={'class': 'form-select'}),
            'text': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'متن سؤال'}),
            'question_type': forms.Select(attrs={'class': 'form-select'}),
            'score': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
        }


class ChoiceForm(forms.ModelForm):
    class Meta:
        model = Choice
        fields = ['question', 'text', 'is_correct']
        widgets = {
            'question': forms.Select(attrs={'class': 'form-select'}),
            'text': forms.TextInput(attrs={'class': 'form-control'}),
            'is_correct': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
