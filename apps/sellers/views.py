from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import Seller
from .serializers import SellerRegistrationSerializer, SellerSerializer


class SellerRegisterView(generics.CreateAPIView):
    """API endpoint to register current user as a seller"""
    serializer_class = SellerRegistrationSerializer
    permission_classes = [IsAuthenticated]
    
    def create(self, request, *args, **kwargs):
        user = request.user
        
        # Check if user is already a seller
        if user.is_seller:
            return Response({
                'error': 'User is already registered as a seller'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if seller profile already exists
        if hasattr(user, 'seller_profile'):
            return Response({
                'error': 'Seller profile already exists'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Create seller profile
        seller = serializer.save(user=user)
        
        # Update user's is_seller flag
        user.is_seller = True
        user.save()
        
        return Response({
            'seller': SellerSerializer(seller).data,
            'message': 'Successfully registered as seller'
        }, status=status.HTTP_201_CREATED)


class SellerProfileView(generics.RetrieveUpdateAPIView):
    """API endpoint to view/update seller profile"""
    serializer_class = SellerSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        """Get current user's seller profile"""
        user = self.request.user
        
        if not user.is_seller:
            return None
        
        try:
            return user.seller_profile
        except Seller.DoesNotExist:
            return None
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        
        if instance is None:
            return Response({
                'error': 'User is not a seller'
            }, status=status.HTTP_404_NOT_FOUND)
        
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    
    def update(self, request, *args, **kwargs):
        """Allow partial updates for both PUT and PATCH"""
        instance = self.get_object()
        
        if instance is None:
            return Response({
                'error': 'User is not a seller'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Always allow partial updates
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        return Response(serializer.data)
    """API endpoint to view/update seller profile"""
    serializer_class = SellerSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        """Get current user's seller profile"""
        user = self.request.user
        
        if not user.is_seller:
            return None
        
        try:
            return user.seller_profile
        except Seller.DoesNotExist:
            return None
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        
        if instance is None:
            return Response({
                'error': 'User is not a seller'
            }, status=status.HTTP_404_NOT_FOUND)
        
        serializer = self.get_serializer(instance)
        return Response(serializer.data)