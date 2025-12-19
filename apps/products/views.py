# Third-party imports
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, generics, status
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response

# Local application imports
from .models import Category, Product
from .permissions import IsSellerOrReadOnly
from .serializers import (
    CategorySerializer,
    ProductCreateUpdateSerializer,
    ProductSerializer,
)


class CategoryListView(generics.ListAPIView):
    """List all categories"""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class ProductListCreateView(generics.ListCreateAPIView):
    """
    List all products or create new product (sellers only)
    """
    queryset = Product.objects.filter(is_active=True).select_related('seller', 'category')
    permission_classes = [IsSellerOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'seller', 'is_active']
    search_fields = ['name', 'description']
    ordering_fields = ['price', 'created_at', 'sales_count']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ProductCreateUpdateSerializer
        return ProductSerializer
    
    def perform_create(self, serializer):
        """Auto-assign seller from logged-in user"""
        serializer.save(seller=self.request.user.seller_profile)
    
    def create(self, request, *args, **kwargs):
        # Check if user has seller profile
        if not hasattr(request.user, 'seller_profile'):
            return Response({
                'error': 'You must be registered as a seller to create products'
            }, status=status.HTTP_403_FORBIDDEN)
        
        return super().create(request, *args, **kwargs)


class ProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete a product
    """
    queryset = Product.objects.all().select_related('seller', 'category')
    permission_classes = [IsSellerOrReadOnly]
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return ProductCreateUpdateSerializer
        return ProductSerializer
    
    def retrieve(self, request, *args, **kwargs):
        """Increment view count when product is viewed"""
        instance = self.get_object()
        instance.views_count += 1
        instance.save(update_fields=['views_count'])
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    
    def update(self, request, *args, **kwargs):
        """Override to return full product details after update"""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        # Return full product details using ProductSerializer
        return Response(ProductSerializer(instance).data)