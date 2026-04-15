from django.urls import path
from . import views

app_name = 'patients'

urlpatterns = [
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('hospitals/', views.search_hospitals_view, name='search_hospitals'),
    path('hospitals/<int:hospital_id>/doctors/', views.hospital_doctors_view, name='hospital_doctors'),
    path('doctors/', views.search_doctors_view, name='search_doctors'),
    path('profile/', views.patient_profile_view, name='profile'),
    path('profile/edit-personal/', views.edit_personal_details_view, name='edit_personal_details'),
    path('profile/update-medical/', views.update_medical_history_view, name='update_medical_history'),
]
