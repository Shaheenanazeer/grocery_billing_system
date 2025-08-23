import streamlit as st
import json
import os
import bcrypt
import smtplib
import uuid
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email_validator import validate_email, EmailNotValidError

from dotenv import load_dotenv

load_dotenv()

EMAIL_HOST = os.getenv("SMTP_SERVER")
EMAIL_PORT = os.getenv("SMTP_PORT")
SMTP_EMAIL = os.getenv("SMTP_EMAIL")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")



# File paths
PRODUCTS_FILE = "products.json"
USERS_FILE = "users.json"
ORDERS_FILE = "orders.json"
TAX_RATE = 0.05

# Use environment variables for email configuration
EMAIL_HOST = EMAIL_HOST or "smtp.gmail.com"
EMAIL_PORT = int(EMAIL_PORT) if EMAIL_PORT else 587
EMAIL_USER = SMTP_EMAIL
EMAIL_PASSWORD = SMTP_PASSWORD

def send_email(to_email, subject, body):
    """Send email to user"""
    # Check if email is properly configured
    if not EMAIL_USER or not EMAIL_PASSWORD:
        st.info("📧 Email not configured. Please update your .env file with SMTP_EMAIL and SMTP_PASSWORD to enable email notifications.")
        return False
    
    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_USER
        msg['To'] = to_email
        msg['Subject'] = subject
        
        msg.attach(MIMEText(body, 'html'))
        
        server = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT)
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        st.warning(f"📧 Email notification failed. Please check your email configuration in config.py")
        st.info("The system will continue to work without email notifications.")
        return False

def create_welcome_email(username):
    """Create welcome email template"""
    return f"""
    <html>
    <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; text-align: center; border-radius: 10px;">
            <h1 style="color: white; margin: 0;">🛒 Welcome to Our Grocery Store!</h1>
        </div>
        
        <div style="padding: 30px; background-color: #f8f9fa; border-radius: 10px; margin-top: 20px;">
            <h2 style="color: #333;">Hello {username}! 👋</h2>
            <p style="color: #666; font-size: 16px; line-height: 1.6;">
                Your account has been successfully created! We're thrilled to have you as part of our grocery family.
            </p>
            
            <div style="background-color: white; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #28a745;">
                <h3 style="color: #28a745; margin-top: 0;">🎉 Account Created Successfully!</h3>
                <p style="color: #666; margin-bottom: 0;">
                    You can now browse our products, add items to your cart, and place orders with ease.
                </p>
            </div>
            
            <p style="color: #666; font-size: 16px;">
                Start shopping now and enjoy fresh groceries delivered to your doorstep!
            </p>
            
            <div style="text-align: center; margin-top: 30px;">
                <p style="color: #999; font-size: 14px;">
                    Thank you for choosing our grocery store! 🙏
                </p>
            </div>
        </div>
    </body>
    </html>
    """

def create_order_email(username, order_id, total, status="pending"):
    """Create order confirmation email"""
    status_color = {"pending": "#ffc107", "shipped": "#17a2b8", "delivered": "#28a745", "cancelled": "#dc3545"}
    
    return f"""
    <html>
    <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
        <div style="background: linear-gradient(135deg, #28a745 0%, #20c997 100%); padding: 30px; text-align: center; border-radius: 10px;">
            <h1 style="color: white; margin: 0;">📦 Order Update</h1>
        </div>
        
        <div style="padding: 30px; background-color: #f8f9fa; border-radius: 10px; margin-top: 20px;">
            <h2 style="color: #333;">Hello {username}! 👋</h2>
            
            <div style="background-color: white; padding: 20px; border-radius: 8px; margin: 20px 0;">
                <h3 style="color: #333; margin-top: 0;">Order Details:</h3>
                <p><strong>Order ID:</strong> {order_id}</p>
                <p><strong>Total Amount:</strong> Rs {total:.2f}</p>
                <p><strong>Status:</strong> <span style="background-color: {status_color.get(status, '#666')}; color: white; padding: 5px 10px; border-radius: 15px; font-size: 12px;">{status.upper()}</span></p>
                <p><strong>Date:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            </div>
            
            <div style="background-color: {status_color.get(status, '#666')}; color: white; padding: 15px; border-radius: 8px; text-align: center;">
                <h3 style="margin: 0;">Your order status: {status.upper()}</h3>
            </div>
            
            <p style="color: #666; font-size: 16px; margin-top: 20px;">
                Thank you for shopping with us! We'll keep you updated on your order progress.
            </p>
        </div>
    </body>
    </html>
    """

