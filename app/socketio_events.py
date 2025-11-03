from flask_socketio import emit, join_room, leave_room
from flask_login import current_user
from app import socketio, db
from app.models import Order, User
from datetime import datetime

@socketio.on('connect')
def on_connect():
    if current_user.is_authenticated:
        join_room(f'user_{current_user.id}')
        emit('status', {'msg': f'{current_user.name} connected'})

@socketio.on('disconnect')
def on_disconnect():
    if current_user.is_authenticated:
        leave_room(f'user_{current_user.id}')

@socketio.on('join_order_room')
def on_join_order(data):
    order_id = data['order_id']
    join_room(f'order_{order_id}')
    emit('status', {'msg': f'Joined order {order_id} tracking'})

@socketio.on('track_order')
def handle_order_tracking(data):
    barcode = data['barcode']
    order = Order.query.filter_by(barcode=barcode).first()
    if order:
        emit('order_update', {
            'barcode': barcode,
            'status': order.status,
            'updated_at': order.updated_at.isoformat()
        })

def notify_order_update(order_id, status):
    """Notify all connected clients about order update"""
    socketio.emit('order_status_update', {
        'order_id': order_id,
        'status': status,
        'timestamp': datetime.utcnow().isoformat()
    }, room=f'order_{order_id}')

def notify_user(user_id, message, type='info'):
    """Send notification to specific user"""
    socketio.emit('notification', {
        'message': message,
        'type': type,
        'timestamp': datetime.utcnow().isoformat()
    }, room=f'user_{user_id}')