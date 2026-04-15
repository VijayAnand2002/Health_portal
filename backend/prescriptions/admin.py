from django.contrib import admin
from .models import Prescription, MedicalRecord

@admin.register(Prescription)
class PrescriptionAdmin(admin.ModelAdmin):
    list_display = ('id', 'patient', 'doctor', 'diagnosis', 'created_at')
    list_filter = ('created_at', 'follow_up_date')
    search_fields = ('patient__user__username', 'doctor__user__username', 'diagnosis')
    date_hierarchy = 'created_at'


@admin.register(MedicalRecord)
class MedicalRecordAdmin(admin.ModelAdmin):
    list_display = ('id', 'patient', 'record_type', 'title', 'record_date', 'created_at')
    list_filter = ('record_type', 'record_date', 'created_at')
    search_fields = ('patient__user__username', 'title', 'description')
    date_hierarchy = 'record_date'
