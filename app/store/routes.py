from flask import render_template, request, redirect, url_for, flash, session, jsonify, jsonify
from flask_login import login_required, current_user
from app.store import bp
from app.models import Product, Transaction, StoreOrder, StoreOrderItem
from app import db
try:
    from app.payment import create_payment_order, process_payment
except ImportError:
    def create_payment_order(amount):
        return {'id': 'test_order', 'amount': amount}
    def process_payment(user_id, cart_items, payment_data):
        return True, 'Payment processed'
try:
    from app.search import ProductSearch
    from app.ecommerce import RecommendationEngine
except ImportError:
    class ProductSearch:
        def __init__(self, query=None):
            from app.models import Product
            self.base_query = query or Product.query
        def filter_in_stock(self):
            return self
        def search(self, term):
            return self
        def filter_price(self, min_price, max_price):
            return self
        def filter_designer(self, designer_id):
            return self
        def filter_featured(self, featured):
            return self
        def sort_by(self, sort_type):
            return self
        def paginate(self, page, per_page):
            return self.base_query.paginate(page=page, per_page=per_page, error_out=False)
    
    class RecommendationEngine:
        @staticmethod
        def get_trending_products(limit=4):
            from app.models import Product
            return Product.query.filter(Product.stock > 0).limit(limit).all()
from sqlalchemy import or_

@bp.route('/')
def index():
    print("Store index route accessed")
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    sort_by = request.args.get('sort', 'newest')
    min_price = request.args.get('min_price', type=float)
    max_price = request.args.get('max_price', type=float)
    designer_id = request.args.get('designer', type=int)
    featured_only = request.args.get('featured', type=bool)
    
    # Use advanced search
    search_engine = ProductSearch()
    search_engine.filter_in_stock()
    
    if search:
        search_engine.search(search)
    if min_price or max_price:
        search_engine.filter_price(min_price, max_price)
    if designer_id:
        search_engine.filter_designer(designer_id)
    if featured_only:
        search_engine.filter_featured(True)
    
    search_engine.sort_by(sort_by)
    products = search_engine.paginate(page, 12)
    
    # Get trending products for sidebar
    trending = RecommendationEngine.get_trending_products(4)
    
    return render_template('store/index.html', 
                         products=products, 
                         search=search, 
                         sort_by=sort_by,
                         trending=trending)

@bp.route('/<slug>')
def product_detail(slug):
    product = Product.query.filter_by(slug=slug).first_or_404()
    related_products = Product.query.filter(
        Product.id != product.id,
        Product.stock > 0
    ).limit(4).all()
    
    return render_template('store/product_detail.html', 
                         product=product, 
                         related_products=related_products)

@bp.route('/add-to-cart/<int:product_id>')
@login_required
def add_to_cart(product_id):
    print(f"Add to cart route accessed for product {product_id}")
    product = Product.query.get_or_404(product_id)
    
    if product.stock <= 0:
        flash('Sorry, this item is out of stock.', 'error')
        return redirect(url_for('store.product_detail', slug=product.slug))
    
    # Initialize cart in session if not exists
    if 'cart' not in session:
        session['cart'] = {}
    
    cart = session['cart']
    product_id_str = str(product_id)
    
    if product_id_str in cart:
        cart[product_id_str] += 1
    else:
        cart[product_id_str] = 1
    
    session['cart'] = cart
    flash(f'{product.title} added to cart!', 'success')
    
    return redirect(url_for('store.product_detail', slug=product.slug))

@bp.route('/cart')
@login_required
def cart():
    cart_items = []
    total = 0
    
    if 'cart' in session:
        for product_id, quantity in session['cart'].items():
            product = Product.query.get(int(product_id))
            if product:
                item_total = float(product.price) * quantity
                cart_items.append({
                    'product': product,
                    'quantity': quantity,
                    'total': item_total
                })
                total += item_total
    
    return render_template('store/cart.html', cart_items=cart_items, total=total)

@bp.route('/remove-from-cart/<int:product_id>')
@login_required
def remove_from_cart(product_id):
    if 'cart' in session:
        cart = session['cart']
        product_id_str = str(product_id)
        if product_id_str in cart:
            del cart[product_id_str]
            session['cart'] = cart
            flash('Item removed from cart.', 'info')
    
    return redirect(url_for('store.cart'))

@bp.route('/checkout')
@login_required
def checkout():
    if 'cart' not in session or not session['cart']:
        flash('Your cart is empty.', 'info')
        return redirect(url_for('store.index'))
    
    cart_items = []
    total = 0
    
    for product_id, quantity in session['cart'].items():
        product = Product.query.get(int(product_id))
        if product:
            item_total = float(product.price) * quantity
            cart_items.append({
                'product': product,
                'quantity': quantity,
                'total': item_total
            })
            total += item_total
    
    # Create Razorpay order
    payment_order = create_payment_order(total)
    
    return render_template('store/checkout.html', 
                         cart_items=cart_items, 
                         total=total,
                         payment_order=payment_order)

