from django.urls import path
from . import views

app_name = 'doctors'

urlpatterns = [
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('appointments/', views.manage_appointments_view, name='manage_appointments'),
    path('appointments/pending/', views.pending_appointments_view, name='pending_appointments'),
    path('appointments/<int:appointment_id>/approve/', views.approve_appointment_view, name='approve_appointment'),
    path('appointments/<int:appointment_id>/reject/', views.reject_appointment_view, name='reject_appointment'),
    path('complete-profile/', views.complete_profile_view, name='complete_profile'),
    path('pending-approval/', views.pending_approval_view, name='pending_approval'),
    path('availability/', views.manage_availability_view, name='manage_availability'),
    path('profile/', views.doctor_profile_view, name='doctor_profile'),
    path('appointments/<int:appointment_id>/slots/', views.get_available_slots_view, name='get_available_slots'),
    path('api/slots/<int:doctor_id>/', views.available_slots_api, name='available_slots_api'),
]
