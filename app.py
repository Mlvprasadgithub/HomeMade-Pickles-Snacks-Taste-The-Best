from flask import Flask, request, session, redirect, url_for, render_template, flash, jsonify
import boto3
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import uuid
import os
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# ---------------------------------------
# Flask App Initialization
# ---------------------------------------
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'ecommerce_secret_key')

# ---------------------------------------
# AWS Configuration
# ---------------------------------------
AWS_REGION = os.environ.get('AWS_REGION_NAME', 'us-east-1')
PRODUCTS_TABLE = os.environ.get('PRODUCTS_TABLE_NAME', 'EcomProducts')
USERS_TABLE = os.environ.get('USERS_TABLE_NAME', 'EcomUsers')
ORDERS_TABLE = os.environ.get('ORDERS_TABLE_NAME', 'EcomOrders')
SNS_TOPIC_ARN = os.environ.get('SNS_TOPIC_ARN')
ENABLE_SNS = os.environ.get('ENABLE_SNS', 'False').lower() == 'true'

# Email Configuration
SENDER_EMAIL = mandalalakshmivaraprasad@gmail.com
SENDER_PASSWORD = hzwwppbkljjwdazd
SMTP_SERVER = smtp.gmail.com
SMTP_PORT = 587
ENABLE_EMAIL = True

# ---------------------------------------
# AWS Resources
# ---------------------------------------
dynamodb = boto3.resource('dynamodb', region_name=AWS_REGION)
sns = boto3.client('sns', region_name=AWS_REGION)

products_table = dynamodb.Table(PRODUCTS_TABLE)
users_table = dynamodb.Table(USERS_TABLE)
orders_table = dynamodb.Table(ORDERS_TABLE)

# ---------------------------------------
# Logging Setup
# ---------------------------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ---------------------------------------
# In-memory Cart
# ---------------------------------------
cart_db = {}

# ---------------------------------------
# Helper Functions
# ---------------------------------------
def is_logged_in():
    return 'email' in session

def send_email(to_email, subject, body):
    if not ENABLE_EMAIL:
        logger.info(f"[Email Skipped] {subject}")
        return
    try:
        msg = MIMEMultipart()
        msg['From'] = SENDER_EMAIL
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, to_email, msg.as_string())
        server.quit()
        logger.info(f"Email sent to {to_email}")
    except Exception as e:
        logger.error(f"Failed to send email: {e}")

def send_sns_notification(message, subject="Order Notification"):
    if ENABLE_SNS:
        try:
            sns.publish(
                TopicArn=SNS_TOPIC_ARN,
                Message=message,
                Subject=subject
            )
            logger.info("SNS message sent")
        except Exception as e:
            logger.error(f"SNS error: {e}")

# ---------------------------------------
# Routes
# ---------------------------------------
@app.route('/')
def home():
    try:
        response = products_table.scan(Limit=3)
        products = response.get('Items', [])
    except Exception as e:
        logger.error(f"Failed to load products: {e}")
        products = []
    return render_template('index.html', featured_products=products)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        name = request.form['name']
        password = generate_password_hash(request.form['password'])

        try:
            existing = users_table.get_item(Key={'email': email})
            if 'Item' in existing:
                flash("Email already registered.", "danger")
                return redirect(url_for('signup'))

            users_table.put_item(Item={
                'email': email,
                'name': name,
                'password': password,
                'created_at': datetime.utcnow().isoformat()
            })

            session['email'] = email
            session['name'] = name

            subject = "Welcome to Our Pickle & Snacks Store!"
            body = f"Hello {name},\n\nThank you for signing up! Enjoy shopping your favorite pickles and snacks.\n\nTeam PickleMart"
            send_email(email, subject, body)

            flash("Account created!", "success")
            return redirect(url_for('home'))
        except Exception as e:
            logger.error(f"Signup error: {e}")
            flash("Error creating account.", "danger")

    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        try:
            result = users_table.get_item(Key={'email': email})
            user = result.get('Item')

            if user and check_password_hash(user['password'], password):
                session['email'] = email
                session['name'] = user['name']
                flash("Logged in successfully!", "success")
                return redirect(url_for('home'))
            else:
                flash("Invalid credentials.", "danger")
        except Exception as e:
            logger.error(f"Login error: {e}")
            flash("Login failed.", "danger")

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash("Logged out.", "info")
    return redirect(url_for('home'))

@app.route('/products')
def products():
    category = request.args.get('category')
    try:
        if category:
            response = products_table.scan(
                FilterExpression="category = :c",
                ExpressionAttributeValues={":c": category}
            )
        else:
            response = products_table.scan()
        products = response.get('Items', [])
    except Exception as e:
        logger.error(f"Product load error: {e}")
        products = []
    return render_template('products.html', products=products)

@app.route('/add-to-cart', methods=['POST'])
def add_to_cart():
    if not is_logged_in():
        return jsonify({'success': False, 'message': 'Login required'})

    email = session['email']
    product_id = request.json.get('product_id')
    quantity = int(request.json.get('quantity', 1))

    if email not in cart_db:
        cart_db[email] = {}

    cart_db[email][product_id] = cart_db[email].get(product_id, 0) + quantity
    return jsonify({'success': True, 'message': 'Added to cart'})

