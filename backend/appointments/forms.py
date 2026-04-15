from django import forms
from .models import Appointment
from doctors.models import DoctorAvailability
import datetime

class AppointmentBookingForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['appointment_date', 'appointment_time', 'consultation_type', 'urgency_level', 'symptoms', 'attachment']
        widgets = {
            'appointment_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'appointment_time': forms.HiddenInput(),
            'consultation_type': forms.Select(attrs={'class': 'form-select'}),
            'urgency_level': forms.Select(attrs={'class': 'form-select'}),
            'reason': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Reason for visit...'}),
            'symptoms': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Describe your symptoms (optional)...'}),
            'attachment': forms.FileInput(attrs={'class': 'form-control'}),
        }

    def clean_appointment_date(self):
        date = self.cleaned_data.get('appointment_date')
        if date < datetime.date.today():
            raise forms.ValidationError("Appointment date cannot be in the past.")
        return date