# Authentication functions
def hash_password(password):
    """Hash password using bcrypt"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

def verify_password(password, hashed):
    """Verify password against hash"""
    return bcrypt.checkpw(password.encode('utf-8'), hashed)

def load_users():
    """Load users from file"""
    try:
        if os.path.exists(USERS_FILE):
            with open(USERS_FILE, "r") as f:
                users = json.load(f)
                # Convert password back to bytes for existing users
                for user in users.values():
                    if isinstance(user.get('password'), str):
                        user['password'] = user['password'].encode('latin-1')
                return users
        return {}
    except Exception:
        return {}

def save_users(users):
    """Save users to file"""
    try:
        # Convert bytes to string for JSON serialization
        users_to_save = {}
        for email, user_data in users.items():
            users_to_save[email] = user_data.copy()
            if isinstance(user_data.get('password'), bytes):
                users_to_save[email]['password'] = user_data['password'].decode('latin-1')
        
        with open(USERS_FILE, "w") as f:
            json.dump(users_to_save, f, indent=4)
        return True
    except Exception:
        return False

def load_orders():
    """Load orders from file"""
    try:
        if os.path.exists(ORDERS_FILE):
            with open(ORDERS_FILE, "r") as f:
                return json.load(f)
        return []
    except Exception:
        return []

def save_orders(orders):
    """Save orders to file"""
    try:
        with open(ORDERS_FILE, "w") as f:
            json.dump(orders, f, indent=4)
        return True
    except Exception:
        return False

# Product functions (from original code)
def load_products():
    try:
        if os.path.exists(PRODUCTS_FILE):
            with open(PRODUCTS_FILE, "r") as f:
                return json.load(f)
        else:
            default_products = {
                "apple": {"price": 100, "unit": "kg"},
                "banana": {"price": 50, "unit": "dozen"},
                "milk": {"price": 120, "unit": "litre"},
                "bread": {"price": 80, "unit": "loaf"},
                "egg": {"price": 15, "unit": "piece"}
            }
            save_products(default_products)
            return default_products
    except (json.JSONDecodeError, IOError):
        return {
            "apple": {"price": 100, "unit": "kg"},
            "banana": {"price": 50, "unit": "dozen"},
            "milk": {"price": 120, "unit": "litre"},
            "bread": {"price": 80, "unit": "loaf"},
            "egg": {"price": 15, "unit": "piece"}
        }

def save_products(products):
    try:
        with open(PRODUCTS_FILE, "w") as f:
            json.dump(products, f, indent=4)
        return True
    except IOError:
        return False

def validate_email_format(email):
    """Validate email format"""
    try:
        validate_email(email)
        return True
    except EmailNotValidError:
        return False

def signup_page():
    """User signup page"""
    st.title("🛒 Create Your Account")
    
    with st.form("signup_form"):
        st.subheader("Sign Up")
        username = st.text_input("Full Name", placeholder="Enter your full name")
        email = st.text_input("Email", placeholder="Enter your email address")
        password = st.text_input("Password", type="password", placeholder="Enter password")
        confirm_password = st.text_input("Confirm Password", type="password", placeholder="Confirm your password")
        
        submitted = st.form_submit_button("Create Account", use_container_width=True)
        
        if submitted:
            users = load_users()
            
            if not username or not email or not password:
                st.error("All fields are required!")
            elif not validate_email_format(email):
                st.error("Please enter a valid email address!")
            elif len(password) < 6:
                st.error("Password must be at least 6 characters long!")
            elif password != confirm_password:
                st.error("Passwords don't match!")
            elif email in users:
                st.error("Email already registered!")
            else:
                # Create new user
                hashed_password = hash_password(password)
                users[email] = {
                    "username": username,
                    "password": hashed_password,
                    "role": "user",
                    "created_at": datetime.now().isoformat()
                }
                
                if save_users(users):
                    # Send welcome email
                    welcome_email = create_welcome_email(username)
                    if send_email(email, "Welcome to Our Grocery Store! 🛒", welcome_email):
                        st.success("Account created successfully! Welcome email sent. Please login.")
                    else:
                        st.success("Account created successfully! Please login.")
                    st.balloons()
                else:
                    st.error("Failed to create account. Please try again.")
def login_page():
    """User login page"""
    st.title("🔐 Login to Your Account")
    with st.form("login_form"):
        st.subheader("Login")
        email = st.text_input("Email", placeholder="Enter your email address")
        password = st.text_input("Password", type="password", placeholder="Enter your password")
        
        submitted = st.form_submit_button("Login", use_container_width=True)
        
        if submitted:
            users = load_users()
            
            if not email or not password:
                st.error("Please enter both email and password!")
            elif email not in users:
                st.error("Email not found! Please sign up first.")
            elif not verify_password(password, users[email]["password"]):
                st.error("Incorrect password!")
            else:
                # Set session state
                st.session_state.logged_in = True
                st.session_state.user_email = email
                st.session_state.username = users[email]["username"]
                st.session_state.user_role = users[email]["role"]
                st.session_state.cart = {}
                st.success(f"Welcome back, {users[email]['username']}!")
                st.rerun()

def auth_page():
    """Authentication page with login/signup tabs"""
    st.set_page_config(
        page_title="Grocery Store - Authentication",
        page_icon="🛒",
        layout="wide"
    )
    
    # Header
    st.markdown("""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 2rem; text-align: center; border-radius: 10px; margin-bottom: 2rem;">
        <h1 style="color: white; margin: 0; font-size: 3rem;">🛒 Grocery Store</h1>
        <p style="color: white; margin: 0; font-size: 1.2rem;">Fresh groceries delivered to your doorstep</p>
    </div>
    """, unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["🔐 Login", "📝 Sign Up"])
    
    with tab1:
        login_page()
    
    with tab2:
        signup_page()

def user_dashboard():
    """User dashboard with products and cart"""
    st.title(f"🛒 Welcome, {st.session_state.username}!")
    
    # Sidebar
    st.sidebar.title("Navigation")
    if st.sidebar.button("Logout"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()
    
    products = load_products()
    
    menu = ["🏪 Browse Products", "🛒 Add to Cart", "👀 View Cart", "❌ Remove Item", "💳 Generate Bill", "📋 My Orders"]
    choice = st.sidebar.selectbox("Menu", menu)
    
    if choice == "🏪 Browse Products":
        st.subheader("Available Products")
        
        # Display products in a nice grid
        cols = st.columns(3)
        for idx, (item, data) in enumerate(products.items()):
            with cols[idx % 3]:
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, #e0f7fa, #ffffff);
 padding: 1rem; border-radius: 10px; text-align: center; margin-bottom: 1rem;">
                    <h3 style="color: #333;">{item.title()}</h3>
                    <p style="color: #666; font-size: 1.2rem;"><strong>Rs {data['price']}</strong> per {data['unit']}</p>
                </div>
                """, unsafe_allow_html=True)
    
    elif choice == "🛒 Add to Cart":
        st.subheader("Add to Cart")
        keyword = st.text_input("🔍 Search products", placeholder="Type product name...")
        
        if keyword:
            matches = {k: v for k, v in products.items() if keyword.lower() in k.lower()}
            if matches:
                item = st.selectbox("Select product", list(matches.keys()))
                qty = st.number_input(f"Quantity ({products[item]['unit']})", min_value=0.1, step=0.1)
                
                if st.button("Add to Cart", use_container_width=True):
                    if qty > 0:
                        if "cart" not in st.session_state:
                            st.session_state.cart = {}
                        
                        if item in st.session_state.cart:
                            st.session_state.cart[item] += qty
                        else:
                            st.session_state.cart[item] = qty
                        
                        st.success(f"✅ Added {qty} {products[item]['unit']} of {item.title()} to cart!")
                    else:
                        st.error("Quantity must be greater than zero!")
            else:
                st.warning("No matching products found.")
    
    elif choice == "👀 View Cart":
        st.subheader("Your Shopping Cart")
        
        if "cart" not in st.session_state or not st.session_state.cart:
            st.info("🛒 Your cart is empty!")
        else:
            total = 0
            for item, qty in st.session_state.cart.items():
                price = products[item]["price"] * qty
                total += price
                
                col1, col2, col3 = st.columns([2, 1, 1])
                with col1:
                    st.write(f"**{item.title()}**")
                with col2:
                    st.write(f"{qty} {products[item]['unit']}")
                with col3:
                    st.write(f"Rs {price:.2f}")
            
            st.markdown("---")
            st.markdown(f"**Subtotal: Rs {total:.2f}**")
    
    elif choice == "❌ Remove Item":
        st.subheader("Remove Items from Cart")
        
        if "cart" not in st.session_state or not st.session_state.cart:
            st.info("🛒 Your cart is empty!")
        else:
            item = st.selectbox("Select item to remove", list(st.session_state.cart.keys()))
            current_qty = st.session_state.cart[item]
            qty_to_remove = st.number_input(f"Quantity to remove (current: {current_qty})", 
                                          min_value=0.1, step=0.1)
            
            if st.button("Remove", use_container_width=True):
                if qty_to_remove > current_qty:
                    st.error(f"❌ Cannot remove {qty_to_remove} {products[item]['unit']}! Only {current_qty} {products[item]['unit']} available in cart.")
                elif qty_to_remove == current_qty:
                    del st.session_state.cart[item]
                    st.success(f"✅ {item.title()} removed from cart!")
                    st.rerun()
                else:
                    st.session_state.cart[item] -= qty_to_remove
                    st.success(f"✅ Removed {qty_to_remove} {products[item]['unit']} from {item.title()}!")
                    st.rerun()
    
    elif choice == "💳 Generate Bill":
        st.subheader("Generate Bill")
        
        if "cart" not in st.session_state or not st.session_state.cart:
            st.info("🛒 Your cart is empty!")
        else:
            cart = st.session_state.cart
            total = sum(products[item]["price"] * qty for item, qty in cart.items())
            
            # Calculate discount
            discount_rate = 0
            if total >= 2000:
                discount_rate = 0.15
            elif total >= 1000:
                discount_rate = 0.10
            
            discount_amount = total * discount_rate
            total_after_discount = total - discount_amount
            tax_amount = total_after_discount * TAX_RATE
            final_total = total_after_discount + tax_amount
            
            # Display bill
            st.markdown("### 🧾 Bill Summary")
            
            for item, qty in cart.items():
                price = products[item]["price"] * qty
                st.write(f"{item.title()} - {qty} {products[item]['unit']} × Rs {products[item]['price']} = Rs {price:.2f}")
            
            st.markdown("---")
            st.write(f"Subtotal: Rs {total:.2f}")
            if discount_rate > 0:
                st.write(f"Discount ({int(discount_rate*100)}%): -Rs {discount_amount:.2f}")
            st.write(f"Tax (5%): +Rs {tax_amount:.2f}")
            st.markdown(f"**Final Total: Rs {final_total:.2f}**")
            
            if st.button("🛒 Place Order", use_container_width=True):
                # Create order
                order_id = str(uuid.uuid4())[:8].upper()
                order = {
                    "order_id": order_id,
                    "user_email": st.session_state.user_email,
                    "username": st.session_state.username,
                    "cart": cart.copy(),
                    "subtotal": total,
                    "discount_amount": discount_amount,
                    "tax_amount": tax_amount,
                    "final_total": final_total,
                    "status": "pending",
                    "created_at": datetime.now().isoformat()
                }
                
                orders = load_orders()
                orders.append(order)
                
                if save_orders(orders):
                    # Send order confirmation email
                    order_email = create_order_email(st.session_state.username, order_id, final_total, "pending")
                    send_email(st.session_state.user_email, f"Order Confirmation - {order_id}", order_email)
                    
                    st.success(f"🎉 Order placed successfully! Order ID: {order_id}")
                    st.session_state.cart = {}
                    st.balloons()
                else:
                    st.error("Failed to place order. Please try again.")
    
    elif choice == "📋 My Orders":
        st.subheader("My Orders")
        
        orders = load_orders()
        user_orders = [order for order in orders if order.get("user_email") == st.session_state.user_email]
        
        if not user_orders:
            st.info("📦 No orders found!")
        else:
            for order in reversed(user_orders):  # Show latest first
                status_color = {"pending": "🟡", "shipped": "🔵", "delivered": "🟢", "cancelled": "🔴"}
                
                with st.expander(f"Order {order['order_id']} - {status_color.get(order['status'], '⚪')} {order['status'].title()}"):
                    st.write(f"**Date:** {order['created_at'][:19]}")
                    st.write(f"**Status:** {order['status'].title()}")
                    st.write(f"**Total:** Rs {order['final_total']:.2f}")
                    
                    st.write("**Items:**")
                    for item, qty in order['cart'].items():
                        st.write(f"- {item.title()}: {qty}")

