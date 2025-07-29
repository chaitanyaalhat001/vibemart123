from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from decimal import Decimal


class User(AbstractUser):
    """
    Custom User model with role-based access control
    Roles: user, vendor, admin
    """
    ROLE_CHOICES = [
        ('user', 'User'),
        ('vendor', 'Vendor'),
        ('admin', 'Admin'),
    ]
    
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user')
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return f"{self.username} ({self.role})"
    
    def is_user(self):
        return self.role == 'user'
    
    def is_vendor(self):
        return self.role == 'vendor'
    
    def is_admin_user(self):
        return self.role == 'admin'


class Wallet(models.Model):
    """
    Wallet model for dummy payment system
    Each user has one wallet
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='wallet')
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username}'s Wallet - Balance: ${self.balance}"
    
    def can_deduct(self, amount):
        """Check if wallet has sufficient balance for deduction"""
        amount = Decimal(str(amount))
        return self.balance >= amount
    
    def add_money(self, amount):
        """Add money to wallet"""
        amount = Decimal(str(amount))
        self.balance += amount
        self.save()
        return self.balance
    
    def deduct_money(self, amount):
        """Deduct money from wallet if sufficient balance"""
        amount = Decimal(str(amount))
        if self.can_deduct(amount):
            self.balance -= amount
            self.save()
            return True
        return False


class WalletTransaction(models.Model):
    """
    Track all wallet transactions
    """
    TRANSACTION_TYPES = [
        ('credit', 'Credit'),
        ('debit', 'Debit'),
    ]
    
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name='transactions')
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.CharField(max_length=255, blank=True, null=True)
    date = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return f"{self.wallet.user.username} - {self.transaction_type.title()} ${self.amount}"
    
    class Meta:
        ordering = ['-date']


class MarketplaceWallet(models.Model):
    """
    Marketplace commission wallet - tracks platform earnings
    """
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    total_commission_earned = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    commission_rate = models.DecimalField(max_digits=5, decimal_places=4, default=Decimal('0.0800'))  # 8%
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Marketplace Wallet - Balance: ${self.balance}"
    
    def add_commission(self, amount):
        """Add commission to marketplace wallet"""
        amount = Decimal(str(amount))
        self.balance += amount
        self.total_commission_earned += amount
        self.save()
        return self.balance
    
    def calculate_commission(self, amount):
        """Calculate commission from vendor payment"""
        amount = Decimal(str(amount))
        commission = amount * self.commission_rate
        vendor_amount = amount - commission
        return {
            'commission': commission,
            'vendor_amount': vendor_amount,
            'commission_rate': float(self.commission_rate) * 100  # Convert to percentage
        }
    
    @classmethod
    def get_instance(cls):
        """Get or create the single marketplace wallet instance"""
        wallet, created = cls.objects.get_or_create(pk=1)
        return wallet
    
    class Meta:
        verbose_name = "Marketplace Wallet"
        verbose_name_plural = "Marketplace Wallet"


class MarketplaceTransaction(models.Model):
    """
    Track marketplace commission transactions
    """
    TRANSACTION_TYPES = [
        ('commission', 'Commission'),
        ('expense', 'Expense'),
        ('withdrawal', 'Withdrawal'),
    ]
    
    marketplace_wallet = models.ForeignKey(MarketplaceWallet, on_delete=models.CASCADE, related_name='transactions')
    transaction_type = models.CharField(max_length=15, choices=TRANSACTION_TYPES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.CharField(max_length=255)
    related_order_id = models.CharField(max_length=100, blank=True, null=True)
    vendor_username = models.CharField(max_length=150, blank=True, null=True)
    date = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return f"Marketplace {self.transaction_type.title()} - ${self.amount}"
    
    class Meta:
        ordering = ['-date']
