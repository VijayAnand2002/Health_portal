from django.contrib import admin
from .models import Payment, Refund

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'appointment', 'amount', 'payment_method', 'status', 'paid_at', 'created_at')
    list_filter = ('status', 'payment_method', 'created_at')
    search_fields = ('user__username', 'transaction_id', 'paypal_order_id')
    date_hierarchy = 'created_at'


@admin.register(Refund)
class RefundAdmin(admin.ModelAdmin):
    list_display = ('id', 'payment', 'amount', 'status', 'created_at', 'completed_at')
    list_filter = ('status', 'created_at')
    search_fields = ('payment__transaction_id', 'reason')
    actions = ['approve_refunds', 'reject_refunds']
    
    def approve_refunds(self, request, queryset):
        queryset.update(status='APPROVED')
        self.message_user(request, 'Selected refunds have been approved.')
    approve_refunds.short_description = 'Approve selected refunds'
    
    def reject_refunds(self, request, queryset):
        queryset.update(status='REJECTED')
        self.message_user(request, 'Selected refunds have been rejected.')
    reject_refunds.short_description = 'Reject selected refunds'