@app.route('/update-cart', methods=['POST'])
def update_cart():
    if not is_logged_in():
        return jsonify({'success': False, 'message': 'Login required'})

    email = session['email']
    product_id = request.json.get('product_id')
    quantity = int(request.json.get('quantity', 1))

    try:
        if email not in cart_db:
            cart_db[email] = {}

        if quantity > 0:
            cart_db[email][product_id] = quantity
            return jsonify({'success': True, 'message': 'Cart updated'})
        else:
            # Remove item if quantity is 0 or less
            if product_id in cart_db[email]:
                del cart_db[email][product_id]
            return jsonify({'success': True, 'message': 'Item removed from cart'})
    except Exception as e:
        logger.error(f"Update cart error: {e}")
        return jsonify({'success': False, 'message': 'Error updating cart'})

@app.route('/remove-from-cart', methods=['POST'])
def remove_from_cart():
    if not is_logged_in():
        return jsonify({'success': False, 'message': 'Login required'})

    email = session['email']
    product_id = request.json.get('product_id')

    try:
        if email in cart_db and product_id in cart_db[email]:
            del cart_db[email][product_id]
            return jsonify({'success': True, 'message': 'Item removed from cart'})
        else:
            return jsonify({'success': False, 'message': 'Item not found in cart'})
    except Exception as e:
        logger.error(f"Remove from cart error: {e}")
        return jsonify({'success': False, 'message': 'Error removing item'})
    
@app.route('/cart')
def cart():
    if not is_logged_in():
        return redirect(url_for('login'))

    email = session['email']
    cart_items = []
    total = 0

    try:
        for pid, qty in cart_db.get(email, {}).items():
            product = products_table.get_item(Key={'id': pid}).get('Item')
            if product:
                product['quantity'] = qty
                product['subtotal'] = product['price'] * qty
                cart_items.append(product)
                total += product['subtotal']
    except Exception as e:
        logger.error(f"Cart error: {e}")

    return render_template('cart.html', cart_items=cart_items, total=total)

@app.route('/veg-pickles')
def veg_pickles():
    try:
        response = products_table.scan(
            FilterExpression="category = :cat",
            ExpressionAttributeValues={":cat": "veg"}
        )
        items = response.get('Items', [])
    except Exception as e:
        logger.error(f"Veg pickles load error: {e}")
        items = []
    return render_template('category.html', title="Vegetarian Pickles", products=items)

@app.route('/non-veg-pickles')
def non_veg_pickles():
    try:
        response = products_table.scan(
            FilterExpression="category = :cat",
            ExpressionAttributeValues={":cat": "non-veg"}
        )
        items = response.get('Items', [])
    except Exception as e:
        logger.error(f"Non-veg pickles load error: {e}")
        items = []
    return render_template('category.html', title="Non-Veg Pickles", products=items)

@app.route('/snacks')
def snacks():
    try:
        response = products_table.scan(
            FilterExpression="category = :cat",
            ExpressionAttributeValues={":cat": "snacks"}
        )
        items = response.get('Items', [])
    except Exception as e:
        logger.error(f"Snacks load error: {e}")
        items = []
    return render_template('category.html', title="Traditional Snacks", products=items)

@app.route('/checkout', methods=['POST'])
def checkout():
    if not is_logged_in():
        return redirect(url_for('login'))

    email = session['email']
    cart = cart_db.get(email, {})
    order_id = str(uuid.uuid4())
    total = 0
    order_items = []

    try:
        for pid, qty in cart.items():
            product = products_table.get_item(Key={'id': pid}).get('Item')
            if product:
                subtotal = product['price'] * qty
                total += subtotal
                order_items.append({
                    'id': pid,
                    'name': product['name'],
                    'price': product['price'],
                    'quantity': qty,
                    'subtotal': subtotal
                })

        orders_table.put_item(Item={
            'order_id': order_id,
            'user_email': email,
            'items': order_items,
            'total': total,
            'created_at': datetime.utcnow().isoformat()
        })

        subject = f"Your Order Confirmation - {order_id}"
        item_list = "\n".join([f"{item['name']} x {item['quantity']} = ₹{item['subtotal']}" for item in order_items])
        body = f"Hello {session['name']},\n\nThank you for your order!\n\nOrder ID: {order_id}\n\nItems:\n{item_list}\n\nTotal: ₹{total}\n\nWe will ship your order shortly.\n\nTeam PickleMart"
        send_email(email, subject, body)

        send_sns_notification(f"New order placed by {email}: Order ID {order_id}")

        cart_db[email] = {}
        flash("Order placed successfully!", "success")
        return redirect(url_for('home'))

    except Exception as e:
        logger.error(f"Checkout error: {e}")
        flash("Checkout failed.", "danger")
        return redirect(url_for('cart'))

@app.route('/api/cart-count')
def api_cart_count():
    if not is_logged_in():
        return jsonify({'count': 0})

    email = session['email']
    count = sum(cart_db.get(email, {}).values())
    return jsonify({'count': count})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
