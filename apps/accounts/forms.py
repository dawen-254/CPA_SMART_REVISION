from django import forms
from .models import StudentProfile


class StudentProfileForm(forms.ModelForm):
    class Meta:
        model = StudentProfile
        fields = [
            'current_level',
            'current_part',
            'exam_date',
            'institution',
            'student_id',
            'bio',
            'avatar',
            'daily_study_goal_minutes',
            'preferred_study_time'
        ]
        widgets = {
            'current_level': forms.Select(attrs={
                'class': 'form-select bg-light'
            }),
            'current_part': forms.Select(attrs={
                'class': 'form-select bg-light'
            }),
            'exam_date': forms.DateInput(attrs={
                'class': 'form-control bg-light',
                'type': 'date'
            }),
            'institution': forms.TextInput(attrs={
                'class': 'form-control bg-light',
                'placeholder': 'Your institution name'
            }),
            'student_id': forms.TextInput(attrs={
                'class': 'form-control bg-light',
                'placeholder': 'Your student ID'
            }),
            'bio': forms.Textarea(attrs={
                'class': 'form-control bg-light',
                'rows': 4,
                'placeholder': 'Tell us about yourself'
            }),
            'avatar': forms.FileInput(attrs={
                'class': 'form-control bg-light'
            }),
            'daily_study_goal_minutes': forms.NumberInput(attrs={
                'class': 'form-control bg-light',
                'min': '15',
                'step': '15'
            }),
            'preferred_study_time': forms.Select(attrs={
                'class': 'form-select bg-light'
            }),
        }