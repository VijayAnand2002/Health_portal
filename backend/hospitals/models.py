"""
Hospital Model
"""

from django.db import models
from django.conf import settings

class Hospital(models.Model):
    """
    Hospital information and management
    """
    
    name = models.CharField(max_length=200)
    registration_number = models.CharField(max_length=50, unique=True)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    
    # Address
    address_line1 = models.CharField(max_length=200)
    address_line2 = models.CharField(max_length=200, blank=True, null=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    pincode = models.CharField(max_length=10)
    country = models.CharField(max_length=100, default='India')
    
    # Details
    description = models.TextField(blank=True, null=True)
    facilities = models.TextField(blank=True, null=True, help_text="Available facilities (comma separated)")
    specializations = models.TextField(blank=True, null=True, help_text="Medical specializations (comma separated)")
    
    # Admin
    admin = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='managed_hospitals')
    
    # Status
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    
    # Images
    logo = models.ImageField(upload_to='hospital_logos/', blank=True, null=True)
    
    # Rating
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'hospitals'
        verbose_name = 'Hospital'
        verbose_name_plural = 'Hospitals'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name
    
    @property
    def full_address(self):
        return f"{self.address_line1}, {self.city}, {self.state} - {self.pincode}"
