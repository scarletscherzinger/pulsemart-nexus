from rest_framework import serializers
from .models import Order, OrderItem
from apps.products.serializers import ProductSerializer
from apps.products.models import Product


class OrderItemSerializer(serializers.ModelSerializer):
    """Serializer for order items (read)"""
    product = ProductSerializer(read_only=True)
    seller_name = serializers.CharField(source='seller.store_name', read_only=True)
    
    class Meta:
        model = OrderItem
        fields = (
            'id', 'product', 'seller', 'seller_name',
            'quantity', 'price_at_purchase', 'subtotal', 'created_at'
        )
        read_only_fields = (
            'id', 'seller', 'price_at_purchase', 'subtotal', 'created_at'
        )


class OrderItemCreateSerializer(serializers.Serializer):
    """Serializer for creating order items"""
    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1)
    
    def validate_product_id(self, value):
        """Validate product exists and is active"""
        try:
            product = Product.objects.get(id=value, is_active=True)
        except Product.DoesNotExist:
            raise serializers.ValidationError("Product not found or inactive")
        return value
    
    def validate_quantity(self, value):
        """Validate quantity is positive"""
        if value < 1:
            raise serializers.ValidationError("Quantity must be at least 1")
        return value


class OrderSerializer(serializers.ModelSerializer):
    """Serializer for order details (read)"""
    items = OrderItemSerializer(many=True, read_only=True)
    buyer_email = serializers.CharField(source='buyer.email', read_only=True)
    buyer_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Order
        fields = (
            'id', 'order_number', 'buyer', 'buyer_email', 'buyer_name',
            'items', 'status', 'payment_status', 'payment_method',
            'total_amount', 'shipping_address',
            'created_at', 'updated_at', 'delivered_at'
        )
        read_only_fields = (
            'id', 'order_number', 'buyer', 'total_amount',
            'created_at', 'updated_at'
        )
    
    def get_buyer_name(self, obj):
        """Get buyer's full name"""
        return f"{obj.buyer.first_name} {obj.buyer.last_name}"


class OrderCreateSerializer(serializers.Serializer):
    """Serializer for creating orders"""
    items = OrderItemCreateSerializer(many=True)
    shipping_address = serializers.JSONField()
    payment_method = serializers.CharField(max_length=50, default='card')
    
    def validate_items(self, value):
        """Validate items list is not empty"""
        if not value:
            raise serializers.ValidationError("Order must contain at least one item")
        return value
    
    def validate_shipping_address(self, value):
        """Validate shipping address has required fields"""
        required_fields = ['street', 'city', 'state', 'zip', 'country']
        for field in required_fields:
            if field not in value:
                raise serializers.ValidationError(f"Shipping address must include '{field}'")
        return value
    
    def create(self, validated_data):
        """Create order with items"""
        items_data = validated_data.pop('items')
        buyer = self.context['request'].user
        
        # Calculate total and validate stock
        total_amount = 0
        order_items = []
        
        for item_data in items_data:
            product = Product.objects.select_for_update().get(
                id=item_data['product_id']
            )
            
            # Check stock availability
            if product.stock_quantity < item_data['quantity']:
                raise serializers.ValidationError({
                    'items': f"Insufficient stock for {product.name}. Available: {product.stock_quantity}"
                })
            
            # Calculate subtotal
            subtotal = product.price * item_data['quantity']
            total_amount += subtotal
            
            order_items.append({
                'product': product,
                'quantity': item_data['quantity'],
                'price_at_purchase': product.price,
                'subtotal': subtotal,
                'seller': product.seller
            })
        
        # Create order
        order = Order.objects.create(
            buyer=buyer,
            total_amount=total_amount,
            shipping_address=validated_data['shipping_address'],
            payment_method=validated_data.get('payment_method', 'card'),
            status='pending',
            payment_status='pending'
        )
        
        # Create order items and update stock
        for item_data in order_items:
            OrderItem.objects.create(
                order=order,
                product=item_data['product'],
                seller=item_data['seller'],
                quantity=item_data['quantity'],
                price_at_purchase=item_data['price_at_purchase']
            )
            
            # Decrement stock
            product = item_data['product']
            product.stock_quantity -= item_data['quantity']
            product.sales_count += item_data['quantity']
            product.save()
        
        return order


class OrderStatusUpdateSerializer(serializers.Serializer):
    """Serializer for updating order status (seller only)"""
    status = serializers.ChoiceField(choices=Order.STATUS_CHOICES)