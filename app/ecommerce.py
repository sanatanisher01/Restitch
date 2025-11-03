from app.models import Product, User, Order
from app import db
from sqlalchemy import func, desc
import random

class WishlistManager:
    @staticmethod
    def add_to_wishlist(user_id, product_id):
        # Add wishlist table to models if needed
        pass
    
    @staticmethod
    def remove_from_wishlist(user_id, product_id):
        pass
    
    @staticmethod
    def get_user_wishlist(user_id):
        pass

class ReviewSystem:
    @staticmethod
    def add_review(user_id, product_id, rating, comment):
        # Add review table to models if needed
        pass
    
    @staticmethod
    def get_product_reviews(product_id):
        pass
    
    @staticmethod
    def get_average_rating(product_id):
        pass

class RecommendationEngine:
    @staticmethod
    def get_similar_products(product_id, limit=4):
        """Get products similar to given product"""
        product = Product.query.get(product_id)
        if not product:
            return []
        
        # Simple recommendation based on tags
        product_tags = set(product.get_tags())
        
        similar_products = []
        all_products = Product.query.filter(
            Product.id != product_id,
            Product.stock > 0
        ).all()
        
        for p in all_products:
            p_tags = set(p.get_tags())
            similarity = len(product_tags.intersection(p_tags)) / len(product_tags.union(p_tags)) if product_tags.union(p_tags) else 0
            if similarity > 0:
                similar_products.append((p, similarity))
        
        # Sort by similarity and return top results
        similar_products.sort(key=lambda x: x[1], reverse=True)
        return [p[0] for p in similar_products[:limit]]
    
    @staticmethod
    def get_recommended_for_user(user_id, limit=6):
        """Get personalized recommendations for user"""
        user = User.query.get(user_id)
        if not user:
            return Product.query.filter(Product.stock > 0).limit(limit).all()
        
        # Get user's order history
        user_orders = Order.query.filter_by(user_id=user_id).all()
        
        if not user_orders:
            # New user - return popular/featured products
            return Product.query.filter(
                Product.is_featured == True,
                Product.stock > 0
            ).limit(limit).all()
        
        # For existing users, recommend based on purchase history
        # This is a simplified version - in production, use ML algorithms
        purchased_tags = set()
        for order in user_orders:
            if order.pickup_request:
                # Analyze pickup items for preferences
                pass
        
        # Return featured products for now
        return Product.query.filter(
            Product.is_featured == True,
            Product.stock > 0
        ).limit(limit).all()
    
    @staticmethod
    def get_trending_products(limit=8):
        """Get trending products based on recent sales"""
        from app.models import Transaction
        from datetime import datetime, timedelta
        
        # Get products with most transactions in last 30 days
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        
        trending = db.session.query(
            Product,
            func.count(Transaction.id).label('sales_count')
        ).join(Transaction).filter(
            Transaction.created_at >= thirty_days_ago,
            Transaction.status == 'completed',
            Product.stock > 0
        ).group_by(Product.id).order_by(
            desc('sales_count')
        ).limit(limit).all()
        
        return [item.Product for item in trending]

class CouponSystem:
    @staticmethod
    def create_coupon(code, discount_type, discount_value, min_amount=0, max_uses=None, expires_at=None):
        """Create a new coupon"""
        # Add coupon table to models if needed
        pass
    
    @staticmethod
    def validate_coupon(code, cart_total):
        """Validate and return coupon details"""
        # Check if coupon exists, is valid, not expired, etc.
        pass
    
    @staticmethod
    def apply_coupon(code, cart_total):
        """Apply coupon and return discounted amount"""
        pass

class InventoryManager:
    @staticmethod
    def check_low_stock(threshold=5):
        """Get products with low stock"""
        return Product.query.filter(
            Product.stock <= threshold,
            Product.stock > 0
        ).all()
    
    @staticmethod
    def get_out_of_stock():
        """Get out of stock products"""
        return Product.query.filter_by(stock=0).all()
    
    @staticmethod
    def update_stock(product_id, quantity):
        """Update product stock"""
        product = Product.query.get(product_id)
        if product:
            product.stock = max(0, product.stock + quantity)
            db.session.commit()
            return True
        return False
    
    @staticmethod
    def reserve_stock(product_id, quantity):
        """Reserve stock for pending orders"""
        product = Product.query.get(product_id)
        if product and product.stock >= quantity:
            product.stock -= quantity
            db.session.commit()
            return True
        return False