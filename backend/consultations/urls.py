from django.urls import path
from . import views

app_name = 'consultations'

urlpatterns = [
    path('start/<int:appointment_id>/', views.start_consultation_view, name='start'),
    path('room/<str:room_id>/', views.join_consultation_view, name='room'),
    path('end/<str:room_id>/', views.end_consultation_view, name='end'),
]
