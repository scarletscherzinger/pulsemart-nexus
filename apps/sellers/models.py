from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator


class Seller(models.Model):
    """Seller profile and metrics"""
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='seller_profile'
    )
    store_name = models.CharField(max_length=200, unique=True)
    store_description = models.TextField(blank=True)
    store_logo_url = models.URLField(blank=True, null=True)
    
    # Denormalized fields for performance
    total_sales = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_orders = models.IntegerField(default=0)
    rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(5)]
    )
    
    is_verified = models.BooleanField(default=False)
    joined_date = models.DateTimeField(auto_now_add=True)
    last_sale_date = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'sellers'
        verbose_name = 'Seller'
        verbose_name_plural = 'Sellers'
        indexes = [
            models.Index(fields=['-total_sales']),
            models.Index(fields=['store_name']),
        ]
    
    def __str__(self):
        return self.store_name