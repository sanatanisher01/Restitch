from flask import Blueprint, request, jsonify, current_app
from flask_login import login_required, current_user
from app.models import User, Product, Order, Transaction
from app.security import rate_limit
from app import db
import jwt
from datetime import datetime, timedelta
from functools import wraps

mobile_api = Blueprint('mobile_api', __name__)

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'error': 'Token missing'}), 401
        
        try:
            token = token.split(' ')[1]  # Remove 'Bearer '
            data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user_id = data['user_id']
            current_user = User.query.get(current_user_id)
        except:
            return jsonify({'error': 'Invalid token'}), 401
        
        return f(current_user, *args, **kwargs)
    return decorated

@mobile_api.route('/auth/login', methods=['POST'])
@rate_limit(limit=5, window=300)
def mobile_login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    
    user = User.query.filter_by(email=email).first()
    
    if user and user.check_password(password):
        token = jwt.encode({
            'user_id': user.id,
            'exp': datetime.utcnow() + timedelta(days=30)
        }, current_app.config['SECRET_KEY'])
        
        return jsonify({
            'token': token,
            'user': {
                'id': user.id,
                'name': user.name,
                'email': user.email,
                'points': user.points
            }
        })
    
    return jsonify({'error': 'Invalid credentials'}), 401

@mobile_api.route('/products', methods=['GET'])
@rate_limit(limit=100, window=60)
def get_products():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    
    query = Product.query.filter(Product.stock > 0)
    
    if search:
        query = query.filter(Product.title.contains(search))
    
    products = query.paginate(page=page, per_page=20, error_out=False)
    
    return jsonify({
        'products': [{
            'id': p.id,
            'title': p.title,
            'price': float(p.price),
            'stock': p.stock,
            'is_featured': p.is_featured,
            'tags': p.get_tags()
        } for p in products.items],
        'pagination': {
            'page': products.page,
            'pages': products.pages,
            'total': products.total
        }
    })

@mobile_api.route('/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    product = Product.query.get_or_404(product_id)
    
    return jsonify({
        'id': product.id,
        'title': product.title,
        'description': product.description,
        'price': float(product.price),
        'stock': product.stock,
        'tags': product.get_tags(),
        'designer': product.designer.name if product.designer else None
    })

@mobile_api.route('/orders', methods=['GET'])
@token_required
def get_user_orders(current_user):
    orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.created_at.desc()).all()
    
    return jsonify({
        'orders': [{
            'id': order.id,
            'status': order.status,
            'barcode': order.barcode,
            'created_at': order.created_at.isoformat(),
            'estimated_days': order.estimated_days
        } for order in orders]
    })

@mobile_api.route('/orders/<barcode>/track', methods=['GET'])
def track_order_mobile(barcode):
    order = Order.query.filter_by(barcode=barcode).first_or_404()
    
    return jsonify({
        'barcode': order.barcode,
        'status': order.status,
        'created_at': order.created_at.isoformat(),
        'updated_at': order.updated_at.isoformat(),
        'estimated_days': order.estimated_days,
        'notes': order.notes
    })

@mobile_api.route('/user/profile', methods=['GET'])
@token_required
def get_profile(current_user):
    return jsonify({
        'id': current_user.id,
        'name': current_user.name,
        'email': current_user.email,
        'phone': current_user.phone,
        'points': current_user.points,
        'member_since': current_user.created_at.isoformat()
    })

@mobile_api.route('/user/profile', methods=['PUT'])
@token_required
def update_profile(current_user):
    data = request.get_json()
    
    if 'name' in data:
        current_user.name = data['name']
    if 'phone' in data:
        current_user.phone = data['phone']
    
    db.session.commit()
    
    return jsonify({'message': 'Profile updated successfully'})

@mobile_api.route('/cart/add', methods=['POST'])
@token_required
def add_to_cart_mobile(current_user):
    data = request.get_json()
    product_id = data.get('product_id')
    quantity = data.get('quantity', 1)
    
    product = Product.query.get_or_404(product_id)
    
    if product.stock < quantity:
        return jsonify({'error': 'Insufficient stock'}), 400
    
    # In a real app, you'd store cart in database or Redis
    return jsonify({'message': 'Added to cart successfully'})

# Register blueprint
def register_mobile_api(app):
    app.register_blueprint(mobile_api, url_prefix='/api/mobile')