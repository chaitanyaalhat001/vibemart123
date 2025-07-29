from django.db import models
from django.utils import timezone
from django.conf import settings
import uuid
import random
import string


class Category(models.Model):
    """
    Product categories for organizing products
    """
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['name']


class Product(models.Model):
    """
    Product model for items in the shop
    """
    name = models.CharField(max_length=200)
    description = models.TextField()
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    stock = models.PositiveIntegerField(default=0)
    vendor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, 
                             related_name='products', limit_choices_to={'role': 'vendor'})
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} - ${self.price}"
    
    def is_in_stock(self):
        """Check if product is available in stock"""
        return self.stock > 0
    
    def reduce_stock(self, quantity):
        """Reduce stock when product is sold"""
        if self.stock >= quantity:
            self.stock -= quantity
            self.save()
            return True
        return False
    
    class Meta:
        ordering = ['-created_at']


class CartItem(models.Model):
    """
    Shopping cart items for users
    Supports both logged-in users and session-based carts
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, 
                           related_name='cart_items', blank=True, null=True)
    session_key = models.CharField(max_length=40, blank=True, null=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        if self.user:
            return f"{self.user.username} - {self.product.name} (x{self.quantity})"
        return f"Guest - {self.product.name} (x{self.quantity})"
    
    def get_total_price(self):
        """Calculate total price for this cart item"""
        return self.product.price * self.quantity
    
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'product'], 
                name='unique_user_product_cart',
                condition=models.Q(user__isnull=False)
            ),
            models.UniqueConstraint(
                fields=['session_key', 'product'], 
                name='unique_session_product_cart',
                condition=models.Q(session_key__isnull=False)
            ),
        ]


class Order(models.Model):
    """
    Order model for completed purchases
    """
    ORDER_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, 
                           related_name='orders')
    order_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    tracking_id = models.CharField(max_length=20, unique=True, blank=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=ORDER_STATUS_CHOICES, default='pending')
    shipping_address = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Order {self.order_id} - {self.user.username}"
    
    def save(self, *args, **kwargs):
        if not self.tracking_id:
            self.tracking_id = self.generate_tracking_id()
        super().save(*args, **kwargs)
    
    def generate_tracking_id(self):
        """Generate dummy tracking ID"""
        prefix = "BLD"
        suffix = ''.join(random.choices(string.digits, k=6))
        return f"{prefix}{suffix}"
    
    class Meta:
        ordering = ['-created_at']


class OrderItem(models.Model):
    """
    Individual items within an order
    """
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Price at time of order
    
    def __str__(self):
        return f"{self.order.order_id} - {self.product.name} (x{self.quantity})"
    
    def get_total_price(self):
        """Calculate total price for this order item"""
        return self.price * self.quantity


class Contact(models.Model):
    """
    Contact form submissions
    """
    SUBJECT_CHOICES = [
        ('General Inquiry', 'General Inquiry'),
        ('Order Support', 'Order Support'),
        ('Vendor Support', 'Vendor Support'),
        ('Technical Issue', 'Technical Issue'),
        ('Billing Question', 'Billing Question'),
        ('Partnership', 'Partnership'),
        ('Feedback', 'Feedback'),
        ('Other', 'Other'),
    ]
    
    STATUS_CHOICES = [
        ('new', 'New'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
    ]
    
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=50, choices=SUBJECT_CHOICES)
    message = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    admin_notes = models.TextField(blank=True, help_text="Internal notes for admins")
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.subject} ({self.status})"
