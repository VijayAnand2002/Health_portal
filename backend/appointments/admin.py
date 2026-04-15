from django.contrib import admin
from .models import Appointment

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'patient', 'doctor', 'appointment_date', 'appointment_time', 'status', 'is_paid', 'created_at')
    list_filter = ('status', 'is_paid', 'appointment_date', 'created_at')
    search_fields = ('patient__user__username', 'doctor__user__username', 'reason')
    date_hierarchy = 'appointment_date'
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('patient__user', 'doctor__user')
