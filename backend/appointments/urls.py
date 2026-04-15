from django.urls import path
from . import views

app_name = 'appointments'

urlpatterns = [
    path('book/<int:doctor_id>/', views.book_appointment_view, name='book_appointment'),
    path('<int:appointment_id>/', views.appointment_detail_view, name='appointment_detail'),
    path('edit/<int:appointment_id>/', views.edit_appointment_view, name='edit_appointment'),
    path('delete/<int:appointment_id>/', views.delete_appointment_view, name='delete_appointment'),
]
