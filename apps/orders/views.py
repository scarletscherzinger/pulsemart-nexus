from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import transaction

from .models import Order, OrderItem
from .serializers import (
    OrderSerializer,
    OrderCreateSerializer,
    OrderStatusUpdateSerializer
)


class OrderListCreateView(generics.ListCreateAPIView):
    """
    List user's orders or create new order
    """
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return OrderCreateSerializer
        return OrderSerializer
    
    def get_queryset(self):
        """Get orders for current user"""
        return Order.objects.filter(
            buyer=self.request.user
        ).prefetch_related('items__product', 'items__seller')
    
    @transaction.atomic
    def create(self, request, *args, **kwargs):
        """Create order with transaction"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        
        # Return full order details
        return Response(
            OrderSerializer(order).data,
            status=status.HTTP_201_CREATED
        )


class OrderDetailView(generics.RetrieveAPIView):
    """
    Retrieve order details
    """
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """User can only view their own orders"""
        return Order.objects.filter(
            buyer=self.request.user
        ).prefetch_related('items__product', 'items__seller')


class SellerOrderListView(generics.ListAPIView):
    """
    List orders containing seller's products
    """
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Get orders containing seller's products"""
        user = self.request.user
        
        if not user.is_seller:
            return Order.objects.none()
        
        # Get orders that have items from this seller
        return Order.objects.filter(
            items__seller=user.seller_profile
        ).distinct().prefetch_related('items__product', 'items__seller')


class OrderStatusUpdateView(generics.UpdateAPIView):
    """
    Update order status (seller only for their products)
    """
    serializer_class = OrderStatusUpdateSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Seller can only update orders containing their products"""
        user = self.request.user
        
        if not user.is_seller:
            return Order.objects.none()
        
        return Order.objects.filter(
            items__seller=user.seller_profile
        ).distinct()
    
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Update status
        instance.status = serializer.validated_data['status']
        instance.save()
        
        return Response(OrderSerializer(instance).data)