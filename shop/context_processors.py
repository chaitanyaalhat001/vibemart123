from .models import CartItem


def cart_count(request):
    """
    Context processor to provide cart count across all templates
    """
    count = 0
    
    if request.user.is_authenticated:
        count = CartItem.objects.filter(user=request.user).count()
    elif hasattr(request, 'session') and request.session.session_key:
        count = CartItem.objects.filter(session_key=request.session.session_key).count()
    
    return {'cart_count': count} 