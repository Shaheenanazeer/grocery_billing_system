# 🛒 Grocery Store Management System

A complete grocery store management system built with Streamlit featuring user authentication, admin dashboard, order management, and email notifications.

## ✨ Features

### 🔐 Authentication System
- User registration with email validation
- Secure password hashing with bcrypt
- Role-based access (Admin/User)
- Session management

### 👤 User Features
- Browse products with beautiful UI
- Add/remove items from cart
- Place orders with automatic bill generation
- View order history with status tracking
- Automatic discount calculation (10% for orders ≥ Rs 1000, 15% for orders ≥ Rs 2000)
- Email notifications for account creation and order updates

### 🔧 Admin Features
- Dashboard with overview statistics
- User management (view all users and their order history)
- Product management (add, update, delete products)
- Order management with status updates
- Real-time email notifications to customers

### 📧 Email Notifications
- Welcome email on account creation
- Order confirmation emails
- Order status update notifications
- Beautiful HTML email templates

## 🚀 Setup Instructions

### 1. Install Dependencies

```bash
# Install using pip
pip install streamlit bcrypt email-validator

# Or using uv (recommended)
uv sync
```

### 2. Configure Email Settings

Create a `.env` file in the project root and add your email credentials:

```env
# Email Configuration
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_EMAIL=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# Admin Credentials
ADMIN_EMAIL=admin@grocery.com
ADMIN_PASSWORD=admin123
```

#### For Gmail Users:
1. Enable 2-factor authentication on your Gmail account
2. Generate an app-specific password:
   - Go to Google Account settings
   - Security → 2-Step Verification → App passwords
   - Generate password for "Mail"
3. Use this app password in the config

### 3. Run the Application

```bash
streamlit run main.py
```

## 🎯 Default Admin Credentials

- **Email:** `admin@grocery.com`
- **Password:** `admin123`

## 📱 How to Use

### For Users:
1. Sign up with your email and create a password
2. Login to access the store
3. Browse products and add items to cart
4. Generate bill and place orders
5. Track your orders in "My Orders" section

### For Admins:
1. Login with admin credentials
2. Access admin dashboard to:
   - View system overview and statistics
   - Manage users and view their activity
   - Add, update, or delete products
   - Manage orders and update status
   - Send automatic email notifications

## 🎨 Features Highlights

### User Dashboard
- 🏪 Browse Products - View all available products
- 🛒 Add to Cart - Search and add products
- 👀 View Cart - Review items before checkout
- ❌ Remove Items - Manage cart contents
- 💳 Generate Bill - Automatic discount and tax calculation
- 📋 My Orders - Track order status

### Admin Dashboard
- 📊 Overview - System statistics and metrics
- 👥 Manage Users - View user accounts and order history
- 🛍️ Manage Products - Full CRUD operations
- 📦 Manage Orders - Update order status with email notifications

## 🛡️ Security Features

- Password hashing with bcrypt
- Session-based authentication
- Role-based access control
- Email validation
- Input sanitization

## 📧 Email Templates

The system includes beautiful HTML email templates for:
- Welcome messages for new users
- Order confirmations
- Order status updates (Pending, Shipped, Delivered, Cancelled)

## 🗂️ File Structure

```
project/
├── main.py              # Main application
├── config.py            # Email configuration
├── users.json           # User data storage
├── products.json        # Product inventory
├── orders.json          # Order records
├── pyproject.toml       # Dependencies
└── README.md           # This file
```

## 🔧 Customization

### Adding New Products
Admins can add products through the admin dashboard or by editing `products.json`:

```json
{
    "product_name": {
        "price": 100,
        "unit": "kg"
    }
}
```

### Email Templates
Customize email templates in the `create_welcome_email()` and `create_order_email()` functions in `main.py`.

## 🐛 Troubleshooting

### Email Not Sending
1. Check your email credentials in `config.py`
2. Ensure app password is correct (for Gmail)
3. Check spam folder for received emails

### Login Issues
- Make sure you're using the correct email format
- Password is case-sensitive
- Default admin: `admin@grocery.com` / `admin123`

### Installation Issues
```bash
# If you get import errors, try:
pip install --upgrade streamlit bcrypt email-validator
```

## 🎉 Success!

Your grocery store management system is now ready! Users can register, shop, and place orders while admins can manage the entire system with beautiful email notifications keeping everyone informed.

---

**Happy Shopping! 🛒✨**
