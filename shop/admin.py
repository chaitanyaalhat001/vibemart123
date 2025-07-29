from django.contrib import admin
from .models import Category, Product, CartItem, Order, OrderItem, Contact


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """
    Admin for Category model
    """
    list_display = ('name', 'description', 'created_at')
    search_fields = ('name',)
    ordering = ('name',)
    readonly_fields = ('created_at',)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """
    Admin for Product model
    """
    list_display = ('name', 'category', 'vendor', 'price', 'stock', 'is_active', 'created_at')
    list_filter = ('category', 'vendor', 'is_active', 'created_at')
    search_fields = ('name', 'description', 'vendor__username')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'category', 'vendor')
        }),
        ('Pricing & Stock', {
            'fields': ('price', 'stock', 'is_active')
        }),
        ('Media', {
            'fields': ('image',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    """
    Admin for CartItem model
    """
    list_display = ('get_user_display', 'product', 'quantity', 'added_at')
    list_filter = ('added_at',)
    search_fields = ('user__username', 'product__name', 'session_key')
    ordering = ('-added_at',)
    readonly_fields = ('added_at',)
    
    def get_user_display(self, obj):
        return obj.user.username if obj.user else f"Guest ({obj.session_key[:8]}...)"
    get_user_display.short_description = 'User'


class OrderItemInline(admin.TabularInline):
    """
    Inline admin for OrderItem
    """
    model = OrderItem
    extra = 0
    readonly_fields = ('product', 'quantity', 'price')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """
    Admin for Order model
    """
    list_display = ('order_id', 'user', 'total_amount', 'status', 'tracking_id', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('order_id', 'user__username', 'tracking_id')
    ordering = ('-created_at',)
    readonly_fields = ('order_id', 'tracking_id', 'created_at', 'updated_at')
    inlines = [OrderItemInline]
    
    fieldsets = (
        ('Order Information', {
            'fields': ('order_id', 'user', 'total_amount', 'status')
        }),
        ('Shipping', {
            'fields': ('shipping_address', 'tracking_id')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    """
    Admin for OrderItem model
    """
    list_display = ('order', 'product', 'quantity', 'price', 'get_total_price')
    list_filter = ('order__created_at',)
    search_fields = ('order__order_id', 'product__name')
    ordering = ('-order__created_at',)
    
    def get_total_price(self, obj):
        return f"${obj.get_total_price():.2f}"
    get_total_price.short_description = 'Total Price'


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    """
    Admin for Contact model
    """
    list_display = ('name', 'email', 'subject', 'status', 'created_at')
    list_filter = ('status', 'subject', 'created_at')
    search_fields = ('name', 'email', 'subject', 'message')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Contact Information', {
            'fields': ('name', 'email', 'subject')
        }),
        ('Message', {
            'fields': ('message',)
        }),
        ('Status & Admin Notes', {
            'fields': ('status', 'admin_notes')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def has_delete_permission(self, request, obj=None):
        # Only allow admins to delete contact messages
        return request.user.is_superuser or request.user.role == 'admin'
