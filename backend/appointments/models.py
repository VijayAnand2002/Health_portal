"""
Appointment Model
"""

from django.db import models
from django.conf import settings
from doctors.models import DoctorProfile
from patients.models import PatientProfile

class Appointment(models.Model):
    """
    Appointment booking and management
    """
    
    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('CONFIRMED', 'Confirmed'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
        ('NO_SHOW', 'No Show'),
    )
    
    # Relationships
    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE, related_name='appointments')
    doctor = models.ForeignKey(DoctorProfile, on_delete=models.CASCADE, related_name='appointments')
    
    # Appointment Details
    appointment_date = models.DateField()
    appointment_time = models.TimeField(blank=True, null=True)
    duration = models.IntegerField(default=30, help_text="Duration in minutes")
    
    CONSULTATION_TYPES = (
        ('VIDEO', 'Video Consultation'),
        ('AUDIO', 'Audio Consultation'),
        ('CLINIC', 'Clinic Visit'),
    )
    consultation_type = models.CharField(max_length=20, choices=CONSULTATION_TYPES, default='CLINIC')
    
    URGENCY_LEVELS = (
        ('ROUTINE', 'Routine Checkup'),
        ('URGENT', 'Urgent Attention'),
        ('EMERGENCY', 'Emergency (Immediate)'),
    )
    urgency_level = models.CharField(max_length=20, choices=URGENCY_LEVELS, default='ROUTINE')
    
    # Attachments
    attachment = models.FileField(upload_to='appointments/attachments/', blank=True, null=True)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    
    # Reason and Notes
    reason = models.TextField(help_text="Reason for consultation", blank=True, null=True)
    symptoms = models.TextField(blank=True, null=True)
    doctor_notes = models.TextField(blank=True, null=True)
    
    # Payment
    consultation_fee = models.DecimalField(max_digits=10, decimal_places=2)
    is_paid = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    cancelled_at = models.DateTimeField(blank=True, null=True)
    cancellation_reason = models.TextField(blank=True, null=True)
    
    class Meta:
        db_table = 'appointments'
        verbose_name = 'Appointment'
        verbose_name_plural = 'Appointments'
        ordering = ['-appointment_date', '-appointment_time']
    
    def __str__(self):
        return f"Appointment #{self.id} - {self.patient.user.username} with Dr. {self.doctor.user.username}"
    
    @property
    def is_upcoming(self):
        from datetime import datetime, date, time
        now = datetime.now()
        appointment_datetime = datetime.combine(self.appointment_date, self.appointment_time)
        return appointment_datetime > now and self.status in ['PENDING', 'CONFIRMED']
    
    @property
    def is_past(self):
        from datetime import datetime
        now = datetime.now()
        appointment_datetime = datetime.combine(self.appointment_date, self.appointment_time)
        return appointment_datetime < now
