from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from .models import User, Wallet


@receiver(post_save, sender=User)
def create_user_wallet(sender, instance, created, **kwargs):
    """
    Create wallet automatically when a new user is created
    """
    if created:
        Wallet.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_wallet(sender, instance, **kwargs):
    """
    Save the user's wallet when the user is saved
    """
    if hasattr(instance, 'wallet'):
        instance.wallet.save()
    else:
        # Create wallet if it doesn't exist
        Wallet.objects.create(user=instance) 