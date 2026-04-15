from django.contrib import admin
from .models import DoctorProfile, DoctorAvailability

@admin.register(DoctorProfile)
class DoctorProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'specialization', 'experience_years', 'consultation_fee', 'is_verified', 'is_available')
    list_filter = ('specialization', 'is_verified', 'is_available', 'created_at')
    search_fields = ('user__username', 'user__email', 'license_number', 'specialization')
    actions = ['verify_doctors', 'unverify_doctors']
    
    def verify_doctors(self, request, queryset):
        queryset.update(is_verified=True)
        self.message_user(request, 'Selected doctors have been verified.')
    verify_doctors.short_description = 'Verify selected doctors'
    
    def unverify_doctors(self, request, queryset):
        queryset.update(is_verified=False)
        self.message_user(request, 'Selected doctors have been unverified.')
    unverify_doctors.short_description = 'Unverify selected doctors'


@admin.register(DoctorAvailability)
class DoctorAvailabilityAdmin(admin.ModelAdmin):
    list_display = ('doctor', 'day', 'start_time', 'end_time', 'is_available')
    list_filter = ('day', 'is_available')
    search_fields = ('doctor__user__username',)
