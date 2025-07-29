from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.db.models import Q
from django.db import transaction
from django.core.paginator import Paginator
import json
from .models import Category, Product, CartItem, Order, OrderItem, Contact
from accounts.models import WalletTransaction, MarketplaceWallet, MarketplaceTransaction
from decimal import Decimal


def home(request):
    """
    Home page view with featured products
    """
    featured_products = Product.objects.filter(is_active=True)[:8]
    categories = Category.objects.all()
    
    return render(request, 'shop/home.html', {
        'featured_products': featured_products,
        'categories': categories
    })


def about_us(request):
    """
    About Us page
    """
    return render(request, 'shop/about_us.html')


def contact_us(request):
    """
    Contact Us page
    """
    if request.method == 'POST':
        # Handle contact form submission
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        
        if name and email and subject and message:
            try:
                # Save contact message to database
                contact = Contact.objects.create(
                    name=name,
                    email=email,
                    subject=subject,
                    message=message
                )
                messages.success(request, f'Thank you {name}! Your message has been received. We will get back to you soon.')
                return redirect('shop:contact_us')
            except Exception as e:
                messages.error(request, 'Sorry, there was an error submitting your message. Please try again.')
        else:
            messages.error(request, 'Please fill in all fields.')
    
    return render(request, 'shop/contact_us.html')


def product_list(request):
    """
    Product listing with search and filtering
    """
    products = Product.objects.filter(is_active=True)
    categories = Category.objects.all()
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) | 
            Q(description__icontains=search_query)
        )
    
    # Category filtering
    category_id = request.GET.get('category', '')
    if category_id:
        products = products.filter(category_id=category_id)
    
    # Pagination
    paginator = Paginator(products, 12)  # 12 products per page
    page_number = request.GET.get('page')
    products = paginator.get_page(page_number)
    
    return render(request, 'shop/products.html', {
        'products': products,
        'categories': categories,
        'search_query': search_query,
        'selected_category': category_id
    })


def product_detail(request, product_id):
    """
    Individual product detail view
    """
    product = get_object_or_404(Product, id=product_id, is_active=True)
    related_products = Product.objects.filter(
        category=product.category, 
        is_active=True
    ).exclude(id=product.id)[:4]
    
    return render(request, 'shop/product_detail.html', {
        'product': product,
        'related_products': related_products
    })


@require_http_methods(["POST"])
def add_to_cart(request):
    """
    Add product to cart (AJAX endpoint)
    """
    try:
        data = json.loads(request.body)
        product_id = data.get('product_id')
        quantity = int(data.get('quantity', 1))
        
        product = get_object_or_404(Product, id=product_id, is_active=True)
        
        if quantity <= 0 or quantity > product.stock:
            return JsonResponse({
                'success': False, 
                'message': f'Invalid quantity. Available stock: {product.stock}'
            })
        
        if request.user.is_authenticated:
            # For logged-in users
            cart_item, created = CartItem.objects.get_or_create(
                user=request.user,
                product=product,
                defaults={'quantity': quantity}
            )
            if not created:
                cart_item.quantity += quantity
                if cart_item.quantity > product.stock:
                    cart_item.quantity = product.stock
                cart_item.save()
        else:
            # For guest users using session
            if not request.session.session_key:
                request.session.create()
            
            cart_item, created = CartItem.objects.get_or_create(
                session_key=request.session.session_key,
                product=product,
                defaults={'quantity': quantity}
            )
            if not created:
                cart_item.quantity += quantity
                if cart_item.quantity > product.stock:
                    cart_item.quantity = product.stock
                cart_item.save()
        
        # Get cart count
        cart_count = get_cart_count(request)
        
        return JsonResponse({
            'success': True,
            'message': 'Product added to cart successfully!',
            'cart_count': cart_count
        })
        
    except (json.JSONDecodeError, ValueError, Product.DoesNotExist):
        return JsonResponse({'success': False, 'message': 'Invalid request'})


def get_cart_count(request):
    """
    Helper function to get cart item count
    """
    if request.user.is_authenticated:
        return CartItem.objects.filter(user=request.user).count()
    elif request.session.session_key:
        return CartItem.objects.filter(session_key=request.session.session_key).count()
    return 0


@login_required
def cart_view(request):
    """
    Shopping cart view
    """
    cart_items = CartItem.objects.filter(user=request.user)
    total_amount = sum(item.get_total_price() for item in cart_items)
    
    return render(request, 'shop/cart.html', {
        'cart_items': cart_items,
        'total_amount': total_amount
    })


@login_required
@require_http_methods(["POST"])
def update_cart_item(request):
    """
    Update cart item quantity (AJAX endpoint)
    """
    try:
        data = json.loads(request.body)
        cart_item_id = data.get('cart_item_id')
        quantity = int(data.get('quantity', 1))
        
        cart_item = get_object_or_404(CartItem, id=cart_item_id, user=request.user)
        
        if quantity <= 0:
            cart_item.delete()
        else:
            if quantity > cart_item.product.stock:
                quantity = cart_item.product.stock
            cart_item.quantity = quantity
            cart_item.save()
        
        # Calculate new totals
        cart_items = CartItem.objects.filter(user=request.user)
        cart_total = sum(item.get_total_price() for item in cart_items)
        
        return JsonResponse({
            'success': True,
            'cart_total': f'{cart_total:.2f}',
            'item_total': {
                'item_id': cart_item_id,
                'total': f'{cart_item.get_total_price():.2f}' if quantity > 0 else '0.00'
            }
        })
        
    except (json.JSONDecodeError, ValueError, CartItem.DoesNotExist):
        return JsonResponse({'success': False, 'message': 'Invalid request'})


