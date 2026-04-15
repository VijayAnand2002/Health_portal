from django import forms
from .models import Prescription, MedicalRecord

class PrescriptionForm(forms.ModelForm):
    # Medications will be handled dynamically in the template as JSON
    class Meta:
        model = Prescription
        fields = ['diagnosis', 'instructions', 'follow_up_date', 'is_private']
        widgets = {
            'diagnosis': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Final diagnosis...'}),
            'instructions': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Medication instructions, lifestyle advice, etc.'}),
            'follow_up_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'is_private': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class MedicalRecordForm(forms.ModelForm):
    class Meta:
        model = MedicalRecord
        fields = ['record_type', 'title', 'document', 'record_date', 'description']
        widgets = {
            'record_type': forms.Select(attrs={'class': 'form-select'}),
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Blood Test Report'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'document': forms.FileInput(attrs={'class': 'form-control'}),
            'record_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }
