from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.db import transaction
import json
from .models import User, Wallet, WalletTransaction
from .forms import UserRegistrationForm, VendorRegistrationForm, UserProfileForm


def user_login(request):
    """
    User login view
    """
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user is not None and user.role == 'user':
            login(request, user)
            messages.success(request, f'Welcome back, {user.first_name or user.username}!')
            return redirect('dashboard:home')
        else:
            messages.error(request, 'Invalid credentials or account type.')
    
    return render(request, 'accounts/login.html', {'user_type': 'User'})


def vendor_login(request):
    """
    Vendor login view
    """
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user is not None and user.role == 'vendor':
            login(request, user)
            messages.success(request, f'Welcome back, {user.first_name or user.username}!')
            return redirect('dashboard:home')
        else:
            messages.error(request, 'Invalid credentials or account type.')
    
    return render(request, 'accounts/login.html', {'user_type': 'Vendor'})


def admin_login(request):
    """
    Admin login view
    """
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user is not None and (user.role == 'admin' or user.is_superuser):
            login(request, user)
            messages.success(request, f'Welcome back, {user.first_name or user.username}!')
            return redirect('dashboard:home')
        else:
            messages.error(request, 'Invalid credentials or account type.')
    
    return render(request, 'accounts/login.html', {'user_type': 'Admin'})


def user_register(request):
    """
    User registration view
    """
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.role = 'user'
            user.save()
            messages.success(request, 'Registration successful! Please login.')
            return redirect('accounts:login')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'accounts/register.html', {
        'form': form, 
        'user_type': 'User'
    })


def vendor_register(request):
    """
    Vendor registration view
    """
    if request.method == 'POST':
        form = VendorRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.role = 'vendor'
            user.save()
            messages.success(request, 'Vendor registration successful! Please login.')
            return redirect('accounts:vendor_login')
    else:
        form = VendorRegistrationForm()
    
    return render(request, 'accounts/register.html', {
        'form': form, 
        'user_type': 'Vendor'
    })


@login_required
def profile_view(request):
    """
    User profile view and update
    """
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('accounts:profile')
    else:
        form = UserProfileForm(instance=request.user)
    
    return render(request, 'accounts/profile.html', {'form': form})


@login_required
def password_change_view(request):
    """
    Password change view for all users
    """
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important to keep user logged in
            messages.success(request, 'Your password was successfully updated!')
            return redirect('accounts:profile')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = PasswordChangeForm(request.user)
    
    return render(request, 'accounts/password_change.html', {'form': form})


@login_required
def wallet_view(request):
    """
    Wallet view for users
    """
    if request.user.role != 'user':
        messages.error(request, 'Access denied.')
        return redirect('dashboard:home')
    
    wallet = request.user.wallet
    transactions = wallet.transactions.all()[:20]  # Latest 20 transactions
    
    return render(request, 'accounts/wallet.html', {
        'wallet': wallet,
        'transactions': transactions
    })


@login_required
@require_http_methods(["POST"])
def add_money(request):
    """
    Add money to user wallet (AJAX endpoint)
    """
    if request.user.role != 'user':
        return JsonResponse({'success': False, 'message': 'Access denied'})
    
    try:
        data = json.loads(request.body)
        amount = float(data.get('amount', 0))
        
        if amount <= 0:
            return JsonResponse({'success': False, 'message': 'Invalid amount'})
        
        if amount > 10000:  # Maximum limit
            return JsonResponse({'success': False, 'message': 'Maximum amount is $10,000'})
        
        with transaction.atomic():
            wallet = request.user.wallet
            wallet.add_money(amount)
            
            # Create transaction record
            WalletTransaction.objects.create(
                wallet=wallet,
                transaction_type='credit',
                amount=amount,
                description=f'Added ${amount} to wallet'
            )
        
        return JsonResponse({
            'success': True, 
            'message': f'${amount} added to wallet successfully!',
            'new_balance': float(wallet.balance)
        })
        
    except (json.JSONDecodeError, ValueError, KeyError):
        return JsonResponse({'success': False, 'message': 'Invalid request data'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': 'An error occurred'})


def user_logout(request):
    """
    Logout view
    """
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('shop:home')
