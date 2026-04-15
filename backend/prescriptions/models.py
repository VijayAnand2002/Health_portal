"""
Prescription and Medical Records Models
"""

from django.db import models
from consultations.models import Consultation
from appointments.models import Appointment
from patients.models import PatientProfile
from doctors.models import DoctorProfile

class Prescription(models.Model):
    """
    Digital prescription issued by doctor
    """
    
    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE, related_name='prescriptions', null=True, blank=True)
    consultation = models.ForeignKey(Consultation, on_delete=models.CASCADE, related_name='prescriptions', null=True, blank=True)
    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE, related_name='prescriptions')
    doctor = models.ForeignKey(DoctorProfile, on_delete=models.CASCADE, related_name='prescriptions')
    
    # Access control
    is_private = models.BooleanField(default=False, help_text="If true, only doctor can see this")
    
    # Diagnosis
    diagnosis = models.TextField()
    symptoms = models.TextField(blank=True, null=True)
    
    # Medications (JSON format: [{"name": "...", "dosage": "...", "frequency": "...", "duration": "..."}])
    medications = models.JSONField(default=list)
    
    # Additional Instructions
    instructions = models.TextField(blank=True, null=True)
    follow_up_date = models.DateField(blank=True, null=True)
    
    # Lab Tests
    lab_tests = models.TextField(blank=True, null=True, help_text="Recommended lab tests")
    
    # Digital Signature
    doctor_signature = models.ImageField(upload_to='signatures/', blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'prescriptions'
        verbose_name = 'Prescription'
        verbose_name_plural = 'Prescriptions'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Prescription #{self.id} - {self.patient.user.username}"


class MedicalRecord(models.Model):
    """
    Patient's medical records and documents
    """
    
    RECORD_TYPE_CHOICES = (
        ('PRESCRIPTION', 'Prescription'),
        ('LAB_REPORT', 'Lab Report'),
        ('XRAY', 'X-Ray'),
        ('MRI', 'MRI'),
        ('CT_SCAN', 'CT Scan'),
        ('OTHER', 'Other'),
    )
    
    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE, related_name='medical_records')
    consultation = models.ForeignKey(Consultation, on_delete=models.SET_NULL, null=True, blank=True, related_name='medical_records')
    
    # Record Details
    record_type = models.CharField(max_length=20, choices=RECORD_TYPE_CHOICES)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    
    # File
    document = models.FileField(upload_to='medical_records/')
    
    # Uploaded by
    uploaded_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True)
    
    # Timestamps
    record_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'medical_records'
        verbose_name = 'Medical Record'
        verbose_name_plural = 'Medical Records'
        ordering = ['-record_date']
    
    def __str__(self):
        return f"{self.get_record_type_display()} - {self.patient.user.username}"
