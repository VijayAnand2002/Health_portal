from django.urls import path
from . import views

app_name = 'prescriptions'

urlpatterns = [
    path('create/<int:appointment_id>/', views.create_prescription_view, name='create_prescription'),
    path('view/<int:prescription_id>/', views.view_prescription_view, name='view_prescription'),
    path('my-records/', views.patient_records_view, name='patient_records'),
    path('download/<int:prescription_id>/', views.download_prescription_pdf, name='download_pdf'),
]
