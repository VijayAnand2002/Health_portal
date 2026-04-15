from django.contrib import admin
from .models import SystemAnalytics, ActivityLog

@admin.register(SystemAnalytics)
class SystemAnalyticsAdmin(admin.ModelAdmin):
    list_display = ('date', 'total_users', 'new_users', 'total_appointments', 'total_revenue', 'created_at')
    list_filter = ('date', 'created_at')
    search_fields = ('date',)
    date_hierarchy = 'date'


@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'action', 'entity_type', 'entity_id', 'ip_address', 'created_at')
    list_filter = ('action', 'entity_type', 'created_at')
    search_fields = ('user__username', 'description', 'ip_address')
    date_hierarchy = 'created_at'
