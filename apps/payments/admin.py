"""
Payment admin configuration.
"""
from django.contrib import admin
from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    """
    Admin interface for Payment model.
    Read-only to prevent accidental modifications.
    """
    list_display = [
        'id',
        'stripe_payment_intent_id',
        'user',
        'order',
        'amount',
        'currency',
        'status',
        'created_at',
    ]
    
    list_filter = [
        'status',
        'currency',
        'created_at',
    ]
    
    search_fields = [
        'stripe_payment_intent_id',
        'stripe_charge_id',
        'user__email',
        'order__id',
    ]
    
    readonly_fields = [
        'id',
        'order',
        'user',
        'stripe_payment_intent_id',
        'stripe_charge_id',
        'amount',
        'currency',
        'status',
        'payment_method_type',
        'failure_message',
        'created_at',
        'updated_at',
    ]
    
    list_per_page = 50
    
    ordering = ['-created_at']
    
    # Make everything read-only
    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False