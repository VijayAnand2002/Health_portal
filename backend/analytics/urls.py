from django.urls import path
from . import views

app_name = 'analytics'

urlpatterns = [
    path('reports/', views.reports_view, name='reports'),
]
