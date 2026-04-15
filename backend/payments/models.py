"""
Payment and Transaction Models
"""

from django.db import models
from django.conf import settings
from appointments.models import Appointment
from consultations.models import Consultation

class Payment(models.Model):
    """
    Payment transactions for appointments and consultations
    """
    
    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
        ('REFUNDED', 'Refunded'),
    )
    
    PAYMENT_METHOD_CHOICES = (
        ('PAYPAL', 'PayPal'),
        ('STRIPE', 'Stripe'),
        ('CARD', 'Credit/Debit Card'),
        ('UPI', 'UPI'),
        ('WALLET', 'Wallet'),
    )
    
    # Relationships
    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE, related_name='payments')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='payments')
    
    # Payment Details
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, default='PAYPAL')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    
    # Transaction
    transaction_id = models.CharField(max_length=200, unique=True, blank=True, null=True)
    paypal_order_id = models.CharField(max_length=200, blank=True, null=True)
    
    # Details
    description = models.TextField(blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    paid_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        db_table = 'payments'
        verbose_name = 'Payment'
        verbose_name_plural = 'Payments'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Payment #{self.id} - {self.user.username} - {self.amount}"


class Refund(models.Model):
    """
    Refund requests and processing
    """
    
    STATUS_CHOICES = (
        ('REQUESTED', 'Requested'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
        ('COMPLETED', 'Completed'),
    )
    
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, related_name='refunds')
    
    # Refund Details
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='REQUESTED')
    
    # Admin Notes
    admin_notes = models.TextField(blank=True, null=True)
    processed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='processed_refunds')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        db_table = 'refunds'
        verbose_name = 'Refund'
        verbose_name_plural = 'Refunds'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Refund #{self.id} - Payment #{self.payment.id}"
