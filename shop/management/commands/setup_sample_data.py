from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from shop.models import Category, Product
from accounts.models import Wallet, WalletTransaction
from decimal import Decimal

User = get_user_model()


class Command(BaseCommand):
    help = 'Sets up sample data for VibeMart'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before creating sample data',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write('Clearing existing data...')
            User.objects.filter(is_superuser=False).delete()
            Category.objects.all().delete()
            Product.objects.all().delete()

        self.stdout.write('Creating sample data...')

        # Create categories
        categories_data = [
            {
                'name': 'Electronics',
                'description': 'Latest electronic gadgets and devices'
            },
            {
                'name': 'Clothing',
                'description': 'Fashion and apparel for everyone'
            },
            {
                'name': 'Books',
                'description': 'Books, magazines, and educational materials'
            },
            {
                'name': 'Home & Garden',
                'description': 'Home improvement and gardening supplies'
            },
            {
                'name': 'Sports',
                'description': 'Sports equipment and fitness gear'
            },
            {
                'name': 'Beauty',
                'description': 'Beauty and personal care products'
            }
        ]

        categories = {}
        for cat_data in categories_data:
            category, created = Category.objects.get_or_create(
                name=cat_data['name'],
                defaults={'description': cat_data['description']}
            )
            categories[cat_data['name']] = category
            if created:
                self.stdout.write(f'Created category: {category.name}')

        # Create admin user
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@vibemart.com',
                'first_name': 'Admin',
                'last_name': 'User',
                'role': 'admin',
                'is_staff': True,
                'is_superuser': True,
                'phone_number': '+1234567890',
                'address': '123 Admin Street, Admin City, AC 12345'
            }
        )
        if created:
            admin_user.set_password('admin123')
            admin_user.save()
            self.stdout.write('Created admin user: admin/admin123')

        # Create sample vendors
        vendors_data = [
            {
                'username': 'vendor1',
                'email': 'vendor1@vibemart.com',
                'first_name': 'John',
                'last_name': 'Electronics',
                'phone_number': '+1234567891',
                'address': '456 Vendor Street, Tech City, TC 12345'
            },
            {
                'username': 'vendor2',
                'email': 'vendor2@vibemart.com',
                'first_name': 'Sarah',
                'last_name': 'Fashion',
                'phone_number': '+1234567892',
                'address': '789 Fashion Ave, Style City, SC 12345'
            },
            {
                'username': 'vendor3',
                'email': 'vendor3@vibemart.com',
                'first_name': 'Mike',
                'last_name': 'Books',
                'phone_number': '+1234567893',
                'address': '321 Book Street, Knowledge City, KC 12345'
            }
        ]

        vendors = {}
        for vendor_data in vendors_data:
            vendor, created = User.objects.get_or_create(
                username=vendor_data['username'],
                defaults={
                    **vendor_data,
                    'role': 'vendor'
                }
            )
            if created:
                vendor.set_password('vendor123')
                vendor.save()
                self.stdout.write(f'Created vendor: {vendor.username}/vendor123')
            vendors[vendor_data['username']] = vendor

        # Create sample users
        users_data = [
            {
                'username': 'user1',
                'email': 'user1@example.com',
                'first_name': 'Alice',
                'last_name': 'Johnson',
                'phone_number': '+1234567894',
                'address': '111 User Lane, Customer City, CC 12345'
            },
            {
                'username': 'user2',
                'email': 'user2@example.com',
                'first_name': 'Bob',
                'last_name': 'Smith',
                'phone_number': '+1234567895',
                'address': '222 Buyer Road, Shopper Town, ST 12345'
            }
        ]

        for user_data in users_data:
            user, created = User.objects.get_or_create(
                username=user_data['username'],
                defaults={
                    **user_data,
                    'role': 'user'
                }
            )
            if created:
                user.set_password('user123')
                user.save()
                
                # Add money to user wallets
                wallet = user.wallet
                wallet.add_money(Decimal('1000.00'))
                WalletTransaction.objects.create(
                    wallet=wallet,
                    transaction_type='credit',
                    amount=Decimal('1000.00'),
                    description='Initial wallet balance'
                )
                self.stdout.write(f'Created user: {user.username}/user123 (Wallet: $1000)')

        # Create sample products
        products_data = [
            # Electronics
            {
                'name': 'Smartphone Pro Max',
                'description': 'Latest flagship smartphone with advanced features and AI capabilities.',
                'price': Decimal('999.99'),
                'category': 'Electronics',
                'stock': 50,
                'vendor': 'vendor1'
            },
            {
                'name': 'Wireless Earbuds',
                'description': 'Premium wireless earbuds with noise cancellation and long battery life.',
                'price': Decimal('199.99'),
                'category': 'Electronics',
                'stock': 100,
                'vendor': 'vendor1'
            },
            {
                'name': 'Smart Watch',
                'description': 'Feature-rich smartwatch with health monitoring and GPS.',
                'price': Decimal('299.99'),
                'category': 'Electronics',
                'stock': 75,
                'vendor': 'vendor1'
            },
            
            # Clothing
            {
                'name': 'Classic Denim Jacket',
                'description': 'Timeless denim jacket perfect for any casual occasion.',
                'price': Decimal('79.99'),
                'category': 'Clothing',
                'stock': 30,
                'vendor': 'vendor2'
            },
            {
                'name': 'Cotton T-Shirt',
                'description': 'Comfortable 100% cotton t-shirt in various colors.',
                'price': Decimal('24.99'),
                'category': 'Clothing',
                'stock': 200,
                'vendor': 'vendor2'
            },
            {
                'name': 'Running Shoes',
                'description': 'High-performance running shoes with superior comfort and support.',
                'price': Decimal('129.99'),
                'category': 'Sports',
                'stock': 60,
                'vendor': 'vendor2'
            },
            
            # Books
            {
                'name': 'Python Programming Guide',
                'description': 'Comprehensive guide to Python programming for beginners and experts.',
                'price': Decimal('39.99'),
                'category': 'Books',
                'stock': 40,
                'vendor': 'vendor3'
            },
            {
                'name': 'Digital Marketing Handbook',
                'description': 'Essential strategies and techniques for modern digital marketing.',
                'price': Decimal('34.99'),
                'category': 'Books',
                'stock': 25,
                'vendor': 'vendor3'
            },
            
            # Home & Garden
            {
                'name': 'Coffee Maker Deluxe',
                'description': 'Premium coffee maker with programmable features and thermal carafe.',
                'price': Decimal('159.99'),
                'category': 'Home & Garden',
                'stock': 20,
                'vendor': 'vendor1'
            },
            {
                'name': 'Garden Tool Set',
                'description': 'Complete set of essential gardening tools for all your gardening needs.',
                'price': Decimal('89.99'),
                'category': 'Home & Garden',
                'stock': 35,
                'vendor': 'vendor2'
            },
            
            # Beauty
            {
                'name': 'Skincare Starter Kit',
                'description': 'Complete skincare routine kit with cleanser, toner, and moisturizer.',
                'price': Decimal('49.99'),
                'category': 'Beauty',
                'stock': 80,
                'vendor': 'vendor2'
            },
            {
                'name': 'Hair Care Bundle',
                'description': 'Professional-grade shampoo and conditioner set for all hair types.',
                'price': Decimal('29.99'),
                'category': 'Beauty',
                'stock': 60,
                'vendor': 'vendor3'
            }
        ]

        for product_data in products_data:
            category = categories[product_data['category']]
            vendor = vendors[product_data['vendor']]
            
            product, created = Product.objects.get_or_create(
                name=product_data['name'],
                vendor=vendor,
                defaults={
                    'description': product_data['description'],
                    'price': product_data['price'],
                    'category': category,
                    'stock': product_data['stock'],
                    'is_active': True
                }
            )
            if created:
                self.stdout.write(f'Created product: {product.name}')

        self.stdout.write(
            self.style.SUCCESS('Sample data created successfully!')
        )
        self.stdout.write('\nLogin credentials:')
        self.stdout.write('Admin: admin/admin123')
        self.stdout.write('Vendors: vendor1/vendor123, vendor2/vendor123, vendor3/vendor123')
        self.stdout.write('Users: user1/user123, user2/user123 (Both have $1000 in wallet)') 