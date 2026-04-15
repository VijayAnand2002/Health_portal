from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('checkout/<int:appointment_id>/', views.initiate_payment_view, name='initiate_payment'),
    path('create-checkout-session/<int:appointment_id>/', views.create_checkout_session, name='create_checkout_session'),
    path('success/', views.payment_success_view, name='success'),
    path('cancel/', views.payment_cancel_view, name='cancel'),
    path('receipt/<int:payment_id>/', views.download_receipt, name='download_receipt'),
    path('webhook/', views.stripe_webhook, name='webhook'),
]
