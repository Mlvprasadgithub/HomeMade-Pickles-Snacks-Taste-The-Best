from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import json
import os
from datetime import datetime
import uuid

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-in-production'

# In-memory database simulation (replace with DynamoDB in production)
users_db = {}
products_db = {
    'mango-pickle': {
        'id': 'mango-pickle',
        'name': 'Traditional Mango Pickle',
        'category': 'veg_pickles',
        'price': 299,
        'image': '/static/images/mango-pickle.jpg',
        'description': 'Authentic homemade mango pickle with traditional spices',
        'stock': 50,
        'ingredients': ['Raw Mango', 'Mustard Oil', 'Red Chili', 'Turmeric', 'Fenugreek'],
        'rating': 4.8
    },
    'lemon-pickle': {
        'id': 'lemon-pickle',
        'name': 'Tangy Lemon Pickle',
        'category': 'veg_pickles',
        'price': 249,
        'image': '/static/images/lemon-pickle.jpg',
        'description': 'Fresh lemon pickle bursting with citrus flavors',
        'stock': 35,
        'ingredients': ['Fresh Lemon', 'Salt', 'Turmeric', 'Red Chili', 'Mustard Seeds'],
        'rating': 4.6
    },
    'chicken-pickle': {
        'id': 'chicken-pickle',
        'name': 'Spicy Chicken Pickle',
        'category': 'non_veg_pickles',
        'price': 399,
        'image': '/static/images/chicken-pickle.jpg',
        'description': 'Tender chicken pieces in aromatic spice blend',
        'stock': 25,
        'ingredients': ['Chicken', 'Ginger-Garlic', 'Red Chili', 'Garam Masala', 'Mustard Oil'],
        'rating': 4.9
    },
    'banana-chips': {
        'id': 'banana-chips',
        'name': 'Crispy Banana Chips',
        'category': 'snacks',
        'price': 199,
        'image': '/static/images/banana-chips.jpg',
        'description': 'Perfectly crispy banana chips made from fresh bananas',
        'stock': 60,
        'ingredients': ['Raw Banana', 'Coconut Oil', 'Salt', 'Turmeric'],
        'rating': 4.5
    },
    'murukku': {
        'id': 'murukku',
        'name': 'Traditional Murukku',
        'category': 'snacks',
        'price': 179,
        'image': '/static/images/murukku.jpg',
        'description': 'Crunchy spiral-shaped traditional snack',
        'stock': 40,
        'ingredients': ['Rice Flour', 'Urad Dal', 'Sesame Seeds', 'Cumin', 'Asafoetida'],
        'rating': 4.7
    }
}
orders_db = {}
cart_db = {}

@app.route('/')
def home():
    featured_products = list(products_db.values())[:3]
    return render_template('index.html', featured_products=featured_products)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/products')
def products():
    category = request.args.get('category', 'all')
    if category == 'all':
        filtered_products = list(products_db.values())
    else:
        filtered_products = [p for p in products_db.values() if p['category'] == category]
    return render_template('products.html', products=filtered_products, category=category)

@app.route('/veg-pickles')
def veg_pickles():
    veg_products = [p for p in products_db.values() if p['category'] == 'veg_pickles']
    return render_template('veg_pickles.html', products=veg_products)

@app.route('/non-veg-pickles')
def non_veg_pickles():
    non_veg_products = [p for p in products_db.values() if p['category'] == 'non_veg_pickles']
    return render_template('non_veg_pickles.html', products=non_veg_products)

@app.route('/snacks')
def snacks():
    snack_products = [p for p in products_db.values() if p['category'] == 'snacks']
    return render_template('snacks.html', products=snack_products)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        if email in users_db and users_db[email]['password'] == password:
            session['user_id'] = email
            session['user_name'] = users_db[email]['name']
            flash('Login successful!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Invalid email or password!', 'error')
    
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        phone = request.form['phone']
        
        if email in users_db:
            flash('Email already exists!', 'error')
        else:
            users_db[email] = {
                'name': name,
                'email': email,
                'password': password,
                'phone': phone,
                'created_at': datetime.now().isoformat()
            }
            session['user_id'] = email
            session['user_name'] = name
            flash('Account created successfully!', 'success')
            return redirect(url_for('home'))
    
    return render_template('signup.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully!', 'success')
    return redirect(url_for('home'))

