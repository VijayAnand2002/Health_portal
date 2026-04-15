from django import forms
from .models import Hospital
from doctors.models import DoctorProfile

class HospitalProfileForm(forms.ModelForm):
    class Meta:
        model = Hospital
        fields = [
            'name', 'email', 'phone', 'address_line1', 'address_line2',
            'city', 'state', 'pincode', 'description', 'facilities',
            'specializations', 'logo'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'address_line1': forms.TextInput(attrs={'class': 'form-control'}),
            'address_line2': forms.TextInput(attrs={'class': 'form-control'}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'state': forms.TextInput(attrs={'class': 'form-control'}),
            'pincode': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'facilities': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. ICU, Emergency, Pharmacy'}),
            'specializations': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Cardiology, Pediatrics'}),
            'logo': forms.FileInput(attrs={'class': 'form-control'}),
        }

class AddDoctorForm(forms.Form):
    license_number = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Doctor License Number'})
    )
