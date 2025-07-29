from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Count, Q
from django.http import JsonResponse
from django.core.paginator import Paginator
from accounts.models import User, Wallet, WalletTransaction, MarketplaceWallet, MarketplaceTransaction
from shop.models import Product, Order, OrderItem, Contact, Category
from shop.forms import ProductForm
from decimal import Decimal


@login_required
def dashboard_home(request):
    """
    Main dashboard view - redirects based on user role
    """
    if request.user.role == 'user':
        return user_dashboard(request)
    elif request.user.role == 'vendor':
        return vendor_dashboard(request)
    elif request.user.role == 'admin' or request.user.is_superuser:
        return admin_dashboard(request)
    else:
        messages.error(request, 'Invalid user role.')
        return redirect('shop:home')


def user_dashboard(request):
    """
    User dashboard with orders, wallet, and product browsing
    """
    user = request.user
    recent_orders = Order.objects.filter(user=user)[:5]
    wallet = user.wallet
    
    # Statistics
    total_orders = Order.objects.filter(user=user).count()
    total_spent = Order.objects.filter(user=user).aggregate(
        total=Sum('total_amount')
    )['total'] or 0
    
    # Featured products for browsing
    featured_products = Product.objects.filter(is_active=True)[:6]
    
    return render(request, 'dashboard/user_dashboard.html', {
        'recent_orders': recent_orders,
        'wallet': wallet,
        'total_orders': total_orders,
        'total_spent': total_spent,
        'featured_products': featured_products
    })


def vendor_dashboard(request):
    """
    Vendor dashboard with product management and analytics
    """
    vendor = request.user
    vendor_products = Product.objects.filter(vendor=vendor)
    
    # Statistics
    total_products = vendor_products.count()
    active_products = vendor_products.filter(is_active=True).count()
    
    # Sales data
    sold_items = OrderItem.objects.filter(product__vendor=vendor)
    total_sales = sold_items.aggregate(total=Sum('quantity'))['total'] or 0
    
    # Calculate total revenue properly
    total_revenue = 0
    for item in sold_items:
        total_revenue += item.price * item.quantity
    
    # Recent orders that contain vendor's products
    recent_orders = Order.objects.filter(
        items__product__vendor=vendor
    ).distinct().order_by('-created_at')[:5]
    
    return render(request, 'dashboard/vendor_dashboard.html', {
        'total_products': total_products,
        'active_products': active_products,
        'total_orders': recent_orders.count(),
        'total_revenue': total_revenue,
        'recent_orders': recent_orders,
        'vendor_products': vendor_products[:5],  # Recent products
        'categories': Category.objects.all()  # For add product modal
    })


def admin_dashboard(request):
    """
    Admin dashboard with overall system statistics
    """
    # User statistics
    total_users = User.objects.filter(role='user').count()
    total_vendors = User.objects.filter(role='vendor').count()
    total_admins = User.objects.filter(role='admin').count()
    
    # Product statistics
    total_products = Product.objects.count()
    active_products = Product.objects.filter(is_active=True).count()
    
    # Order statistics
    total_orders = Order.objects.count()
    total_revenue = Order.objects.aggregate(
        revenue=Sum('total_amount')
    )['revenue'] or 0
    
    # Recent activities
    recent_orders = Order.objects.all()[:10]
    recent_products = Product.objects.all()[:10]
    recent_users = User.objects.filter(role__in=['user', 'vendor'])[:10]
    
    return render(request, 'dashboard/admin_dashboard.html', {
        'total_users': total_users,
        'total_vendors': total_vendors,
        'total_admins': total_admins,
        'total_products': total_products,
        'active_products': active_products,
        'total_orders': total_orders,
        'total_revenue': total_revenue,
        'recent_orders': recent_orders,
        'recent_products': recent_products,
        'recent_users': recent_users
    })


