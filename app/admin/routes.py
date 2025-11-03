from flask import render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from functools import wraps
from app.admin import bp
from app.models import User, PickupRequest, Order, Product, ActivityLog, DesignerApplication
from app.admin.forms import OrderUpdateForm, ProductForm
try:
    from app.analytics import Analytics
except ImportError:
    class Analytics:
        @staticmethod
        def get_dashboard_stats():
            return {'total_users': 0, 'total_orders': 0, 'total_revenue': 0, 'total_products': 0, 'new_users_30d': 0, 'new_orders_30d': 0, 'avg_order_value': 0}
        @staticmethod
        def get_inventory_report():
            return {'low_stock_products': [], 'out_of_stock_products': [], 'total_inventory_value': 0}
        @staticmethod
        def get_popular_products(limit=5):
            return []
        @staticmethod
        def get_sales_by_month():
            return []
        @staticmethod
        def get_user_analytics():
            return {'user_growth': [], 'top_customers': []}
from app import db
import qrcode
import io
import base64
from datetime import datetime
import os

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin():
            flash('Access denied. Admin privileges required.', 'error')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

@bp.route('/')
@login_required
@admin_required
def dashboard():
    # Get real data from database
    stats = {
        'users': User.query.count(),
        'pickups': PickupRequest.query.count(),
        'orders': Order.query.count(),
        'products': Product.query.count()
    }
    
    # Recent activity
    recent_pickups = PickupRequest.query.order_by(PickupRequest.created_at.desc()).limit(5).all()
    recent_orders = Order.query.order_by(Order.created_at.desc()).limit(5).all()
    
    return render_template('admin/dashboard.html', 
                         stats=stats,
                         recent_pickups=recent_pickups, 
                         recent_orders=recent_orders)

