from django.contrib import admin
from .models import Consultation

@admin.register(Consultation)
class ConsultationAdmin(admin.ModelAdmin):
    list_display = ('id', 'appointment', 'room_id', 'status', 'start_time', 'end_time', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('room_id', 'appointment__patient__user__username', 'appointment__doctor__user__username')
