from django.contrib import admin
from .models import Hospital

@admin.register(Hospital)
class HospitalAdmin(admin.ModelAdmin):
    list_display = ('name', 'city', 'is_verified', 'is_active', 'rating', 'created_at')
    list_filter = ('is_verified', 'is_active', 'city', 'state')
    search_fields = ('name', 'registration_number', 'city')
    actions = ['verify_hospitals', 'unverify_hospitals']
    
    def verify_hospitals(self, request, queryset):
        queryset.update(is_verified=True)
        self.message_user(request, 'Selected hospitals have been verified.')
    verify_hospitals.short_description = 'Verify selected hospitals'
    
    def unverify_hospitals(self, request, queryset):
        queryset.update(is_verified=False)
        self.message_user(request, 'Selected hospitals have been unverified.')
    unverify_hospitals.short_description = 'Unverify selected hospitals'
