from django.urls import path
from . import views

app_name = 'admin_dashboard'

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('users/', views.manage_users_view, name='manage_users'),
    path('users/doctors/', views.manage_doctors_view, name='manage_doctors'),
    path('users/patients/', views.manage_patients_view, name='manage_patients'),
    path('staff/', views.manage_staff_view, name='manage_staff'),
    path('hospitals/', views.manage_hospitals_view, name='manage_hospitals'),
    path('doctors/<int:user_id>/approve/', views.approve_doctor_view, name='approve_doctor'),
    path('doctors/<int:user_id>/review/', views.review_doctor_view, name='review_doctor'),
    path('users/<int:user_id>/toggle-status/', views.toggle_user_status_view, name='toggle_user_status'),
    path('hospitals/<int:hospital_id>/verify/', views.verify_hospital_view, name='verify_hospital'),
]
