#!/usr/bin/env python
"""
Production database setup for Vercel deployment
Run this locally to set up your remote Supabase database
"""
import os
import sys
import django
from pathlib import Path

# Add the project directory to Python path
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))

# Set environment variables for production database
os.environ['DATABASE_HOST'] = 'db.cmfaakkyzvknqzyfjrgl.supabase.co'
os.environ['DATABASE_NAME'] = 'postgres'
os.environ['DATABASE_USER'] = 'postgres'
os.environ['DATABASE_PASSWORD'] = 'NLoVbIpaZDorGoBu'
os.environ['DATABASE_PORT'] = '5432'
os.environ['SECRET_KEY'] = 'django-insecure-@nhnlqimd#h8v!u4xunxx1#23e$b@)q@3#(*1k6*=_9h@p^1=4'
os.environ['DEBUG'] = 'False'

# Set Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vibemart.settings')

# Initialize Django
django.setup()

# Now import Django modules
from django.core.management import execute_from_command_line
from django.contrib.auth import get_user_model

def main():
    print("🚀 Setting up VibeMart production database...")
    
    # Run migrations
    print("📦 Running database migrations...")
    execute_from_command_line(['manage.py', 'migrate'])
    
    # Create admin user
    print("👤 Creating admin user...")
    User = get_user_model()
    
    if not User.objects.filter(username='admin').exists():
        admin_user = User.objects.create_user(
            username='admin',
            email='admin@vibemart.com',
            password='admin123',
            role='admin',
            is_staff=True,
            is_superuser=True
        )
        print("✅ Admin user created: admin/admin123")
    else:
        print("ℹ️  Admin user already exists")
    
    # Optional: Create sample data
    try:
        print("📝 Creating sample data...")
        execute_from_command_line(['manage.py', 'setup_sample_data'])
        print("✅ Sample data created successfully!")
    except Exception as e:
        print(f"ℹ️  Sample data creation skipped: {e}")
    
    print("🎉 Production database setup completed!")
    print("🌐 Your VibeMart app should now work on Vercel!")

if __name__ == '__main__':
    main() 