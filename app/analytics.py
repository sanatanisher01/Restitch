from sqlalchemy import func, extract
from app.models import User, Order, Product, Transaction, PickupRequest
from app import db
from datetime import datetime, timedelta
import json

class Analytics:
    @staticmethod
    def get_dashboard_stats():
        """Get key metrics for admin dashboard"""
        total_users = User.query.count()
        total_orders = Order.query.count()
        total_revenue = db.session.query(func.sum(Transaction.amount)).filter_by(status='completed').scalar() or 0
        total_products = Product.query.count()
        
        # Growth metrics (last 30 days)
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        new_users = User.query.filter(User.created_at >= thirty_days_ago).count()
        new_orders = Order.query.filter(Order.created_at >= thirty_days_ago).count()
        
        return {
            'total_users': total_users,
            'total_orders': total_orders,
            'total_revenue': float(total_revenue),
            'total_products': total_products,
            'new_users_30d': new_users,
            'new_orders_30d': new_orders,
            'avg_order_value': float(total_revenue / total_orders) if total_orders > 0 else 0
        }
    
    @staticmethod
    def get_sales_by_month(months=12):
        """Get monthly sales data"""
        results = db.session.query(
            extract('year', Transaction.created_at).label('year'),
            extract('month', Transaction.created_at).label('month'),
            func.sum(Transaction.amount).label('total'),
            func.count(Transaction.id).label('count')
        ).filter_by(status='completed').group_by(
            extract('year', Transaction.created_at),
            extract('month', Transaction.created_at)
        ).order_by('year', 'month').limit(months).all()
        
        return [{
            'year': int(r.year),
            'month': int(r.month),
            'total': float(r.total),
            'count': r.count
        } for r in results]
    
    @staticmethod
    def get_popular_products(limit=10):
        """Get most popular products by sales"""
        results = db.session.query(
            Product,
            func.count(Transaction.id).label('sales_count'),
            func.sum(Transaction.amount).label('total_revenue')
        ).join(Transaction).filter_by(status='completed').group_by(Product.id).order_by(
            func.count(Transaction.id).desc()
        ).limit(limit).all()
        
        return [{
            'product': r.Product,
            'sales_count': r.sales_count,
            'total_revenue': float(r.total_revenue)
        } for r in results]
    
    @staticmethod
    def get_user_analytics():
        """Get user behavior analytics"""
        # User registration by month
        user_growth = db.session.query(
            extract('year', User.created_at).label('year'),
            extract('month', User.created_at).label('month'),
            func.count(User.id).label('count')
        ).group_by(
            extract('year', User.created_at),
            extract('month', User.created_at)
        ).order_by('year', 'month').all()
        
        # Top customers by orders
        try:
            top_customers = db.session.query(
                User,
                func.count(Order.id).label('order_count'),
                func.coalesce(func.sum(Transaction.amount), 0).label('total_spent')
            ).join(Order).outerjoin(Transaction).filter(
                Transaction.status == 'completed'
            ).group_by(User.id).order_by(
                func.count(Order.id).desc()
            ).limit(10).all()
        except Exception:
            top_customers = []
        
        return {
            'user_growth': [{
                'year': int(r.year),
                'month': int(r.month),
                'count': r.count
            } for r in user_growth],
            'top_customers': [{
                'user': r.User,
                'order_count': r.order_count,
                'total_spent': float(r.total_spent or 0)
            } for r in top_customers]
        }
    
    @staticmethod
    def get_inventory_report():
        """Get inventory status report"""
        low_stock = Product.query.filter(Product.stock <= 5, Product.stock > 0).all()
        out_of_stock = Product.query.filter_by(stock=0).all()
        total_inventory_value = db.session.query(
            func.sum(Product.price * Product.stock)
        ).scalar() or 0
        
        return {
            'low_stock_products': low_stock,
            'out_of_stock_products': out_of_stock,
            'total_inventory_value': float(total_inventory_value),
            'total_products': Product.query.count()
        }