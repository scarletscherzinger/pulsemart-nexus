from rest_framework import serializers

from .models import Category, Product, ProductImage


class CategorySerializer(serializers.ModelSerializer):
    """Serializer for categories"""
    
    class Meta:
        model = Category
        fields = ('id', 'name', 'description', 'slug', 'created_at')
        read_only_fields = ('id', 'created_at')


class ProductImageSerializer(serializers.ModelSerializer):
    """Serializer for product images"""
    
    class Meta:
        model = ProductImage
        fields = ('id', 'image', 'is_primary', 'created_at')
        read_only_fields = ('id', 'created_at')


class ProductSerializer(serializers.ModelSerializer):
    """Serializer for product listing"""
    category = CategorySerializer(read_only=True)
    category_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    seller_name = serializers.CharField(source='seller.store_name', read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)
    
    class Meta:
        model = Product
        fields = (
            'id', 'seller', 'seller_name', 'category', 'category_id',
            'name', 'description', 'price', 'stock_quantity', 'image',
            'is_active', 'views_count', 'sales_count',
            'created_at', 'updated_at', 'images'
        )
        read_only_fields = (
            'id', 'seller', 'seller_name', 'views_count', 'sales_count',
            'created_at', 'updated_at'
        )
    
    def validate_price(self, value):
        """Ensure price is positive"""
        if value < 0:
            raise serializers.ValidationError("Price cannot be negative")
        return value
    
    def validate_stock_quantity(self, value):
        """Ensure stock is non-negative"""
        if value < 0:
            raise serializers.ValidationError("Stock quantity cannot be negative")
        return value


class ProductCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating products"""
    category_id = serializers.IntegerField(required=False, allow_null=True)
    
    class Meta:
        model = Product
        fields = (
            'name', 'description', 'price', 'stock_quantity',
            'image', 'category_id', 'is_active'
        )
    
    def validate_price(self, value):
        if value < 0:
            raise serializers.ValidationError("Price cannot be negative")
        return value
    
    def validate_stock_quantity(self, value):
        if value < 0:
            raise serializers.ValidationError("Stock quantity cannot be negative")
        return value