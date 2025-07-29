# VibeMart - Django E-commerce Platform

VibeMart is a comprehensive e-commerce platform built with Django, featuring role-based access control for Users, Vendors, and Administrators. The platform includes a dummy wallet system for secure transactions and provides a complete shopping experience.

## 🚀 Features

### 🏠 **Homepage**
- Hero section with call-to-action buttons
- Category browsing
- Featured products showcase
- Vendor registration promotion

### 👤 **User Features**
- User registration and authentication
- Product browsing with search and filtering
- Shopping cart functionality (session-based for guests, persistent for users)
- Dummy wallet system with transaction history
- Order placement and tracking
- Order history and status tracking
- Profile management

### 🏪 **Vendor Features**
- Self-registration without admin approval
- Product management (add, edit, delete)
- Inventory tracking
- Sales analytics and reporting
- Revenue dashboard
- Order notifications

### 🛠 **Admin Features**
- Comprehensive admin dashboard
- User management (view all users, vendors)
- Product oversight
- Transaction monitoring
- System-wide analytics

### 🔧 **Technical Features**
- Role-based access control (User, Vendor, Admin)
- Session-based cart for guest users
- Responsive Bootstrap UI
- AJAX functionality for cart operations
- Image upload for products
- Search functionality
- Pagination
- Django signals for automatic wallet creation

## 📋 Requirements

- Python 3.8+
- Django 5.2+
- SQLite (for development)
- Pillow (for image handling)

## 🛠 Installation & Setup

### 1. Clone the Repository
```bash
git clone <repository-url>
cd vibemart
```

### 2. Install Dependencies
```bash
pip install django pillow
```

### 3. Run Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 4. Create Sample Data
```bash
python manage.py setup_sample_data
```

### 5. Run the Development Server
```bash
python manage.py runserver
```

Visit `http://127.0.0.1:8000` to access the application.

## 👥 Default Login Credentials

### Admin
- **Username:** admin
- **Password:** admin123
- **Access:** Full system administration

### Vendors
- **Username:** vendor1, vendor2, vendor3
- **Password:** vendor123
- **Access:** Product management and analytics

### Users
- **Username:** user1, user2
- **Password:** user123
- **Access:** Shopping and wallet management
- **Wallet Balance:** $1000 each

## 📁 Project Structure

```
vibemart/
├── accounts/           # User authentication and wallet management
│   ├── models.py      # User, Wallet, WalletTransaction models
│   ├── views.py       # Authentication views
│   ├── forms.py       # Registration and profile forms
│   └── admin.py       # Admin configuration
├── shop/              # Product and order management
│   ├── models.py      # Product, Category, Cart, Order models
│   ├── views.py       # Shopping and cart views
│   ├── forms.py       # Product management forms
│   └── admin.py       # Admin configuration
├── dashboard/         # Role-specific dashboards
│   ├── views.py       # Dashboard views for all roles
│   └── urls.py        # Dashboard routing
├── templates/         # HTML templates
│   ├── base.html      # Base template with Bootstrap
│   ├── accounts/      # Authentication templates
│   ├── shop/          # Shopping templates
│   └── dashboard/     # Dashboard templates
├── static/           # Static files
│   ├── css/          # Custom CSS
│   ├── js/           # Custom JavaScript
│   └── images/       # Static images
└── media/            # User uploaded files
```

## 🎯 Key Models

### User Model
- Extended AbstractUser with role field
- Roles: user, vendor, admin
- Additional fields: phone_number, address

### Product Model
- Name, description, price, category
- Stock management
- Vendor relationship
- Image upload

### Order System
- Order with unique tracking ID
- OrderItem for individual products
- Status tracking (pending, confirmed, shipped, delivered, cancelled)

### Wallet System
- Decimal-based balance management
- Transaction history
- Credit/Debit operations

## 🔄 Workflow

### User Journey
1. Browse products without login
2. Register/Login to add items to cart
3. Add money to wallet
4. Checkout and place orders
5. Track order status

### Vendor Journey
1. Register as vendor
2. Login to dashboard
3. Add/manage products
4. View sales analytics
5. Track revenue

### Admin Journey
1. Login to admin dashboard
2. Monitor users and vendors
3. Oversee all products
4. View system analytics

## 🎨 UI/UX Features

- **Responsive Design:** Bootstrap-based responsive layout
- **Modern UI:** Clean, professional design with animations
- **User-Friendly:** Intuitive navigation and clear CTAs
- **Interactive Elements:** AJAX cart operations, live search
- **Notifications:** Success/error messages for user feedback

## 🔒 Security Features

- Django's built-in authentication
- CSRF protection
- Role-based access control
- Secure wallet transactions
- Session management

## 📊 Business Logic

### Inventory Management
- Real-time stock tracking
- Automatic stock reduction on orders
- Out-of-stock indicators

### Pricing System
- Decimal-based pricing for accuracy
- Cart total calculations
- Wallet balance validations

### Order Processing
1. Cart validation
2. Stock verification
3. Wallet balance check
4. Order creation
5. Stock reduction
6. Payment processing
7. Order confirmation

## 🚀 Future Enhancements

- Email notifications
- Payment gateway integration
- Advanced search and filtering
- Product reviews and ratings
- Multi-vendor messaging system
- Advanced analytics dashboard
- Mobile app API
- Social media integration

## 🧪 Testing

The project includes sample data for testing all features:
- 6 product categories
- 12+ sample products
- 3 vendor accounts
- 2 user accounts with wallet balance
- 1 admin account

## 📞 Support

For questions or issues, please refer to the Django documentation or create an issue in the project repository.

## 📝 License

This project is created for educational purposes and follows Django best practices for e-commerce development.

---

**Built with ❤️ using Django and Bootstrap** 