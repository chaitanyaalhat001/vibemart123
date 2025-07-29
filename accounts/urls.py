from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    # Authentication URLs
    path('login/', views.user_login, name='login'),
    path('vendor-login/', views.vendor_login, name='vendor_login'),
    path('admin-login/', views.admin_login, name='admin_login'),
    path('logout/', views.user_logout, name='logout'),
    
    # Registration URLs
    path('register/', views.user_register, name='register'),
    path('vendor-register/', views.vendor_register, name='vendor_register'),
    
    # Profile URLs
    path('profile/', views.profile_view, name='profile'),
    path('password-change/', views.password_change_view, name='password_change'),
    path('wallet/', views.wallet_view, name='wallet'),
    
    # AJAX URLs
    path('add-money/', views.add_money, name='add_money'),
] 