"""
Doctor Profile and Availability Models
"""

from django.db import models
from django.conf import settings
from hospitals.models import Hospital

class DoctorProfile(models.Model):
    """
    Extended profile for doctors with professional information
    """
    
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='doctor_profile')
    
    # Professional Details
    specialization = models.CharField(max_length=100)
    qualifications = models.TextField(help_text="Degrees and certifications")
    license_number = models.CharField(max_length=50, unique=True)
    experience_years = models.IntegerField(default=0)
    
    # Hospital Affiliation
    hospitals = models.ManyToManyField(Hospital, related_name='doctors', blank=True)
    
    # Consultation
    consultation_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    consultation_duration = models.IntegerField(default=30, help_text="Duration in minutes")
    
    # About
    bio = models.TextField(blank=True, null=True)
    
    # Rating
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    total_consultations = models.IntegerField(default=0)
    
    # Status
    is_available = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'doctor_profiles'
        verbose_name = 'Doctor Profile'
        verbose_name_plural = 'Doctor Profiles'
    
    def __str__(self):
        return f"Dr. {self.user.get_full_name() or self.user.username} - {self.specialization}"

    def get_available_slots(self, date):
        """
        Generate available time slots for a specific date based on doctor's availability
        and existing appointments.
        """
        from datetime import datetime, timedelta, time
        from appointments.models import Appointment
        
        # Get day of week name (MONDAY, TUESDAY, etc.)
        day_name = date.strftime('%A').upper()
        
        # Get doctor's availability for that day
        availabilities = self.availability.filter(day=day_name, is_available=True)
        if not availabilities.exists():
            return []
            
        # Get existing appointments for that date
        booked_appointments = Appointment.objects.filter(
            doctor=self,
            appointment_date=date,
            status__in=['PENDING', 'CONFIRMED']
        ).values_list('appointment_time', flat=True)
        
        slots = []
        duration = self.consultation_duration
        
        for availability in availabilities:
            start_dt = datetime.combine(date, availability.start_time)
            end_dt = datetime.combine(date, availability.end_time)
            
            current_dt = start_dt
            while current_dt + timedelta(minutes=duration) <= end_dt:
                slot_time = current_dt.time()
                
                # Check if this slot is already booked
                # We check for any overlap within the duration
                is_booked = False
                for booked_time in booked_appointments:
                    if booked_time == slot_time:
                        is_booked = True
                        break
                
                if not is_booked:
                    slots.append({
                        'time': slot_time.strftime('%H:%M'),
                        'display_time': slot_time.strftime('%I:%M %p')
                    })
                
                current_dt += timedelta(minutes=duration)
                
        return slots


class DoctorAvailability(models.Model):
    """
    Doctor's weekly availability schedule
    """
    
    DAY_CHOICES = (
        ('MONDAY', 'Monday'),
        ('TUESDAY', 'Tuesday'),
        ('WEDNESDAY', 'Wednesday'),
        ('THURSDAY', 'Thursday'),
        ('FRIDAY', 'Friday'),
        ('SATURDAY', 'Saturday'),
        ('SUNDAY', 'Sunday'),
    )
    
    doctor = models.ForeignKey(DoctorProfile, on_delete=models.CASCADE, related_name='availability')
    day = models.CharField(max_length=10, choices=DAY_CHOICES)
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_available = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'doctor_availability'
        verbose_name = 'Doctor Availability'
        verbose_name_plural = 'Doctor Availabilities'
        unique_together = ['doctor', 'day', 'start_time']
    
    def __str__(self):
        return f"{self.doctor.user.username} - {self.day} ({self.start_time} - {self.end_time})"
