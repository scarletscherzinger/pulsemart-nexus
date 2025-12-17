from rest_framework import serializers

from .models import Seller
from apps.accounts.serializers import UserSerializer


class SellerRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for seller registration"""
    
    class Meta:
        model = Seller
        fields = ('store_name', 'store_description', 'store_logo_url')
        extra_kwargs = {
            'store_name': {'required': True},
        }


class SellerSerializer(serializers.ModelSerializer):
    """Serializer for seller profile data"""
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = Seller
        fields = (
            'id', 'user', 'store_name', 'store_description', 'store_logo_url',
            'total_sales', 'total_orders', 'rating', 'is_verified',
            'joined_date', 'last_sale_date'
        )
        read_only_fields = (
            'id', 'total_sales', 'total_orders', 'rating',
            'is_verified', 'joined_date', 'last_sale_date'
        )