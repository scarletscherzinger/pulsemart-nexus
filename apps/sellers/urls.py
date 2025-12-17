from django.urls import path

from .views import SellerRegisterView, SellerProfileView

urlpatterns = [
    path('register/', SellerRegisterView.as_view(), name='seller-register'),
    path('me/', SellerProfileView.as_view(), name='seller-profile'),
]