from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, login_manager
import json

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20))
    role = db.Column(db.String(20), default='user')  # user, admin, designer
    points = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    addresses = db.relationship('Address', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    pickup_requests = db.relationship('PickupRequest', backref='user', lazy='dynamic')
    orders = db.relationship('Order', foreign_keys='Order.user_id', backref='user', lazy='dynamic')
    transactions = db.relationship('Transaction', backref='user', lazy='dynamic')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def is_admin(self):
        return self.role == 'admin'
    
    def is_designer(self):
        return self.role == 'designer'

class Address(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    line1 = db.Column(db.String(200), nullable=False)
    line2 = db.Column(db.String(200))
    city = db.Column(db.String(100), nullable=False)
    state = db.Column(db.String(100), nullable=False)
    zip_code = db.Column(db.String(20), nullable=False)
    lat = db.Column(db.Float)
    lng = db.Column(db.Float)
    is_default = db.Column(db.Boolean, default=False)

class PickupRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    address_id = db.Column(db.Integer, db.ForeignKey('address.id'), nullable=False)
    preferred_slot = db.Column(db.DateTime, nullable=False)
    service_type = db.Column(db.String(20), nullable=False)  # donate, redesign, resale
    status = db.Column(db.String(20), default='pending')  # pending, scheduled, picked_up, completed
    items_json = db.Column(db.Text)  # JSON string of item descriptions
    photos = db.Column(db.Text)  # JSON array of photo paths
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    address = db.relationship('Address', backref='pickup_requests')
    orders = db.relationship('Order', backref='pickup_request', lazy='dynamic')
    
    def get_items(self):
        return json.loads(self.items_json) if self.items_json else []
    
    def set_items(self, items):
        self.items_json = json.dumps(items)
    
    def get_photos(self):
        return json.loads(self.photos) if self.photos else []
    
    def set_photos(self, photos):
        self.photos = json.dumps(photos)

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    pickup_id = db.Column(db.Integer, db.ForeignKey('pickup_request.id'))
    designer_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    status = db.Column(db.String(30), default='received')  # received, sorting, designing, ready, shipped, delivered
    service_type = db.Column(db.String(20), default='redesign')  # donate, redesign, resale
    fabric_type = db.Column(db.String(100))
    notes = db.Column(db.Text)
    estimated_days = db.Column(db.Integer)
    images_before = db.Column(db.Text)  # JSON array of image paths
    images_after = db.Column(db.Text)  # JSON array of image paths
    video_url = db.Column(db.String(500))
    barcode = db.Column(db.String(100), unique=True, index=True)
    points_awarded = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    designer = db.relationship('User', foreign_keys=[designer_id], backref='designed_orders')
    activity_logs = db.relationship('ActivityLog', 
                                   primaryjoin="and_(Order.id==ActivityLog.subject_id, ActivityLog.subject_type=='order')", 
                                   foreign_keys='ActivityLog.subject_id', 
                                   lazy='dynamic')
    
    def get_images_before(self):
        return json.loads(self.images_before) if self.images_before else []
    
    def set_images_before(self, images):
        self.images_before = json.dumps(images)
    
    def get_images_after(self):
        return json.loads(self.images_after) if self.images_after else []
    
    def set_images_after(self, images):
        self.images_after = json.dumps(images)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(200), unique=True, nullable=False, index=True)
    description = db.Column(db.Text)
    images = db.Column(db.Text)  # JSON array of image paths
    video_demo = db.Column(db.String(500))
    price = db.Column(db.Numeric(10, 2), nullable=False)
    stock = db.Column(db.Integer, default=1)
    designer_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    tags = db.Column(db.String(500))  # Comma-separated tags
    is_featured = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    designer = db.relationship('User', backref='products')
    transactions = db.relationship('Transaction', backref='product', lazy='dynamic')
    
    def get_images(self):
        return json.loads(self.images) if self.images else []
    
    def set_images(self, images):
        self.images = json.dumps(images)
    
    def get_tags(self):
        return [tag.strip() for tag in self.tags.split(',') if tag.strip()] if self.tags else []

class StoreOrder(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    order_number = db.Column(db.String(20), unique=True, nullable=False, index=True)
    total_amount = db.Column(db.Numeric(10, 2), nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, confirmed, shipped, delivered, cancelled
    shipping_address = db.Column(db.Text)
    payment_method = db.Column(db.String(50))
    payment_id = db.Column(db.String(200))
    tracking_number = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    shipped_at = db.Column(db.DateTime)
    delivered_at = db.Column(db.DateTime)
    
    # Relationships
    user = db.relationship('User', backref='store_orders')
    items = db.relationship('StoreOrderItem', backref='order', lazy='dynamic', cascade='all, delete-orphan')

class StoreOrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('store_order.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    
    # Relationships
    product = db.relationship('Product')

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, completed, failed
    stripe_payment_id = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

class ActivityLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subject_type = db.Column(db.String(50), nullable=False)  # order, pickup, product
    subject_id = db.Column(db.Integer, nullable=False)
    action = db.Column(db.String(100), nullable=False)
    metadata_json = db.Column(db.Text)  # JSON metadata
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    user = db.relationship('User')
    
    def get_metadata(self):
        return json.loads(self.metadata_json) if self.metadata_json else {}
    
    def set_metadata(self, metadata):
        self.metadata_json = json.dumps(metadata)

class DesignerApplication(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    portfolio_url = db.Column(db.String(500))
    experience_years = db.Column(db.Integer)
    specialization = db.Column(db.String(200))
    why_designer = db.Column(db.Text)
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected
    admin_notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    reviewed_at = db.Column(db.DateTime)
    reviewed_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    # Relationships
    user = db.relationship('User', foreign_keys=[user_id], backref='designer_application')
    reviewer = db.relationship('User', foreign_keys=[reviewed_by])

class CityExpansion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    is_active = db.Column(db.Boolean, default=False)
    launch_date = db.Column(db.Date)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)