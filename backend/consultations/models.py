"""
Consultation Model for online video/audio consultations
"""

from django.db import models
from appointments.models import Appointment

class Consultation(models.Model):
    """
    Online consultation session with WebRTC
    """
    
    STATUS_CHOICES = (
        ('SCHEDULED', 'Scheduled'),
        ('ACTIVE', 'Active'),
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    )
    
    appointment = models.OneToOneField(Appointment, on_delete=models.CASCADE, related_name='consultation')
    
    # Room details for WebRTC
    room_id = models.CharField(max_length=100, unique=True)
    
    # Session timing
    start_time = models.DateTimeField(blank=True, null=True)
    end_time = models.DateTimeField(blank=True, null=True)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='SCHEDULED')
    
    # Notes and Summary
    consultation_notes = models.TextField(blank=True, null=True)
    diagnosis = models.TextField(blank=True, null=True)
    
    # Recording (optional)
    recording_url = models.URLField(blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'consultations'
        verbose_name = 'Consultation'
        verbose_name_plural = 'Consultations'
    
    def __str__(self):
        return f"Consultation for Appointment #{self.appointment.id}"
    
    @property
    def duration_minutes(self):
        if self.start_time and self.end_time:
            diff = self.end_time - self.start_time
            return int(diff.total_seconds() / 60)
        return 0
