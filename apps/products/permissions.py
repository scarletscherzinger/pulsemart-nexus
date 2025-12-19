from rest_framework import permissions


class IsSellerOrReadOnly(permissions.BasePermission):
    """
    Sellers can create/edit their own products.
    Everyone else can only read.
    """
    
    def has_permission(self, request, view):
        # Allow read operations for everyone
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write operations require authenticated seller
        return request.user.is_authenticated and request.user.is_seller
    
    def has_object_permission(self, request, view, obj):
        # Allow read operations for everyone
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write operations only for product owner
        return obj.seller.user == request.user