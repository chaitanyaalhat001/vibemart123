from django.urls import path
from . import views

app_name = 'shop'

urlpatterns = [
    # Main pages
    path('', views.home, name='home'),
    path('about/', views.about_us, name='about_us'),
    path('contact/', views.contact_us, name='contact_us'),
    path('products/', views.product_list, name='products'),
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),
    
    # Cart functionality
    path('cart/', views.cart_view, name='cart'),
    path('add-to-cart/', views.add_to_cart, name='add_to_cart'),
    path('update-cart-item/', views.update_cart_item, name='update_cart_item'),
    
    # Checkout and orders
    path('checkout/', views.checkout, name='checkout'),
    path('order-confirmation/<uuid:order_id>/', views.order_confirmation, name='order_confirmation'),
    path('orders/', views.order_list, name='orders'),
    path('order/<uuid:order_id>/', views.order_detail, name='order_detail'),
    
    # AJAX endpoints
    path('search/', views.search_products, name='search'),
] 