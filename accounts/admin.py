from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Wallet, WalletTransaction, MarketplaceWallet, MarketplaceTransaction


@admin.register(User)
class CustomUserAdmin(BaseUserAdmin):
    """
    Custom admin for User model with role-based fields
    """
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'is_staff', 'date_joined')
    list_filter = ('role', 'is_staff', 'is_superuser', 'is_active', 'date_joined')
    search_fields = ('username', 'first_name', 'last_name', 'email', 'phone_number')
    ordering = ('-date_joined',)
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Additional Info', {
            'fields': ('role', 'phone_number', 'address')
        }),
    )
    
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Additional Info', {
            'fields': ('role', 'phone_number', 'address')
        }),
    )


@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    """
    Admin for Wallet model
    """
    list_display = ('user', 'balance', 'created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('user__username', 'user__email')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-updated_at',)
    
    def has_add_permission(self, request):
        # Wallets should be created automatically when users are created
        return False


@admin.register(WalletTransaction)
class WalletTransactionAdmin(admin.ModelAdmin):
    """
    Admin for WalletTransaction model
    """
    list_display = ('wallet', 'transaction_type', 'amount', 'description', 'date')
    list_filter = ('transaction_type', 'date')
    search_fields = ('wallet__user__username', 'description')
    readonly_fields = ('date',)
    ordering = ('-date',)
    
    def has_change_permission(self, request, obj=None):
        # Transactions should not be editable once created
        return False


@admin.register(MarketplaceWallet)
class MarketplaceWalletAdmin(admin.ModelAdmin):
    """
    Admin for MarketplaceWallet model
    """
    list_display = ('balance', 'total_commission_earned', 'commission_rate', 'created_at', 'updated_at')
    readonly_fields = ('balance', 'total_commission_earned', 'created_at', 'updated_at')
    
    fieldsets = (
        ('Balance Information', {
            'fields': ('balance', 'total_commission_earned')
        }),
        ('Commission Settings', {
            'fields': ('commission_rate',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def has_add_permission(self, request):
        # Only allow one marketplace wallet
        return not MarketplaceWallet.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        # Don't allow deletion of marketplace wallet
        return False


@admin.register(MarketplaceTransaction)
class MarketplaceTransactionAdmin(admin.ModelAdmin):
    """
    Admin for MarketplaceTransaction model
    """
    list_display = ('marketplace_wallet', 'transaction_type', 'amount', 'vendor_username', 'related_order_id', 'date')
    list_filter = ('transaction_type', 'date')
    search_fields = ('description', 'vendor_username', 'related_order_id')
    readonly_fields = ('date',)
    ordering = ('-date',)
    
    fieldsets = (
        ('Transaction Details', {
            'fields': ('marketplace_wallet', 'transaction_type', 'amount', 'description')
        }),
        ('Related Information', {
            'fields': ('vendor_username', 'related_order_id')
        }),
        ('Timestamp', {
            'fields': ('date',),
            'classes': ('collapse',)
        }),
    )
    
    def has_change_permission(self, request, obj=None):
        # Marketplace transactions should not be editable once created
        return False
