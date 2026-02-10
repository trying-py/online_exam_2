from django import forms
from .models import Exam


class ExamForm(forms.ModelForm):
    class Meta:
        model = Exam
        fields = ['title', 'subject', 'total_score',
                  'start_time', 'duration_minutes']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'عنوان آزمون'}),
            'subject': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'موضوع آزمون'}),
            'total_score': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'start_time': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'duration_minutes': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
        }