@bp.route('/orders')
@login_required
@admin_required
def orders():
    page = request.args.get('page', 1, type=int)
    status_filter = request.args.get('status', '')
    
    query = Order.query
    if status_filter:
        query = query.filter_by(status=status_filter)
    
    orders = query.order_by(Order.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    
    return render_template('admin/orders.html', orders=orders, status_filter=status_filter)

@bp.route('/orders/<int:order_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def order_detail(order_id):
    order = Order.query.get_or_404(order_id)
    form = OrderUpdateForm(obj=order)
    
    # Populate designer choices
    designers = User.query.filter_by(role='designer').all()
    form.designer_id.choices = [(0, 'Select Designer')] + [(d.id, d.name) for d in designers]
    
    if form.validate_on_submit():
        old_status = order.status
        
        # Update order fields
        order.status = form.status.data
        order.designer_id = form.designer_id.data if form.designer_id.data != 0 else None
        order.fabric_type = form.fabric_type.data
        order.notes = form.notes.data
        order.estimated_days = form.estimated_days.data
        order.points_awarded = form.points_awarded.data
        
        # Generate barcode if status changed to 'approved' or 'shipped'
        if old_status != 'approved' and order.status == 'approved' and not order.barcode:
            order.barcode = f"RS{order.id:06d}"
        
        # Award points to user if points changed
        if form.points_awarded.data > 0:
            points_diff = form.points_awarded.data - (order.points_awarded or 0)
            if points_diff > 0:
                order.user.points += points_diff
        
        # Log activity
        activity = ActivityLog(
            subject_type='order',
            subject_id=order.id,
            action=f'Status updated to {order.status}',
            user_id=current_user.id
        )
        db.session.add(activity)
        
        db.session.commit()
        flash('Order updated successfully!', 'success')
        return redirect(url_for('admin.order_detail', order_id=order.id))
    
    # Generate QR code for barcode if exists
    qr_code_data = None
    if order.barcode:
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(url_for('api.track', barcode=order.barcode, _external=True))
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        qr_code_data = base64.b64encode(buffer.getvalue()).decode()
    
    return render_template('admin/order_detail.html', 
                         order=order, 
                         form=form, 
                         qr_code_data=qr_code_data)

@bp.route('/pickups')
@login_required
@admin_required
def pickups():
    page = request.args.get('page', 1, type=int)
    status_filter = request.args.get('status', '')
    
    query = PickupRequest.query
    if status_filter:
        query = query.filter_by(status=status_filter)
    
    pickups = query.order_by(PickupRequest.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    
    return render_template('admin/pickups.html', pickups=pickups, status_filter=status_filter)

@bp.route('/pickups/<int:pickup_id>/convert-to-order', methods=['POST'])
@login_required
@admin_required
def convert_pickup_to_order(pickup_id):
    pickup = PickupRequest.query.get_or_404(pickup_id)
    action = request.form.get('action')
    message = request.form.get('message', '')
    
    if action == 'accept':
        if pickup.service_type == 'donate':
            order = Order(
                user_id=pickup.user_id,
                pickup_id=pickup.id,
                service_type=pickup.service_type,
                status='received'
            )
            db.session.add(order)
            pickup.status = 'completed'
            flash('Donation request accepted and order created!', 'success')
        else:
            pickup.status = 'completed'
            flash('Pickup request accepted!', 'success')
    elif action == 'reject':
        pickup.status = 'rejected'
        pickup.notes += f'\nRejected by admin: {message}'
        flash('Pickup request rejected with message sent to user.', 'info')
    
    db.session.commit()
    return redirect(url_for('admin.pickups'))

@bp.route('/orders/<int:order_id>/approve', methods=['POST'])
@login_required
@admin_required
def approve_order(order_id):
    order = Order.query.get_or_404(order_id)
    
    if order.status == 'complete':
        order.status = 'approved'
        if not order.barcode:
            order.barcode = f"RS{order.id:06d}"
        
        activity = ActivityLog(
            subject_type='order',
            subject_id=order.id,
            action='Order approved for delivery',
            user_id=current_user.id
        )
        db.session.add(activity)
        db.session.commit()
        
        flash('Order approved and scheduled for delivery!', 'success')
    
    return redirect(url_for('admin.orders'))

@bp.route('/orders/<int:order_id>/approve-for-store', methods=['POST'])
@login_required
@admin_required
def approve_for_store(order_id):
    order = Order.query.get_or_404(order_id)
    
    if order.status == 'pending_approval' and order.service_type == 'resale':
        sale_price = 100
        if 'Expected Sale Price: ₹' in order.notes:
            try:
                price_str = order.notes.split('Expected Sale Price: ₹')[1].split('\n')[0]
                sale_price = float(price_str)
            except:
                pass
        
        product = Product(
            title=f"Resale Item #{order.id}",
            slug=f"resale-item-{order.id}",
            description=f"Quality resale item from user {order.user.name}",
            price=sale_price,
            stock=1,
            tags="resale,secondhand",
            is_featured=False
        )
        
        db.session.add(product)
        order.status = 'approved_for_store'
        db.session.commit()
        
        flash('Resale item approved and added to store!', 'success')
    
    return redirect(url_for('admin.orders'))

@bp.route('/products')
@login_required
@admin_required
def products():
    page = request.args.get('page', 1, type=int)
    products = Product.query.order_by(Product.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    
    return render_template('admin/products.html', products=products)

@bp.route('/products/new', methods=['GET', 'POST'])
@login_required
@admin_required
def new_product():
    form = ProductForm()
    designers = User.query.filter_by(role='designer').all()
    
    if form.validate_on_submit():
        slug = form.title.data.lower().replace(' ', '-').replace('/', '-')
        
        product = Product(
            title=form.title.data,
            slug=slug,
            description=form.description.data,
            price=form.price.data,
            stock=form.stock.data,
            designer_id=form.designer_id.data if form.designer_id.data != 0 else None,
            tags=form.tags.data,
            is_featured=form.is_featured.data
        )
        
        db.session.add(product)
        db.session.commit()
        
        flash('Product created successfully!', 'success')
        return redirect(url_for('admin.products'))
    
    return render_template('admin/product_form.html', form=form, designers=designers, title='New Product')

@bp.route('/products/<int:product_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_product(product_id):
    product = Product.query.get_or_404(product_id)
    form = ProductForm(obj=product)
    designers = User.query.filter_by(role='designer').all()
    
    if form.validate_on_submit():
        product.title = form.title.data
        product.description = form.description.data
        product.price = form.price.data
        product.stock = form.stock.data
        product.designer_id = form.designer_id.data if form.designer_id.data != 0 else None
        product.tags = form.tags.data
        product.is_featured = form.is_featured.data
        
        db.session.commit()
        
        flash('Product updated successfully!', 'success')
        return redirect(url_for('admin.products'))
    
    return render_template('admin/product_form.html', 
                         form=form, 
                         product=product, 
                         designers=designers,
                         title='Edit Product')

@bp.route('/users')
@login_required
@admin_required
def users():
    page = request.args.get('page', 1, type=int)
    users = User.query.order_by(User.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    
    return render_template('admin/users.html', users=users)

@bp.route('/designer-applications')
@login_required
@admin_required
def designer_applications():
    page = request.args.get('page', 1, type=int)
    status_filter = request.args.get('status', '')
    
    query = DesignerApplication.query
    if status_filter:
        query = query.filter_by(status=status_filter)
    
    applications = query.order_by(DesignerApplication.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    
    return render_template('admin/designer_applications.html', applications=applications, status_filter=status_filter)

@bp.route('/designer-applications/<int:app_id>/review', methods=['POST'])
@login_required
@admin_required
def review_designer_application(app_id):
    application = DesignerApplication.query.get_or_404(app_id)
    action = request.form.get('action')
    admin_notes = request.form.get('admin_notes', '')
    
    try:
        if action == 'approve':
            application.status = 'approved'
            application.user.role = 'designer'
            flash(f'{application.user.name} has been approved as a designer!', 'success')
        elif action == 'reject':
            application.status = 'rejected'
            flash(f'{application.user.name}\'s application has been rejected.', 'info')
        
        application.admin_notes = admin_notes
        application.reviewed_at = datetime.utcnow()
        application.reviewed_by = current_user.id
        
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error reviewing designer application: {e}")
        flash('Error processing application. Please try again.', 'error')
    
    return redirect(url_for('admin.designer_applications'))