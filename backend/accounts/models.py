"""
Custom User Model with role-based access
"""

from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    """
    Custom User model extending Django's AbstractUser
    Supports multiple roles: PATIENT, DOCTOR, HOSPITAL_ADMIN, SYSTEM_ADMIN
    """
    
    ROLE_CHOICES = (
        ('PATIENT', 'Patient'),
        ('DOCTOR', 'Doctor'),
        ('HOSPITAL_ADMIN', 'Hospital Admin'),
        ('SYSTEM_ADMIN', 'System Admin'),
    )
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='PATIENT')
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    
    # Email verification
    email_verified = models.BooleanField(default=False)
    verification_token = models.CharField(max_length=100, blank=True, null=True)
    
    # Status
    is_approved = models.BooleanField(default=True)  # For doctor/hospital admin approval
    is_active = models.BooleanField(default=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
    
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
    
    @property
    def is_patient(self):
        return self.role == 'PATIENT'
    
    @property
    def is_doctor(self):
        return self.role == 'DOCTOR'
    
    @property
    def is_hospital_admin(self):
        return self.role == 'HOSPITAL_ADMIN'
    
    @property
    def is_system_admin(self):
        return self.role == 'SYSTEM_ADMIN'
