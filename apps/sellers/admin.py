from django.contrib import admin

from .models import Seller


@admin.register(Seller)
class SellerAdmin(admin.ModelAdmin):
    list_display = ('store_name', 'user', 'total_sales', 'total_orders', 'rating', 'is_verified', 'joined_date')
    list_filter = ('is_verified', 'joined_date')
    search_fields = ('store_name', 'user__email')
    list_editable = ('is_verified',)
    readonly_fields = ('total_sales', 'total_orders', 'joined_date', 'last_sale_date')
    
    fieldsets = (
        ('Basic Info', {
            'fields': ('user', 'store_name', 'store_description', 'store_logo_url')
        }),
        ('Metrics', {
            'fields': ('total_sales', 'total_orders', 'rating')
        }),
        ('Status', {
            'fields': ('is_verified', 'joined_date', 'last_sale_date')
        }),
    )