@login_required
def checkout(request):
    """
    Checkout process
    """
    if request.user.role != 'user':
        messages.error(request, 'Only users can make purchases.')
        return redirect('shop:home')
    
    cart_items = CartItem.objects.filter(user=request.user)
    if not cart_items:
        messages.warning(request, 'Your cart is empty.')
        return redirect('shop:cart')
    
    total_amount = sum(item.get_total_price() for item in cart_items)
    wallet = request.user.wallet
    
    if request.method == 'POST':
        shipping_address = request.POST.get('shipping_address', request.user.address)
        
        if not wallet.can_deduct(total_amount):
            messages.error(request, f'Insufficient wallet balance. Required: ${total_amount}, Available: ${wallet.balance}')
            return redirect('shop:checkout')
        
        # Check stock availability
        for item in cart_items:
            if item.quantity > item.product.stock:
                messages.error(request, f'Insufficient stock for {item.product.name}. Available: {item.product.stock}')
                return redirect('shop:cart')
        
        try:
            with transaction.atomic():
                # Create order
                order = Order.objects.create(
                    user=request.user,
                    total_amount=total_amount,
                    shipping_address=shipping_address,
                    status='confirmed'
                )
                
                # Create order items and update stock
                for item in cart_items:
                    OrderItem.objects.create(
                        order=order,
                        product=item.product,
                        quantity=item.quantity,
                        price=item.product.price
                    )
                    
                    # Reduce product stock
                    item.product.reduce_stock(item.quantity)
                
                # Deduct money from user wallet
                wallet.deduct_money(total_amount)
                
                # Create user wallet transaction
                WalletTransaction.objects.create(
                    wallet=wallet,
                    transaction_type='debit',
                    amount=total_amount,
                    description=f'Purchase - Order {order.order_id}'
                )
                
                # Transfer money to vendor wallets
                vendor_payments = {}
                for item in cart_items:
                    vendor = item.product.vendor
                    item_total = item.get_total_price()
                    
                    if vendor in vendor_payments:
                        vendor_payments[vendor] += item_total
                    else:
                        vendor_payments[vendor] = item_total
                
                # Process vendor payments with marketplace commission
                marketplace_wallet = MarketplaceWallet.get_instance()
                total_commission = Decimal('0.00')
                
                for vendor, gross_amount in vendor_payments.items():
                    # Calculate commission (8% to marketplace, 92% to vendor)
                    commission_info = marketplace_wallet.calculate_commission(gross_amount)
                    commission_amount = commission_info['commission']
                    vendor_net_amount = commission_info['vendor_amount']
                    
                    # Add net amount to vendor wallet
                    vendor_wallet = vendor.wallet
                    vendor_wallet.add_money(vendor_net_amount)
                    
                    # Create vendor wallet transaction (net amount after commission)
                    WalletTransaction.objects.create(
                        wallet=vendor_wallet,
                        transaction_type='credit',
                        amount=vendor_net_amount,
                        description=f'Sale - Order {order.order_id} (Net: ${vendor_net_amount}, Commission: ${commission_amount})'
                    )
                    
                    # Add commission to marketplace wallet
                    marketplace_wallet.add_commission(commission_amount)
                    
                    # Create marketplace commission transaction record
                    MarketplaceTransaction.objects.create(
                        marketplace_wallet=marketplace_wallet,
                        transaction_type='commission',
                        amount=commission_amount,
                        description=f'Commission from Order {order.order_id} (8%)',
                        related_order_id=str(order.order_id),
                        vendor_username=vendor.username
                    )
                    
                    total_commission += commission_amount
                
                # Clear cart
                cart_items.delete()
                
                messages.success(request, f'Order placed successfully! Order ID: {order.order_id}')
                return redirect('shop:order_confirmation', order_id=order.order_id)
                
        except Exception as e:
            messages.error(request, 'An error occurred while processing your order.')
            return redirect('shop:checkout')
    
    return render(request, 'shop/checkout.html', {
        'cart_items': cart_items,
        'total_amount': total_amount,
        'wallet_balance': wallet.balance
    })


@login_required
def order_confirmation(request, order_id):
    """
    Order confirmation page
    """
    order = get_object_or_404(Order, order_id=order_id, user=request.user)
    return render(request, 'shop/order_confirmation.html', {'order': order})


@login_required
def order_list(request):
    """
    User's order history
    """
    if request.user.role != 'user':
        messages.error(request, 'Access denied.')
        return redirect('dashboard:home')
    
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    
    return render(request, 'shop/orders.html', {'orders': orders})


@login_required
def order_detail(request, order_id):
    """
    Detailed order view
    """
    order = get_object_or_404(Order, order_id=order_id, user=request.user)
    return render(request, 'shop/order_detail.html', {'order': order})


def search_products(request):
    """
    AJAX product search endpoint
    """
    query = request.GET.get('q', '').strip()
    results = []
    
    if query and len(query) >= 2:
        products = Product.objects.filter(
            Q(name__icontains=query) | Q(description__icontains=query),
            is_active=True
        )[:10]
        
        results = [{
            'id': product.id,
            'name': product.name,
            'price': str(product.price),
            'image': product.image.url if product.image else None
        } for product in products]
    
    return JsonResponse({'results': results})
