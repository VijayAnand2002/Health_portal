from django.urls import path
from . import views

app_name = 'hospitals'

urlpatterns = [
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('manage-doctors/', views.manage_doctors_view, name='manage_doctors'),
    path('edit-profile/', views.edit_hospital_profile_view, name='edit_profile'),
    path('add-doctor/', views.add_doctor_view, name='add_doctor'),
    path('appointments/', views.hospital_appointments_view, name='appointments'),
    path('appointments/<int:appointment_id>/approve/', views.approve_appointment_view, name='approve_appointment'),
    path('appointments/<int:appointment_id>/reject/', views.reject_appointment_view, name='reject_appointment'),
]
