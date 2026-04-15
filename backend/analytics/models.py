"""
Analytics and Reporting Models
"""

from django.db import models
from django.conf import settings

class SystemAnalytics(models.Model):
    """
    Daily system analytics and statistics
    """
    
    # Date
    date = models.DateField(unique=True)
    
    # User Stats
    total_users = models.IntegerField(default=0)
    new_users = models.IntegerField(default=0)
    active_users = models.IntegerField(default=0)
    total_patients = models.IntegerField(default=0)
    total_doctors = models.IntegerField(default=0)
    
    # Appointment Stats
    total_appointments = models.IntegerField(default=0)
    completed_appointments = models.IntegerField(default=0)
    cancelled_appointments = models.IntegerField(default=0)
    
    # Consultation Stats
    total_consultations = models.IntegerField(default=0)
    completed_consultations = models.IntegerField(default=0)
    
    # Revenue Stats
    total_revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    total_payments = models.IntegerField(default=0)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'system_analytics'
        verbose_name = 'System Analytics'
        verbose_name_plural = 'System Analytics'
        ordering = ['-date']
    
    def __str__(self):
        return f"Analytics for {self.date}"


class ActivityLog(models.Model):
    """
    User activity logging for audit trail
    """
    
    ACTION_CHOICES = (
        ('LOGIN', 'Login'),
        ('LOGOUT', 'Logout'),
        ('CREATE', 'Create'),
        ('UPDATE', 'Update'),
        ('DELETE', 'Delete'),
        ('VIEW', 'View'),
    )
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='activity_logs')
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    entity_type = models.CharField(max_length=50, blank=True, null=True)  # e.g., 'Appointment', 'Prescription'
    entity_id = models.IntegerField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True, null=True)
    
    # Timestamp
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'activity_logs'
        verbose_name = 'Activity Log'
        verbose_name_plural = 'Activity Logs'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username if self.user else 'Unknown'} - {self.action} - {self.created_at}"
