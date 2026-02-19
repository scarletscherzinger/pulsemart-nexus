"""
Payment service layer - handles Stripe API interactions.
Separation of concerns: keeps business logic out of views.
"""
from decimal import Decimal
from typing import Dict, Optional

import stripe
from django.conf import settings
from django.db import transaction

from .models import Payment
from apps.orders.models import Order



# Initialize Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY


class PaymentService:
    """
    Service class for payment operations.
    Encapsulates Stripe API logic and payment processing.
    """
    
    @staticmethod
    def create_payment_intent(order: Order, user) -> Dict[str, any]:
        """
        Create a Stripe Payment Intent for an order.
        
        Args:
            order: Order instance to create payment for
            user: User making the payment
            
        Returns:
            dict: Payment intent details including client_secret
            
        Raises:
            stripe.error.StripeError: If Stripe API call fails
        """
        # Convert to cents (Stripe uses smallest currency unit)
        amount_cents = int(order.total_amount * 100)
        
        try:
            # Create Payment Intent
            intent = stripe.PaymentIntent.create(
                amount=amount_cents,
                currency='usd',
                metadata={
                    'order_id': order.id,
                    'user_id': user.id,
                    'user_email': user.email,
                },
                # Idempotency key prevents duplicate charges
                idempotency_key=f"order_{order.id}_{order.created_at.timestamp()}"
            )
            
            # Store payment record in database
            with transaction.atomic():
                payment, created = Payment.objects.update_or_create(
                    order=order,
                    defaults={
                        'user': user,
                        'stripe_payment_intent_id': intent.id,
                        'amount': order.total_amount,
                        'currency': 'usd',
                        'status': Payment.PaymentStatus.PENDING,
                    }
                )
            
            return {
                'payment_intent_id': intent.id,
                'client_secret': intent.client_secret,
                'amount': order.total_amount,
                'currency': 'usd',
                'status': intent.status,
            }
            
        except stripe.error.StripeError as e:
            raise Exception(f"Stripe error: {str(e)}")
    
    @staticmethod
    def get_payment_status(payment_intent_id: str) -> Dict[str, any]:
        """
        Retrieve payment status from Stripe.
        
        Args:
            payment_intent_id: Stripe Payment Intent ID
            
        Returns:
            dict: Current payment status
        """
        try:
            intent = stripe.PaymentIntent.retrieve(payment_intent_id)
            
            return {
                'payment_intent_id': intent.id,
                'status': intent.status,
                'amount': Decimal(intent.amount) / 100,
                'currency': intent.currency,
            }
            
        except stripe.error.StripeError as e:
            raise Exception(f"Failed to retrieve payment: {str(e)}")
    
    @staticmethod
    @transaction.atomic
    def handle_payment_success(payment_intent_id: str) -> Optional[Payment]:
        """
        Handle successful payment (called from webhook).
        Updates payment and order status.
        
        Args:
            payment_intent_id: Stripe Payment Intent ID
            
        Returns:
            Payment: Updated payment instance
        """
        try:
            payment = Payment.objects.select_related('order').get(
                stripe_payment_intent_id=payment_intent_id
            )
            
            # Update payment status
            payment.status = Payment.PaymentStatus.SUCCEEDED
            payment.save(update_fields=['status', 'updated_at'])
            
            # Update order status
            order = payment.order
            order.status = Order.OrderStatus.PROCESSING
            order.save(update_fields=['status', 'updated_at'])
            
            return payment
            
        except Payment.DoesNotExist:
            return None
    
    @staticmethod
    @transaction.atomic
    def handle_payment_failure(
        payment_intent_id: str,
        failure_message: str
    ) -> Optional[Payment]:
        """
        Handle failed payment (called from webhook).
        
        Args:
            payment_intent_id: Stripe Payment Intent ID
            failure_message: Reason for failure
            
        Returns:
            Payment: Updated payment instance
        """
        try:
            payment = Payment.objects.get(
                stripe_payment_intent_id=payment_intent_id
            )
            
            payment.status = Payment.PaymentStatus.FAILED
            payment.failure_message = failure_message
            payment.save(update_fields=['status', 'failure_message', 'updated_at'])
            
            return payment
            
        except Payment.DoesNotExist:
            return None