@login_required
def vendor_products(request):
    """
    Vendor's product management page
    """
    if request.user.role != 'vendor':
        messages.error(request, 'Access denied.')
        return redirect('dashboard:home')
    
    products = Product.objects.filter(vendor=request.user)
    
    # Pagination
    paginator = Paginator(products, 10)
    page_number = request.GET.get('page')
    products = paginator.get_page(page_number)
    
    return render(request, 'dashboard/vendor_products.html', {
        'products': products
    })


@login_required
def add_product(request):
    """
    Add new product (vendor only)
    """
    if request.user.role != 'vendor':
        messages.error(request, 'Access denied.')
        return redirect('dashboard:home')
    
    if request.method == 'POST':
        # Handle form data manually for the modal
        name = request.POST.get('name')
        price = request.POST.get('price')
        category_id = request.POST.get('category')
        stock = request.POST.get('stock')
        description = request.POST.get('description')
        image = request.FILES.get('image')
        
        try:
            category = Category.objects.get(id=category_id)
            product = Product.objects.create(
                vendor=request.user,
                name=name,
                price=price,
                category=category,
                stock=stock,
                description=description,
                image=image
            )
            messages.success(request, f'Product "{product.name}" added successfully!')
        except Exception as e:
            messages.error(request, f'Error adding product: {str(e)}')
        
        return redirect('dashboard:home')
    
    # For GET request, just redirect back to dashboard
    return redirect('dashboard:home')


@login_required
def edit_product(request, product_id):
    """
    Edit existing product (vendor only)
    """
    if request.user.role != 'vendor':
        messages.error(request, 'Access denied.')
        return redirect('dashboard:home')
    
    product = get_object_or_404(Product, id=product_id, vendor=request.user)
    
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product updated successfully!')
            return redirect('dashboard:vendor_products')
    else:
        form = ProductForm(instance=product)
    
    return render(request, 'dashboard/edit_product.html', {
        'form': form,
        'product': product
    })


@login_required
def delete_product(request, product_id):
    """
    Delete product (vendor only)
    """
    if request.user.role != 'vendor':
        messages.error(request, 'Access denied.')
        return redirect('dashboard:home')
    
    product = get_object_or_404(Product, id=product_id, vendor=request.user)
    
    if request.method == 'POST':
        product.delete()
        messages.success(request, 'Product deleted successfully!')
        return redirect('dashboard:vendor_products')
    
    return render(request, 'dashboard/delete_product.html', {'product': product})


@login_required
def vendor_analytics(request):
    """
    Vendor analytics page
    """
    if request.user.role != 'vendor':
        messages.error(request, 'Access denied.')
        return redirect('dashboard:home')
    
    vendor = request.user
    
    # Product analytics
    products = Product.objects.filter(vendor=vendor)
    product_sales = OrderItem.objects.filter(product__vendor=vendor)
    
    # Sales by product
    sales_by_product = product_sales.values('product__name').annotate(
        total_sold=Sum('quantity'),
        total_revenue=Sum('quantity') * Sum('price')
    ).order_by('-total_sold')
    
    # Calculate total revenue properly
    total_revenue = 0
    for item in product_sales:
        total_revenue += item.price * item.quantity
    
    # Monthly sales (simplified)
    monthly_sales = product_sales.values('order__created_at__month').annotate(
        total_sales=Sum('quantity'),
        total_revenue=Sum('quantity') * Sum('price')
    ).order_by('-order__created_at__month')
    
    # Order statistics
    vendor_orders = Order.objects.filter(items__product__vendor=vendor).distinct()
    total_orders = vendor_orders.count()
    
    return render(request, 'dashboard/vendor_analytics.html', {
        'sales_by_product': sales_by_product,
        'monthly_sales': monthly_sales,
        'total_products': products.count(),
        'total_sales': product_sales.aggregate(total=Sum('quantity'))['total'] or 0,
        'total_revenue': total_revenue,
        'total_orders': total_orders
    })


