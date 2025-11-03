from celery import Celery
from app.email import send_order_update_email, send_pickup_confirmation_email
from app.models import User, Order, PickupRequest
from app import create_app, db

def make_celery(app):
    celery = Celery(
        app.import_name,
        backend=app.config.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0'),
        broker=app.config.get('CELERY_BROKER_URL', 'redis://localhost:6379/0')
    )
    
    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)
    
    celery.Task = ContextTask
    return celery

# Initialize Celery
app = create_app()
celery = make_celery(app)

@celery.task
def send_order_notification(order_id):
    """Send order update notification"""
    with app.app_context():
        order = Order.query.get(order_id)
        if order:
            send_order_update_email(order.user, order)

@celery.task
def send_pickup_notification(pickup_id):
    """Send pickup confirmation notification"""
    with app.app_context():
        pickup = PickupRequest.query.get(pickup_id)
        if pickup:
            send_pickup_confirmation_email(pickup.user, pickup)

@celery.task
def process_inventory_alerts():
    """Check for low stock and send alerts"""
    with app.app_context():
        from app.ecommerce import InventoryManager
        low_stock_products = InventoryManager.check_low_stock()
        
        if low_stock_products:
            # Send alert to admin
            admin_users = User.query.filter_by(role='admin').all()
            for admin in admin_users:
                # Send low stock alert email
                pass

@celery.task
def cleanup_expired_sessions():
    """Clean up expired user sessions"""
    # Implement session cleanup logic
    pass

@celery.task
def generate_daily_reports():
    """Generate daily analytics reports"""
    with app.app_context():
        from app.analytics import Analytics
        stats = Analytics.get_dashboard_stats()
        # Generate and email daily report
        pass