from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from functools import wraps
from app.designer import bp
from app.models import Order, User
from app import db

def designer_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_designer():
            flash('Access denied. Designer privileges required.', 'error')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

@bp.route('/dashboard')
@login_required
@designer_required
def dashboard():
    # Get orders assigned to this designer
    review_orders = Order.query.filter_by(designer_id=current_user.id, status='review').all()
    in_progress_orders = Order.query.filter_by(designer_id=current_user.id, status='in_progress').all()
    completed_orders = Order.query.filter_by(designer_id=current_user.id, status='complete').all()
    
    stats = {
        'review': len(review_orders),
        'in_progress': len(in_progress_orders),
        'completed': len(completed_orders),
        'total': len(review_orders) + len(in_progress_orders) + len(completed_orders)
    }
    
    return render_template('designer/dashboard.html', 
                         stats=stats,
                         review_orders=review_orders,
                         in_progress_orders=in_progress_orders,
                         completed_orders=completed_orders)

@bp.route('/orders/<int:order_id>/accept', methods=['POST'])
@login_required
@designer_required
def accept_order(order_id):
    order = Order.query.get_or_404(order_id)
    
    if order.designer_id == current_user.id and order.status == 'review':
        order.status = 'in_progress'
        # Schedule pickup for the order
        if order.pickup_request:
            order.pickup_request.status = 'scheduled'
        db.session.commit()
        flash('Order accepted! Pickup has been scheduled.', 'success')
    
    return redirect(url_for('designer.dashboard'))

@bp.route('/orders/<int:order_id>/reject', methods=['POST'])
@login_required
@designer_required
def reject_order(order_id):
    order = Order.query.get_or_404(order_id)
    message = request.form.get('message', '')
    
    if order.designer_id == current_user.id and order.status == 'review':
        order.status = 'rejected'
        order.notes = f"Rejected by designer: {message}"
        db.session.commit()
        flash('Order rejected with message sent to user.', 'info')
    
    return redirect(url_for('designer.dashboard'))

@bp.route('/orders/<int:order_id>/complete', methods=['POST'])
@login_required
@designer_required
def complete_order(order_id):
    order = Order.query.get_or_404(order_id)
    
    if order.designer_id == current_user.id and order.status == 'in_progress':
        order.status = 'complete'
        db.session.commit()
        flash('Order completed! Sent to admin for final approval.', 'success')
    
    return redirect(url_for('designer.dashboard'))