@login_required
def admin_users(request):
    """
    Admin: View all users
    """
    if not (request.user.role == 'admin' or request.user.is_superuser):
        messages.error(request, 'Access denied.')
        return redirect('dashboard:home')
    
    users = User.objects.all().order_by('-date_joined')
    
    # Filter by role
    role_filter = request.GET.get('role', '')
    if role_filter:
        users = users.filter(role=role_filter)
    
    # Pagination
    paginator = Paginator(users, 20)
    page_number = request.GET.get('page')
    users = paginator.get_page(page_number)
    
    return render(request, 'dashboard/admin_users.html', {
        'users': users,
        'role_filter': role_filter
    })


@login_required
def admin_products(request):
    """
    Admin: View all products
    """
    if not (request.user.role == 'admin' or request.user.is_superuser):
        messages.error(request, 'Access denied.')
        return redirect('dashboard:home')
    
    products = Product.objects.all().order_by('-created_at')
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(vendor__username__icontains=search_query) |
            Q(category__name__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(products, 20)
    page_number = request.GET.get('page')
    products = paginator.get_page(page_number)
    
    return render(request, 'dashboard/admin_products.html', {
        'products': products,
        'search_query': search_query
    })


@login_required
def admin_orders(request):
    """
    Admin: View all orders
    """
    if not (request.user.role == 'admin' or request.user.is_superuser):
        messages.error(request, 'Access denied.')
        return redirect('dashboard:home')
    
    orders = Order.objects.all().order_by('-created_at')
    
    # Pagination
    paginator = Paginator(orders, 20)
    page_number = request.GET.get('page')
    orders = paginator.get_page(page_number)
    
    return render(request, 'dashboard/admin_orders.html', {
        'orders': orders
    })


@login_required
def admin_remove_product(request, product_id):
    """
    Admin: Remove/Delete a product
    """
    if not (request.user.role == 'admin' or request.user.is_superuser):
        messages.error(request, 'Access denied.')
        return redirect('dashboard:home')
    
    if request.method == 'POST':
        try:
            product = get_object_or_404(Product, id=product_id)
            product_name = product.name
            vendor_name = product.vendor.username
            
            # Delete the product
            product.delete()
            
            messages.success(request, f'Product "{product_name}" by {vendor_name} has been successfully removed from the marketplace.')
            
        except Product.DoesNotExist:
            messages.error(request, 'Product not found.')
        except Exception as e:
            messages.error(request, f'Error removing product: {str(e)}')
    
    return redirect('dashboard:admin_products')


@login_required
def admin_remove_user(request, user_id):
    """
    Admin: Remove/Delete a user
    """
    if not (request.user.role == 'admin' or request.user.is_superuser):
        messages.error(request, 'Access denied.')
        return redirect('dashboard:home')
    
    if request.method == 'POST':
        try:
            user_to_delete = get_object_or_404(User, id=user_id)
            
            # Prevent deletion of current admin user
            if user_to_delete == request.user:
                messages.error(request, 'You cannot delete your own account.')
                return redirect('dashboard:admin_users')
            
            # Prevent deletion of superusers by regular admins
            if user_to_delete.is_superuser and not request.user.is_superuser:
                messages.error(request, 'You cannot delete a superuser account.')
                return redirect('dashboard:admin_users')
            
            username = user_to_delete.username
            user_role = user_to_delete.role
            
            # Delete the user (CASCADE will handle related objects)
            user_to_delete.delete()
            
            messages.success(request, f'{user_role.title()} "{username}" has been successfully removed from the platform.')
            
        except User.DoesNotExist:
            messages.error(request, 'User not found.')
        except Exception as e:
            messages.error(request, f'Error removing user: {str(e)}')
    
    return redirect('dashboard:admin_users')


@login_required
def admin_user_products(request, user_id):
    """
    Admin: View products of a specific user (vendor)
    """
    if not (request.user.role == 'admin' or request.user.is_superuser):
        messages.error(request, 'Access denied.')
        return redirect('dashboard:home')
    
    user = get_object_or_404(User, id=user_id)
    
    if user.role != 'vendor':
        messages.error(request, f'User "{user.username}" is not a vendor.')
        return redirect('dashboard:admin_users')
    
    products = Product.objects.filter(vendor=user).order_by('-created_at')
    
    # Pagination
    paginator = Paginator(products, 10)
    page_number = request.GET.get('page')
    products = paginator.get_page(page_number)
    
    return render(request, 'dashboard/admin_user_products.html', {
        'user': user,
        'products': products
    })


@login_required
def admin_user_wallet(request, user_id):
    """
    Admin: View wallet details of a specific user
    """
    if not (request.user.role == 'admin' or request.user.is_superuser):
        messages.error(request, 'Access denied.')
        return redirect('dashboard:home')
    
    user = get_object_or_404(User, id=user_id)
    wallet = user.wallet
    transactions = wallet.transactions.all().order_by('-date')[:20]
    
    # Calculate statistics
    total_credits = wallet.transactions.filter(transaction_type='credit').aggregate(
        total=Sum('amount'))['total'] or 0
    total_debits = wallet.transactions.filter(transaction_type='debit').aggregate(
        total=Sum('amount'))['total'] or 0
    
    return render(request, 'dashboard/admin_user_wallet.html', {
        'user': user,
        'wallet': wallet,
        'transactions': transactions,
        'total_credits': total_credits,
        'total_debits': total_debits
    })


@login_required
def vendor_orders(request):
    """
    Vendor's order management page
    """
    if request.user.role != 'vendor':
        messages.error(request, 'Access denied.')
        return redirect('dashboard:home')
    
    # Get all orders that contain vendor's products
    orders = Order.objects.filter(
        items__product__vendor=request.user
    ).distinct().order_by('-created_at')
    
    # Filter by status if requested
    status_filter = request.GET.get('status', '')
    if status_filter:
        orders = orders.filter(status=status_filter)
    
    # Pagination
    paginator = Paginator(orders, 10)
    page_number = request.GET.get('page')
    orders = paginator.get_page(page_number)
    
    # Order statistics
    total_orders = Order.objects.filter(items__product__vendor=request.user).distinct().count()
    confirmed_orders = Order.objects.filter(items__product__vendor=request.user, status='confirmed').distinct().count()
    processing_orders = Order.objects.filter(items__product__vendor=request.user, status='processing').distinct().count()
    shipped_orders = Order.objects.filter(items__product__vendor=request.user, status='shipped').distinct().count()
    delivered_orders = Order.objects.filter(items__product__vendor=request.user, status='delivered').distinct().count()
    
    return render(request, 'dashboard/vendor_orders.html', {
        'orders': orders,
        'status_filter': status_filter,
        'total_orders': total_orders,
        'confirmed_orders': confirmed_orders,
        'processing_orders': processing_orders,
        'shipped_orders': shipped_orders,
        'delivered_orders': delivered_orders
    })


@login_required
def vendor_order_detail(request, order_id):
    """
    Vendor's order detail view
    """
    if request.user.role != 'vendor':
        messages.error(request, 'Access denied.')
        return redirect('dashboard:home')
    
    # Get order that contains vendor's products
    order = get_object_or_404(Order, order_id=order_id, items__product__vendor=request.user)
    
    # Get only the vendor's items from this order
    vendor_items = order.items.filter(product__vendor=request.user)
    
    return render(request, 'dashboard/vendor_order_detail.html', {
        'order': order,
        'vendor_items': vendor_items
    })


@login_required
def update_order_status(request, order_id):
    """
    Update order status (vendor only)
    """
    if request.user.role != 'vendor':
        messages.error(request, 'Access denied.')
        return redirect('dashboard:home')
    
    order = get_object_or_404(Order, order_id=order_id, items__product__vendor=request.user)
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in ['confirmed', 'processing', 'shipped', 'delivered', 'cancelled']:
            order.status = new_status
            order.save()
            messages.success(request, f'Order status updated to {order.get_status_display()}')
        else:
            messages.error(request, 'Invalid status.')
    
    return redirect('dashboard:vendor_order_detail', order_id=order_id)


@login_required
def vendor_wallet(request):
    """
    Vendor wallet management
    """
    if request.user.role != 'vendor':
        messages.error(request, 'Access denied.')
        return redirect('dashboard:home')
    
    wallet = request.user.wallet
    transactions = wallet.transactions.all().order_by('-date')[:20]  # Latest 20 transactions
    
    # Calculate earnings this month
    from django.utils import timezone
    from datetime import timedelta
    
    current_month = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    next_month = (current_month + timedelta(days=32)).replace(day=1)
    
    monthly_earnings = WalletTransaction.objects.filter(
        wallet=wallet,
        transaction_type='credit',
        date__gte=current_month,
        date__lt=next_month
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    # Calculate total earnings
    total_earnings = WalletTransaction.objects.filter(
        wallet=wallet,
        transaction_type='credit'
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    # Calculate pending withdrawals
    pending_withdrawals = WalletTransaction.objects.filter(
        wallet=wallet,
        transaction_type='debit',
        description__icontains='Withdrawal'
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    return render(request, 'dashboard/vendor_wallet.html', {
        'wallet': wallet,
        'transactions': transactions,
        'monthly_earnings': monthly_earnings,
        'total_earnings': total_earnings,
        'pending_withdrawals': pending_withdrawals
    })


@login_required
def withdraw_money(request):
    """
    Vendor money withdrawal
    """
    if request.user.role != 'vendor':
        messages.error(request, 'Access denied.')
        return redirect('dashboard:home')
    
    if request.method == 'POST':
        try:
            amount = float(request.POST.get('amount', 0))
            description = request.POST.get('description', 'Withdrawal')
            
            if amount <= 0:
                messages.error(request, 'Please enter a valid amount.')
                return redirect('dashboard:vendor_wallet')
            
            wallet = request.user.wallet
            
            if not wallet.can_deduct(amount):
                messages.error(request, f'Insufficient balance. Available: ${wallet.balance}')
                return redirect('dashboard:vendor_wallet')
            
            # Deduct money from wallet
            wallet.deduct_money(amount)
            
            # Create withdrawal transaction
            WalletTransaction.objects.create(
                wallet=wallet,
                transaction_type='debit',
                amount=amount,
                description=f'Withdrawal - {description}'
            )
            
            messages.success(request, f'${amount} withdrawal request processed successfully!')
            
        except (ValueError, TypeError):
            messages.error(request, 'Invalid amount entered.')
        except Exception as e:
            messages.error(request, f'Error processing withdrawal: {str(e)}')
    
    return redirect('dashboard:vendor_wallet')


@login_required
def admin_contacts(request):
    """
    Admin: View all contact messages
    """
    if not (request.user.role == 'admin' or request.user.is_superuser):
        messages.error(request, 'Access denied.')
        return redirect('dashboard:home')
    
    from shop.models import Contact
    
    contacts = Contact.objects.all().order_by('-created_at')
    
    # Filter by status
    status_filter = request.GET.get('status', '')
    if status_filter:
        contacts = contacts.filter(status=status_filter)
    
    # Filter by subject
    subject_filter = request.GET.get('subject', '')
    if subject_filter:
        contacts = contacts.filter(subject=subject_filter)
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        contacts = contacts.filter(
            Q(name__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(subject__icontains=search_query) |
            Q(message__icontains=search_query)
        )
    
    # Statistics
    total_contacts = Contact.objects.count()
    new_contacts = Contact.objects.filter(status='new').count()
    in_progress_contacts = Contact.objects.filter(status='in_progress').count()
    resolved_contacts = Contact.objects.filter(status='resolved').count()
    
    # Pagination
    paginator = Paginator(contacts, 20)
    page_number = request.GET.get('page')
    contacts = paginator.get_page(page_number)
    
    return render(request, 'dashboard/admin_contacts.html', {
        'contacts': contacts,
        'status_filter': status_filter,
        'subject_filter': subject_filter,
        'search_query': search_query,
        'total_contacts': total_contacts,
        'new_contacts': new_contacts,
        'in_progress_contacts': in_progress_contacts,
        'resolved_contacts': resolved_contacts,
    })


@login_required
def admin_contact_detail(request, contact_id):
    """
    Admin: View contact message details
    """
    if not (request.user.role == 'admin' or request.user.is_superuser):
        messages.error(request, 'Access denied.')
        return redirect('dashboard:home')
    
    from shop.models import Contact
    
    contact = get_object_or_404(Contact, id=contact_id)
    
    if request.method == 'POST':
        # Update admin notes
        admin_notes = request.POST.get('admin_notes', '')
        contact.admin_notes = admin_notes
        contact.save()
        messages.success(request, 'Admin notes updated successfully.')
        return redirect('dashboard:admin_contact_detail', contact_id=contact_id)
    
    return render(request, 'dashboard/admin_contact_detail.html', {
        'contact': contact
    })


@login_required
def admin_update_contact_status(request, contact_id):
    """
    Admin: Update contact message status
    """
    if not (request.user.role == 'admin' or request.user.is_superuser):
        messages.error(request, 'Access denied.')
        return redirect('dashboard:home')
    
    if request.method == 'POST':
        from shop.models import Contact
        
        try:
            contact = get_object_or_404(Contact, id=contact_id)
            new_status = request.POST.get('status')
            
            if new_status in ['new', 'in_progress', 'resolved', 'closed']:
                old_status = contact.status
                contact.status = new_status
                contact.save()
                
                messages.success(request, f'Contact status updated from "{old_status}" to "{new_status}".')
            else:
                messages.error(request, 'Invalid status selected.')
                
        except Contact.DoesNotExist:
            messages.error(request, 'Contact message not found.')
        except Exception as e:
            messages.error(request, f'Error updating status: {str(e)}')
    
    return redirect('dashboard:admin_contacts')


@login_required
def admin_marketplace_earnings(request):
    """
    Admin: View marketplace commission earnings and statistics
    """
    if not (request.user.role == 'admin' or request.user.is_superuser):
        messages.error(request, 'Access denied.')
        return redirect('dashboard:home')
    
    # Get marketplace wallet
    marketplace_wallet = MarketplaceWallet.get_instance()
    
    # Get marketplace transactions
    transactions = marketplace_wallet.transactions.all().order_by('-date')
    
    # Statistics
    total_commissions = marketplace_wallet.total_commission_earned
    current_balance = marketplace_wallet.balance
    commission_rate = float(marketplace_wallet.commission_rate) * 100
    vendor_percentage = 100 - commission_rate
    
    # Monthly commission earnings
    from django.utils import timezone
    from datetime import timedelta
    
    current_month = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    next_month = (current_month + timedelta(days=32)).replace(day=1)
    
    monthly_commissions = MarketplaceTransaction.objects.filter(
        transaction_type='commission',
        date__gte=current_month,
        date__lt=next_month
    ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
    
    # Commission by vendor
    vendor_commissions = MarketplaceTransaction.objects.filter(
        transaction_type='commission'
    ).values('vendor_username').annotate(
        total_commission=Sum('amount'),
        order_count=Count('related_order_id', distinct=True)
    ).order_by('-total_commission')[:10]
    
    # Calculate average commission per order for each vendor
    for vendor_data in vendor_commissions:
        if vendor_data['order_count'] > 0:
            vendor_data['avg_commission'] = vendor_data['total_commission'] / vendor_data['order_count']
        else:
            vendor_data['avg_commission'] = 0
    
    # Recent transactions with pagination
    paginator = Paginator(transactions, 20)
    page_number = request.GET.get('page')
    transactions = paginator.get_page(page_number)
    
    return render(request, 'dashboard/admin_marketplace_earnings.html', {
        'marketplace_wallet': marketplace_wallet,
        'transactions': transactions,
        'total_commissions': total_commissions,
        'current_balance': current_balance,
        'commission_rate': commission_rate,
        'vendor_percentage': vendor_percentage,
        'monthly_commissions': monthly_commissions,
        'vendor_commissions': vendor_commissions,
    })