def admin_dashboard():
    """Admin dashboard"""
    st.title(f"🔧 Admin Dashboard - Welcome, {st.session_state.username}!")
    
    # Sidebar
    st.sidebar.title("Admin Navigation")
    if st.sidebar.button("Logout"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()
    
    menu = ["📊 Overview", "👥 Manage Users", "🛍️ Manage Products", "📦 Manage Orders"]
    choice = st.sidebar.selectbox("Admin Menu", menu)
    
    if choice == "📊 Overview":
        st.subheader("Dashboard Overview")
        
        # Load data
        users = load_users()
        orders = load_orders()
        products = load_products()
        
        # Statistics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("👥 Total Users", len([u for u in users.values() if u['role'] == 'user']))
        
        with col2:
            st.metric("📦 Total Orders", len(orders))
        
        with col3:
            st.metric("🛍️ Products", len(products))
        
        with col4:
            total_revenue = sum(order['final_total'] for order in orders)
            st.metric("💰 Revenue", f"Rs {total_revenue:.2f}")
        
        # Recent orders
        st.subheader("Recent Orders")
        if orders:
            for order in orders[-5:]:  # Show last 5 orders
                status_color = {"pending": "🟡", "shipped": "🔵", "delivered": "🟢", "cancelled": "🔴"}
                st.write(f"{status_color.get(order['status'], '⚪')} {order['order_id']} - {order['username']} - Rs {order['final_total']:.2f}")
        else:
            st.info("No orders yet!")
    
    elif choice == "👥 Manage Users":
        st.subheader("User Management")
        
        users = load_users()
        user_list = [u for email, u in users.items() if u['role'] == 'user']
        
        if user_list:
            st.write(f"**Total Users: {len(user_list)}**")
            
            for email, user in users.items():
                if user['role'] == 'user':
                    with st.expander(f"👤 {user['username']} ({email})"):
                        st.write(f"**Email:** {email}")
                        st.write(f"**Joined:** {user.get('created_at', 'Unknown')[:10]}")
                        
                        # User orders
                        orders = load_orders()
                        user_orders = [o for o in orders if o.get('user_email') == email]
                        st.write(f"**Total Orders:** {len(user_orders)}")
                        
                        if user_orders:
                            total_spent = sum(o['final_total'] for o in user_orders)
                            st.write(f"**Total Spent:** Rs {total_spent:.2f}")
        else:
            st.info("No users registered yet!")
    
    elif choice == "🛍️ Manage Products":
        st.subheader("Product Management")
        
        tab1, tab2, tab3, tab4 = st.tabs(["➕ Add Product", "✏️ Update Product", "❌ Delete Product", "📋 View Products"])
        
        products = load_products()
        
        with tab1:
            st.write("**Add New Product**")
            with st.form("add_product"):
                name = st.text_input("Product Name").lower()
                price = st.number_input("Price (Rs)", min_value=0.0, step=0.01)
                unit = st.text_input("Unit (kg, litre, piece, etc.)").lower()
                
                if st.form_submit_button("Add Product"):
                    if name and price > 0 and unit:
                        if name in products:
                            st.error("Product already exists!")
                        else:
                            products[name] = {"price": price, "unit": unit}
                            if save_products(products):
                                st.success(f"✅ Product '{name.title()}' added successfully!")
                                st.rerun()
                            else:
                                st.error("Failed to add product!")
                    else:
                        st.error("Please fill all fields correctly!")
        
        with tab2:
            st.write("**Update Product**")
            if products:
                product_name = st.selectbox("Select Product", list(products.keys()))
                
                with st.form("update_product"):
                    new_price = st.number_input("New Price", value=float(products[product_name]["price"]), min_value=0.0, step=0.01)
                    new_unit = st.text_input("New Unit", value=products[product_name]["unit"])
                    
                    if st.form_submit_button("Update Product"):
                        if new_price > 0 and new_unit:
                            products[product_name] = {"price": new_price, "unit": new_unit.lower()}
                            if save_products(products):
                                st.success(f"✅ Product '{product_name.title()}' updated successfully!")
                                st.rerun()
                            else:
                                st.error("Failed to update product!")
                        else:
                            st.error("Please enter valid details!")
            else:
                st.info("No products available!")
        
        with tab3:
            st.write("**Delete Product**")
            if products:
                product_to_delete = st.selectbox("Select Product to Delete", list(products.keys()))
                
                if st.button("🗑️ Delete Product", use_container_width=True):
                    del products[product_to_delete]
                    if save_products(products):
                        st.success(f"✅ Product '{product_to_delete.title()}' deleted successfully!")
                        st.rerun()
                    else:
                        st.error("Failed to delete product!")
            else:
                st.info("No products available!")
        
        with tab4:
            st.write("**All Products**")
            if products:
                for item, data in products.items():
                    st.write(f"**{item.title()}** - Rs {data['price']} per {data['unit']}")
            else:
                st.info("No products available!")
    
    elif choice == "📦 Manage Orders":
        st.subheader("Order Management")
        
        orders = load_orders()
        
        if not orders:
            st.info("No orders yet!")
        else:
            st.write(f"**Total Orders: {len(orders)}**")
            
            # Filter by status
            status_filter = st.selectbox("Filter by Status", ["All", "pending", "shipped", "delivered", "cancelled"])
            
            filtered_orders = orders if status_filter == "All" else [o for o in orders if o['status'] == status_filter]
            
            for idx, order in enumerate(reversed(filtered_orders)):  # Show latest first
                status_colors = {"pending": "🟡", "shipped": "🔵", "delivered": "🟢", "cancelled": "🔴"}
                
                with st.expander(f"{status_colors.get(order['status'], '⚪')} Order {order['order_id']} - {order['username']}"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write(f"**Order ID:** {order['order_id']}")
                        st.write(f"**Customer:** {order['username']}")
                        st.write(f"**Email:** {order['user_email']}")
                        st.write(f"**Date:** {order['created_at'][:19]}")
                        st.write(f"**Total:** Rs {order['final_total']:.2f}")
                    
                    with col2:
                        st.write("**Items Ordered:**")
                        for item, qty in order['cart'].items():
                            st.write(f"- {item.title()}: {qty}")
                    
                    # Status update
                    current_status = order['status']
                    new_status = st.selectbox(f"Update Status for {order['order_id']}", 
                                            ["pending", "shipped", "delivered", "cancelled"], 
                                            index=["pending", "shipped", "delivered", "cancelled"].index(current_status),
                                            key=f"status_{order['order_id']}")
                    
                    if new_status != current_status:
                        if st.button(f"Update Status to {new_status.title()}", key=f"update_{order['order_id']}"):
                            # Update order status
                            for i, o in enumerate(orders):
                                if o['order_id'] == order['order_id']:
                                    orders[i]['status'] = new_status
                                    break
                            
                            if save_orders(orders):
                                # Send status update email
                                status_email = create_order_email(order['username'], order['order_id'], order['final_total'], new_status)
                                send_email(order['user_email'], f"Order Status Update - {order['order_id']}", status_email)
                                
                                st.success(f"✅ Order status updated to {new_status.title()}! Email sent to customer.")
                                st.rerun()
                            else:
                                st.error("Failed to update order status!")

def main():
    """Main function"""
    # Initialize session state
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    
    # Check if user is logged in
    if not st.session_state.logged_in:
        auth_page()
    else:
        # Check user role and show appropriate dashboard
        if st.session_state.user_role == "admin":
            admin_dashboard()
        else:
            user_dashboard()

if __name__ == "__main__":
    main()