from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from apps.products.models import Product
from apps.sellers.models import Seller
import uuid
from django.utils import timezone


class Order(models.Model):
    """Customer orders"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]
    
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]
    
    order_number = models.CharField(max_length=50, unique=True, editable=False)
    buyer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='orders'
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    
    payment_status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS_CHOICES,
        default='pending'
    )
    payment_method = models.CharField(max_length=50, blank=True)
    
    shipping_address = models.JSONField()  # {street, city, state, zip, country}
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'orders'
        verbose_name = 'Order'
        verbose_name_plural = 'Orders'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['buyer']),
            models.Index(fields=['status']),
            models.Index(fields=['-created_at']),
            models.Index(fields=['order_number']),
        ]
    
    def save(self, *args, **kwargs):
        """Generate unique order number on creation"""
        if not self.order_number:
            self.order_number = self.generate_order_number()
        super().save(*args, **kwargs)
    
    def generate_order_number(self):
        """Generate unique order number: ORD-20251218-XXXX"""
        date_str = timezone.now().strftime('%Y%m%d')
        unique_id = str(uuid.uuid4().hex[:8]).upper()
        return f"ORD-{date_str}-{unique_id}"
    
    def __str__(self):
        return self.order_number


class OrderItem(models.Model):
    """Individual items in an order"""
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items'
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE
    )
    seller = models.ForeignKey(
        Seller,
        on_delete=models.CASCADE,
        related_name='order_items'
    )
    
    quantity = models.IntegerField(validators=[MinValueValidator(1)])
    price_at_purchase = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )  # Price snapshot
    subtotal = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'order_items'
        verbose_name = 'Order Item'
        verbose_name_plural = 'Order Items'
        indexes = [
            models.Index(fields=['order']),
            models.Index(fields=['product']),
            models.Index(fields=['seller']),
            models.Index(fields=['-created_at']),
        ]
    
    def save(self, *args, **kwargs):
        """Calculate subtotal before saving"""
        self.subtotal = self.quantity * self.price_at_purchase
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.quantity}x {self.product.name} in {self.order.order_number}"