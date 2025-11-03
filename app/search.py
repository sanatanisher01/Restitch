from sqlalchemy import or_, and_, func
from app.models import Product, Order, User
from datetime import datetime, timedelta

class ProductSearch:
    def __init__(self, query=None):
        self.base_query = query or Product.query
    
    def search(self, term):
        if term:
            self.base_query = self.base_query.filter(
                or_(
                    Product.title.contains(term),
                    Product.description.contains(term),
                    Product.tags.contains(term)
                )
            )
        return self
    
    def filter_price(self, min_price=None, max_price=None):
        if min_price:
            self.base_query = self.base_query.filter(Product.price >= min_price)
        if max_price:
            self.base_query = self.base_query.filter(Product.price <= max_price)
        return self
    
    def filter_designer(self, designer_id):
        if designer_id:
            self.base_query = self.base_query.filter(Product.designer_id == designer_id)
        return self
    
    def filter_featured(self, featured=None):
        if featured is not None:
            self.base_query = self.base_query.filter(Product.is_featured == featured)
        return self
    
    def filter_in_stock(self):
        self.base_query = self.base_query.filter(Product.stock > 0)
        return self
    
    def sort_by(self, sort_type):
        if sort_type == 'price_low':
            self.base_query = self.base_query.order_by(Product.price.asc())
        elif sort_type == 'price_high':
            self.base_query = self.base_query.order_by(Product.price.desc())
        elif sort_type == 'newest':
            self.base_query = self.base_query.order_by(Product.created_at.desc())
        elif sort_type == 'oldest':
            self.base_query = self.base_query.order_by(Product.created_at.asc())
        elif sort_type == 'popular':
            # Sort by number of transactions (popularity)
            from app.models import Transaction
            self.base_query = self.base_query.outerjoin(Transaction).group_by(Product.id).order_by(func.count(Transaction.id).desc())
        return self
    
    def paginate(self, page=1, per_page=12):
        return self.base_query.paginate(page=page, per_page=per_page, error_out=False)

class OrderSearch:
    def __init__(self, query=None):
        self.base_query = query or Order.query
    
    def filter_status(self, status):
        if status:
            self.base_query = self.base_query.filter(Order.status == status)
        return self
    
    def filter_date_range(self, start_date=None, end_date=None):
        if start_date:
            self.base_query = self.base_query.filter(Order.created_at >= start_date)
        if end_date:
            self.base_query = self.base_query.filter(Order.created_at <= end_date)
        return self
    
    def filter_user(self, user_id):
        if user_id:
            self.base_query = self.base_query.filter(Order.user_id == user_id)
        return self
    
    def search_barcode(self, barcode):
        if barcode:
            self.base_query = self.base_query.filter(Order.barcode.contains(barcode))
        return self
    
    def paginate(self, page=1, per_page=20):
        return self.base_query.order_by(Order.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)