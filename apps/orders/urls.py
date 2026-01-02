from django.urls import path
from .views import (
    OrderListCreateView,
    OrderDetailView,
    SellerOrderListView,
    OrderStatusUpdateView
)

urlpatterns = [
    path('', OrderListCreateView.as_view(), name='order-list-create'),
    path('<int:pk>/', OrderDetailView.as_view(), name='order-detail'),
    path('seller/', SellerOrderListView.as_view(), name='seller-orders'),
    path('<int:pk>/status/', OrderStatusUpdateView.as_view(), name='order-status-update'),
]