"""
Payment serializers with strict validation.
"""
from rest_framework import serializers
from decimal import Decimal
from .models import Payment


class PaymentSerializer(serializers.ModelSerializer):
    """
    Read-only serializer for payment details.
    """
    order_id = serializers.IntegerField(source='order.id', read_only=True)
    user_email = serializers.EmailField(source='user.email', read_only=True)
    
    class Meta:
        model = Payment
        fields = [
            'id',
            'order_id',
            'user_email',
            'stripe_payment_intent_id',
            'stripe_charge_id',
            'amount',
            'currency',
            'status',
            'payment_method_type',
            'failure_message',
            'created_at',
            'updated_at',
        ]
        read_only_fields = fields


class CreatePaymentIntentSerializer(serializers.Serializer):
    """
    Validate payment intent creation request.
    Strict validation following Django/DRF best practices.
    """
    order_id = serializers.IntegerField(min_value=1)
    
    def validate_order_id(self, value: int) -> int:
        """
        Ensure order exists and belongs to requesting user.
        """
        from apps.orders.models import Order
        
        request = self.context.get('request')
        if not request:
            raise serializers.ValidationError("Request context required")
        
        try:
            order = Order.objects.select_related('user').get(id=value)
        except Order.DoesNotExist:
            raise serializers.ValidationError("Order not found")
        
        # Verify ownership
        if order.user != request.user:
            raise serializers.ValidationError("Order does not belong to you")
        
        # Check if already paid
        if hasattr(order, 'payment') and order.payment.status == Payment.PaymentStatus.SUCCEEDED:
            raise serializers.ValidationError("Order already paid")
        
        # Verify order status
        if order.status == Order.OrderStatus.CANCELED:
            raise serializers.ValidationError("Cannot pay for canceled order")
        
        return value
    
    def validate(self, attrs: dict) -> dict:
        """
        Additional validation at serializer level.
        """
        from apps.orders.models import Order
        
        order = Order.objects.get(id=attrs['order_id'])
        
        # Validate amount
        if order.total_amount <= Decimal('0'):
            raise serializers.ValidationError(
                {"order_id": "Order total must be greater than zero"}
            )
        
        return attrs


class PaymentStatusSerializer(serializers.Serializer):
    """
    Read-only serializer for payment status checks.
    """
    payment_intent_id = serializers.CharField(read_only=True)
    status = serializers.CharField(read_only=True)
    amount = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        read_only=True
    )
    created_at = serializers.DateTimeField(read_only=True)