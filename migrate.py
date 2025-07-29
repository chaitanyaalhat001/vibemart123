#!/usr/bin/env python
"""
Migration script for Vercel deployment
Run this after deployment to set up the database
"""
import os
import django
from django.conf import settings
from django.core.management import execute_from_command_line

if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vibemart.settings')
    django.setup()
    
    # Run migrations
    print("Running migrations...")
    execute_from_command_line(['manage.py', 'migrate'])
    
    # Create superuser if it doesn't exist
    from django.contrib.auth import get_user_model
    User = get_user_model()
    
    if not User.objects.filter(is_superuser=True).exists():
        print("Creating admin user...")
        admin_user = User.objects.create_user(
            username='admin',
            email='admin@vibemart.com',
            password='admin123',
            role='admin',
            is_staff=True,
            is_superuser=True
        )
        print("Admin user created: admin/admin123")
    
    print("Migration completed successfully!") 