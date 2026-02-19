"""
Payment URL configuration.
"""
from django.urls import path
from .views import (
    CreatePaymentIntentView,
    PaymentDetailView,
    MyPaymentsView,
    PaymentStatusView,
)


app_name = 'payments'

urlpatterns = [
    # Create payment intent
    path(
        'create-intent/',
        CreatePaymentIntentView.as_view(),
        name='create-intent'
    ),
    
    # Get my payments
    path(
        'my-payments/',
        MyPaymentsView.as_view(),
        name='my-payments'
    ),
    
    # Payment detail by intent ID
    path(
        '<str:payment_intent_id>/',
        PaymentDetailView.as_view(),
        name='payment-detail'
    ),
    
    # Check payment status
    path(
        '<str:payment_intent_id>/status/',
        PaymentStatusView.as_view(),
        name='payment-status'
    ),
]