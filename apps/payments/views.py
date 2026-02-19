"""
Payment views - thin controllers using service layer.
"""
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, OpenApiParameter
from django.shortcuts import get_object_or_404

from .models import Payment
from .serializers import (
    PaymentSerializer,
    CreatePaymentIntentSerializer,
    PaymentStatusSerializer
)
from .services import PaymentService
from apps.orders.models import Order


class CreatePaymentIntentView(APIView):
    """
    Create a Stripe Payment Intent for an order.
    """
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        request=CreatePaymentIntentSerializer,
        responses={201: PaymentStatusSerializer},
        description="Create a payment intent for an order"
    )
    def post(self, request):
        """
        Create payment intent.
        
        Required: order_id
        Returns: client_secret for frontend Stripe integration
        """
        serializer = CreatePaymentIntentSerializer(
            data=request.data,
            context={'request': request}
        )
        
        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get order
        order = get_object_or_404(
            Order.objects.select_related('user'),
            id=serializer.validated_data['order_id']
        )
        
        try:
            # Use service layer
            payment_data = PaymentService.create_payment_intent(
                order=order,
                user=request.user
            )
            
            return Response(
                payment_data,
                status=status.HTTP_201_CREATED
            )
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class PaymentDetailView(APIView):
    """
    Get payment details by Payment Intent ID.
    """
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        responses={200: PaymentSerializer},
        description="Get payment details"
    )
    def get(self, request, payment_intent_id):
        """
        Retrieve payment by Stripe Payment Intent ID.
        """
        payment = get_object_or_404(
            Payment.objects.select_related('order', 'user'),
            stripe_payment_intent_id=payment_intent_id,
            user=request.user  # Ensure user owns payment
        )
        
        serializer = PaymentSerializer(payment)
        return Response(serializer.data)


class MyPaymentsView(APIView):
    """
    List all payments for authenticated user.
    """
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        responses={200: PaymentSerializer(many=True)},
        description="Get all user payments"
    )
    def get(self, request):
        """
        Get all payments for current user.
        """
        payments = Payment.objects.filter(
            user=request.user
        ).select_related('order').order_by('-created_at')
        
        serializer = PaymentSerializer(payments, many=True)
        return Response(serializer.data)


class PaymentStatusView(APIView):
    """
    Check payment status from Stripe.
    """
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        responses={200: PaymentStatusSerializer},
        description="Check payment status from Stripe"
    )
    def get(self, request, payment_intent_id):
        """
        Get current payment status from Stripe API.
        """
        # Verify user owns this payment
        payment = get_object_or_404(
            Payment.objects.select_related('user'),
            stripe_payment_intent_id=payment_intent_id,
            user=request.user
        )
        
        try:
            status_data = PaymentService.get_payment_status(payment_intent_id)
            return Response(status_data)
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )