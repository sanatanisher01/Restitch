from flask import render_template, jsonify, request
from app.api import bp
from app.models import Order, ActivityLog

@bp.route('/track/<barcode>')
def track(barcode):
    """Public tracking page for barcode/QR codes"""
    order = Order.query.filter_by(barcode=barcode).first_or_404()
    
    # Get activity timeline
    activities = ActivityLog.query.filter_by(
        subject_type='order',
        subject_id=order.id
    ).order_by(ActivityLog.timestamp.asc()).all()
    
    # Status timeline for display
    status_timeline = [
        {'status': 'received', 'label': 'Received', 'completed': True},
        {'status': 'sorting', 'label': 'Sorting', 'completed': order.status in ['sorting', 'designing', 'ready', 'shipped', 'delivered']},
        {'status': 'designing', 'label': 'Designing', 'completed': order.status in ['designing', 'ready', 'shipped', 'delivered']},
        {'status': 'ready', 'label': 'Ready', 'completed': order.status in ['ready', 'shipped', 'delivered']},
        {'status': 'shipped', 'label': 'Shipped', 'completed': order.status in ['shipped', 'delivered']},
        {'status': 'delivered', 'label': 'Delivered', 'completed': order.status == 'delivered'}
    ]
    
    return render_template('api/track.html', 
                         order=order, 
                         activities=activities, 
                         status_timeline=status_timeline)

@bp.route('/stats')
def stats():
    """Public API endpoint for site statistics"""
    from app.models import User, Order, Product
    
    stats = {
        'total_users': User.query.count(),
        'total_orders': Order.query.count(),
        'total_products': Product.query.count(),
        'kg_saved': Order.query.count() * 2.5,  # Estimate
        'trees_saved': int(Order.query.count() * 0.1)
    }
    
    return jsonify(stats)