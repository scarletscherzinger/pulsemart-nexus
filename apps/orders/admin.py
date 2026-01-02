from django.contrib import admin

from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product', 'seller', 'quantity', 'price_at_purchase', 'subtotal')
    can_delete = False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'buyer', 'status', 'payment_status', 'total_amount', 'created_at')
    list_filter = ('status', 'payment_status', 'created_at')
    search_fields = ('order_number', 'buyer__email')
    readonly_fields = ('order_number', 'total_amount', 'created_at', 'updated_at')
    inlines = [OrderItemInline]
    
    fieldsets = (
        ('Order Info', {
            'fields': ('order_number', 'buyer', 'total_amount')
        }),
        ('Status', {
            'fields': ('status', 'payment_status', 'payment_method')
        }),
        ('Shipping', {
            'fields': ('shipping_address',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'delivered_at')
        }),
    )


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'seller', 'quantity', 'price_at_purchase', 'subtotal')
    list_filter = ('created_at',)
    search_fields = ('order__order_number', 'product__name')
    readonly_fields = ('order', 'product', 'seller', 'price_at_purchase', 'subtotal', 'created_at')