@bp.route('/process-checkout', methods=['POST'])
@login_required
def process_checkout():
    # Validate CSRF token
    from flask_wtf.csrf import validate_csrf
    try:
        validate_csrf(request.form.get('csrf_token'))
    except:
        flash('Security token expired. Please try again.', 'error')
        return redirect(url_for('store.checkout'))
    
    if 'cart' not in session or not session['cart']:
        flash('Your cart is empty.', 'error')
        return redirect(url_for('store.index'))
    
    try:
        # Calculate total
        total_amount = 0
        cart_items = []
        
        for product_id, quantity in session['cart'].items():
            product = Product.query.get(int(product_id))
            if product and product.stock >= quantity:
                item_total = float(product.price) * quantity
                total_amount += item_total
                cart_items.append({
                    'product': product,
                    'quantity': quantity,
                    'price': product.price
                })
        
        # Generate order number
        import random
        order_number = f"ST{random.randint(100000, 999999)}"
        
        # Create store order
        store_order = StoreOrder(
            user_id=current_user.id,
            order_number=order_number,
            total_amount=total_amount,
            status='confirmed',
            shipping_address=f"{current_user.name}\n{current_user.email}",
            payment_method='online'
        )
        db.session.add(store_order)
        db.session.flush()  # Get order ID
        
        # Create order items and update stock
        for item in cart_items:
            order_item = StoreOrderItem(
                order_id=store_order.id,
                product_id=item['product'].id,
                quantity=item['quantity'],
                price=item['price']
            )
            db.session.add(order_item)
            
            # Update stock
            item['product'].stock -= item['quantity']
            
            # Award points (1 point per ₹10 spent)
            points_earned = int(float(item['price'] * item['quantity']) / 10)
            current_user.points += points_earned
        
        db.session.commit()
        
        # Clear cart
        session.pop('cart', None)
        
        flash(f'Order #{order_number} placed successfully!', 'success')
        return redirect(url_for('store.order_confirmation', order_number=order_number))
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Checkout error: {e}")
        flash('Error processing order. Please try again.', 'error')
        return redirect(url_for('store.checkout'))

@bp.route('/payment/verify', methods=['POST'])
@login_required
def verify_payment():
    # Validate CSRF token
    from flask_wtf.csrf import validate_csrf
    try:
        validate_csrf(request.form.get('csrf_token'))
    except:
        return jsonify({'success': False, 'message': 'Security token expired'})
    
    payment_data = {
        'payment_id': request.form.get('razorpay_payment_id'),
        'order_id': request.form.get('razorpay_order_id'),
        'signature': request.form.get('razorpay_signature')
    }
    
    if 'cart' not in session or not session['cart']:
        return jsonify({'success': False, 'message': 'Cart is empty'})
    
    # Get cart items
    cart_items = []
    for product_id, quantity in session['cart'].items():
        product = Product.query.get(int(product_id))
        if product:
            cart_items.append({
                'product': product,
                'quantity': quantity,
                'total': float(product.price) * quantity
            })
    
    # Process payment
    success, message = process_payment(current_user.id, cart_items, payment_data)
    
    if success:
        session.pop('cart', None)
        return jsonify({'success': True, 'redirect': url_for('main.dashboard')})
    else:
        return jsonify({'success': False, 'message': message})

@bp.route('/order-confirmation/<order_number>')
@login_required
def order_confirmation(order_number):
    order = StoreOrder.query.filter_by(order_number=order_number, user_id=current_user.id).first_or_404()
    return render_template('store/order_confirmation.html', order=order)

@bp.route('/track-order/<order_number>')
def track_order(order_number):
    order = StoreOrder.query.filter_by(order_number=order_number).first_or_404()
    
    # Status timeline
    status_timeline = [
        {'status': 'confirmed', 'label': 'Order Confirmed', 'completed': True},
        {'status': 'shipped', 'label': 'Shipped', 'completed': order.status in ['shipped', 'delivered']},
        {'status': 'delivered', 'label': 'Delivered', 'completed': order.status == 'delivered'}
    ]
    
    return render_template('store/track_order.html', order=order, status_timeline=status_timeline)

@bp.route('/my-orders')
@login_required
def my_orders():
    page = request.args.get('page', 1, type=int)
    orders = StoreOrder.query.filter_by(user_id=current_user.id).order_by(StoreOrder.created_at.desc()).paginate(
        page=page, per_page=10, error_out=False
    )
    return render_template('store/my_orders.html', orders=orders)