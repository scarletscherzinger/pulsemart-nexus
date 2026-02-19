"""
Payment models for handling Stripe transactions.
"""
from django.db import models
from django.conf import settings

from apps.orders.models import Order


class Payment(models.Model):
    """
    Store payment transaction details.
    Follows single responsibility - only handles payment records.
    """
    
    class PaymentStatus(models.TextChoices):
        PENDING = 'pending', 'Pending'
        PROCESSING = 'processing', 'Processing'
        SUCCEEDED = 'succeeded', 'Succeeded'
        FAILED = 'failed', 'Failed'
        CANCELED = 'canceled', 'Canceled'
        REFUNDED = 'refunded', 'Refunded'
    
    # Relationships
    order = models.OneToOneField(
        Order,
        on_delete=models.PROTECT,
        related_name='payment'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='payments'
    )
    
    # Stripe fields
    stripe_payment_intent_id = models.CharField(
        max_length=255,
        unique=True,
        db_index=True
    )
    stripe_charge_id = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )
    
    # Payment details
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )
    currency = models.CharField(
        max_length=3,
        default='USD'
    )
    status = models.CharField(
        max_length=20,
        choices=PaymentStatus.choices,
        default=PaymentStatus.PENDING,
        db_index=True
    )
    
    # Metadata
    payment_method_type = models.CharField(
        max_length=50,
        blank=True,
        null=True
    )
    failure_message = models.TextField(
        blank=True,
        null=True
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'payments'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['status', '-created_at']),
        ]
    
    def __str__(self) -> str:
        return f"Payment {self.stripe_payment_intent_id} - {self.status}"