@app.route('/add-to-cart', methods=['POST'])
def add_to_cart():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Please login first'})
    
    product_id = request.json.get('product_id')
    quantity = int(request.json.get('quantity', 1))
    user_id = session['user_id']
    
    if user_id not in cart_db:
        cart_db[user_id] = {}
    
    if product_id in cart_db[user_id]:
        cart_db[user_id][product_id] += quantity
    else:
        cart_db[user_id][product_id] = quantity
    
    return jsonify({'success': True, 'message': 'Product added to cart'})

@app.route('/cart')
def cart():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    cart_items = []
    total = 0
    
    if user_id in cart_db:
        for product_id, quantity in cart_db[user_id].items():
            if product_id in products_db:
                product = products_db[product_id].copy()
                product['quantity'] = quantity
                product['subtotal'] = product['price'] * quantity
                cart_items.append(product)
                total += product['subtotal']
    
    return render_template('cart.html', cart_items=cart_items, total=total)

@app.route('/update-cart', methods=['POST'])
def update_cart():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Please login first'})
    
    product_id = request.json.get('product_id')
    quantity = int(request.json.get('quantity'))
    user_id = session['user_id']
    
    if user_id in cart_db and product_id in cart_db[user_id]:
        if quantity <= 0:
            del cart_db[user_id][product_id]
        else:
            cart_db[user_id][product_id] = quantity
    
    return jsonify({'success': True})

@app.route('/checkout')
def checkout():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    cart_items = []
    total = 0
    
    if user_id in cart_db:
        for product_id, quantity in cart_db[user_id].items():
            if product_id in products_db:
                product = products_db[product_id].copy()
                product['quantity'] = quantity
                product['subtotal'] = product['price'] * quantity
                cart_items.append(product)
                total += product['subtotal']
    
    return render_template('checkout.html', cart_items=cart_items, total=total)

@app.route('/place-order', methods=['POST'])
def place_order():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    order_id = str(uuid.uuid4())
    
    # Get cart items
    cart_items = []
    total = 0
    
    if user_id in cart_db:
        for product_id, quantity in cart_db[user_id].items():
            if product_id in products_db:
                product = products_db[product_id].copy()
                product['quantity'] = quantity
                product['subtotal'] = product['price'] * quantity
                cart_items.append(product)
                total += product['subtotal']
                
                # Update stock
                products_db[product_id]['stock'] -= quantity
    
    # Create order
    orders_db[order_id] = {
        'order_id': order_id,
        'user_id': user_id,
        'items': cart_items,
        'total': total,
        'status': 'confirmed',
        'created_at': datetime.now().isoformat(),
        'shipping_address': {
            'name': request.form['name'],
            'address': request.form['address'],
            'city': request.form['city'],
            'pincode': request.form['pincode'],
            'phone': request.form['phone']
        }
    }
    
    # Clear cart
    if user_id in cart_db:
        cart_db[user_id] = {}
    
    return redirect(url_for('order_success', order_id=order_id))

@app.route('/order-success/<order_id>')
def order_success(order_id):
    if order_id in orders_db:
        order = orders_db[order_id]
        return render_template('success.html', order=order)
    else:
        return redirect(url_for('home'))

@app.route('/contact')
def contact():
    return render_template('contact_us.html')

@app.route('/api/products')
def api_products():
    return jsonify(list(products_db.values()))

@app.route('/api/cart-count')
def api_cart_count():
    if 'user_id' not in session:
        return jsonify({'count': 0})
    
    user_id = session['user_id']
    count = 0
    if user_id in cart_db:
        count = sum(cart_db[user_id].values())
    
    return jsonify({'count': count})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)