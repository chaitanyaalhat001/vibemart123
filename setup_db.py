import os
import psycopg2
import django
from django.conf import settings

# Database connection settings
DATABASE_CONFIG = {
    'host': 'db.cmfaakkyzvknqzyfjrgl.supabase.co',
    'database': 'postgres',
    'user': 'postgres',
    'password': 'NLoVbIpaZDorGoBu',
    'port': 5432
}

def setup_database():
    print("Setting up database connection...")
    
    # Configure Django settings
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vibemart.settings')
    
    # Override database settings for remote connection
    settings.configure(
        DEBUG=False,
        DATABASES={
            'default': {
                'ENGINE': 'django.db.backends.postgresql',
                'NAME': DATABASE_CONFIG['database'],
                'USER': DATABASE_CONFIG['user'],
                'PASSWORD': DATABASE_CONFIG['password'],
                'HOST': DATABASE_CONFIG['host'],
                'PORT': DATABASE_CONFIG['port'],
            }
        },
        INSTALLED_APPS=[
            'django.contrib.admin',
            'django.contrib.auth',
            'django.contrib.contenttypes',
            'django.contrib.sessions',
            'django.contrib.messages',
            'django.contrib.staticfiles',
            'accounts',
            'shop',
            'dashboard',
        ],
        AUTH_USER_MODEL='accounts.User',
        SECRET_KEY='temp-key-for-migration',
        USE_TZ=True,
    )
    
    django.setup()
    
    # Import Django management
    from django.core.management import execute_from_command_line
    
    print("Running migrations...")
    execute_from_command_line(['manage.py', 'migrate'])
    
    print("Creating admin user...")
    from django.contrib.auth import get_user_model
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
        print("Admin user created: admin/admin123")
    else:
        print("Admin user already exists")
    
    print("Database setup completed!")

if __name__ == '__main__':
    setup_database() 