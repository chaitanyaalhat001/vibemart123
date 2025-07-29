from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    # Main dashboard
    path('', views.dashboard_home, name='home'),
    
    # Vendor URLs
    path('products/', views.vendor_products, name='vendor_products'),
    path('add-product/', views.add_product, name='add_product'),
    path('edit-product/<int:product_id>/', views.edit_product, name='edit_product'),
    path('delete-product/<int:product_id>/', views.delete_product, name='delete_product'),
    path('analytics/', views.vendor_analytics, name='vendor_analytics'),
    path('orders/', views.vendor_orders, name='vendor_orders'),
    path('order/<uuid:order_id>/', views.vendor_order_detail, name='vendor_order_detail'),
    path('update-order-status/<uuid:order_id>/', views.update_order_status, name='update_order_status'),
    path('wallet/', views.vendor_wallet, name='vendor_wallet'),
    path('withdraw-money/', views.withdraw_money, name='withdraw_money'),
    
    # Admin URLs
    path('admin/users/', views.admin_users, name='admin_users'),
    path('admin/users/remove/<int:user_id>/', views.admin_remove_user, name='admin_remove_user'),
    path('admin/users/<int:user_id>/products/', views.admin_user_products, name='admin_user_products'),
    path('admin/users/<int:user_id>/wallet/', views.admin_user_wallet, name='admin_user_wallet'),
    path('admin/products/', views.admin_products, name='admin_products'),
    path('admin/products/remove/<int:product_id>/', views.admin_remove_product, name='admin_remove_product'),
    path('admin/orders/', views.admin_orders, name='admin_orders'),
    path('admin/contacts/', views.admin_contacts, name='admin_contacts'),
    path('admin/contacts/<int:contact_id>/', views.admin_contact_detail, name='admin_contact_detail'),
    path('admin/contacts/<int:contact_id>/update-status/', views.admin_update_contact_status, name='admin_update_contact_status'),
    path('admin/marketplace-earnings/', views.admin_marketplace_earnings, name='admin_marketplace_earnings'),
] 