from app import create_app, db
from app.models import User, Address, PickupRequest, Order, Product, Transaction, ActivityLog, CityExpansion
from datetime import datetime, timedelta
import random

def seed_database():
    app = create_app()
    
    with app.app_context():
        # Check if we're in development or if database is empty
        import os
        is_production = os.environ.get('FLASK_ENV') == 'production'
        
        if not is_production:
            # Drop and create all tables in development
            db.drop_all()
            db.create_all()
        else:
            # In production, only create tables if they don't exist
            db.create_all()
        
        # Create admin user
        admin = User(
            email='admin@restitch.com',
            name='Admin User',
            phone='+91-9876543210',
            role='admin',
            points=1000
        )
        admin.set_password('admin123')
        db.session.add(admin)
        
        # Create designer user
        designer = User(
            email='designer@restitch.com',
            name='Sarah Designer',
            phone='+91-9876543211',
            role='designer',
            points=500
        )
        designer.set_password('designer123')
        db.session.add(designer)
        
        # Create regular users
        users_data = [
            {'name': 'Priya Sharma', 'email': 'priya@example.com', 'phone': '+91-9876543212'},
            {'name': 'Rahul Kumar', 'email': 'rahul@example.com', 'phone': '+91-9876543213'},
            {'name': 'Anita Singh', 'email': 'anita@example.com', 'phone': '+91-9876543214'},
            {'name': 'Vikram Patel', 'email': 'vikram@example.com', 'phone': '+91-9876543215'},
            {'name': 'Meera Gupta', 'email': 'meera@example.com', 'phone': '+91-9876543216'},
        ]
        
        users = []
        for user_data in users_data:
            user = User(
                email=user_data['email'],
                name=user_data['name'],
                phone=user_data['phone'],
                points=random.randint(50, 500)
            )
            user.set_password('password123')
            users.append(user)
            db.session.add(user)
        
        db.session.commit()
        
        # Create addresses for users
        addresses_data = [
            {'line1': '123 MG Road', 'city': 'Bangalore', 'state': 'Karnataka', 'zip_code': '560001'},
            {'line1': '456 Park Street', 'city': 'Delhi', 'state': 'Delhi', 'zip_code': '110001'},
            {'line1': '789 Marine Drive', 'city': 'Mumbai', 'state': 'Maharashtra', 'zip_code': '400001'},
            {'line1': '321 Brigade Road', 'city': 'Bangalore', 'state': 'Karnataka', 'zip_code': '560025'},
            {'line1': '654 Connaught Place', 'city': 'Delhi', 'state': 'Delhi', 'zip_code': '110002'},
        ]
        
        for i, addr_data in enumerate(addresses_data):
            address = Address(
                user_id=users[i].id,
                line1=addr_data['line1'],
                city=addr_data['city'],
                state=addr_data['state'],
                zip_code=addr_data['zip_code'],
                is_default=True
            )
            db.session.add(address)
        
        db.session.commit()
        
        # Create pickup requests
        service_types = ['donate', 'redesign', 'resale']
        statuses = ['pending', 'scheduled', 'picked_up', 'completed']
        
        for i in range(10):
            pickup = PickupRequest(
                user_id=users[i % len(users)].id,
                address_id=i % len(addresses_data) + 1,
                preferred_slot=datetime.utcnow() + timedelta(days=random.randint(1, 30)),
                service_type=random.choice(service_types),
                status=random.choice(statuses),
                notes=f'Sample pickup request {i+1}'
            )
            pickup.set_items(['Cotton shirt', 'Denim jeans', 'Winter jacket'])
            db.session.add(pickup)
        
        db.session.commit()
        
        # Create orders
        order_statuses = ['received', 'sorting', 'designing', 'ready', 'shipped', 'delivered']
        fabric_types = ['Cotton', 'Denim', 'Silk', 'Wool', 'Polyester', 'Linen']
        
        for i in range(15):
            order = Order(
                user_id=users[i % len(users)].id,
                pickup_id=(i % 10) + 1,
                designer_id=designer.id,
                status=random.choice(order_statuses),
                fabric_type=random.choice(fabric_types),
                notes=f'Sample order notes for order {i+1}',
                estimated_days=random.randint(7, 21),
                points_awarded=random.randint(10, 100)
            )
            
            db.session.add(order)
        
        db.session.commit()
        
        # Update barcodes after commit to get IDs
        orders = Order.query.all()
        for order in orders:
            if order.status in ['ready', 'shipped', 'delivered'] and not order.barcode:
                order.barcode = f'RS{order.id:06d}'
        
        db.session.commit()
        
        # Create products
        products_data = [
            {
                'title': 'Upcycled Denim Jacket',
                'slug': 'upcycled-denim-jacket',
                'description': 'A beautiful denim jacket transformed from old jeans with artistic patches and embroidery.',
                'price': 2499.00,
                'stock': 3,
                'tags': 'denim, jacket, casual, upcycled',
                'is_featured': True
            },
            {
                'title': 'Vintage Cotton Dress',
                'slug': 'vintage-cotton-dress',
                'description': 'Elegant cotton dress redesigned from vintage fabrics with modern cuts.',
                'price': 1899.00,
                'stock': 2,
                'tags': 'cotton, dress, vintage, formal',
                'is_featured': True
            },
            {
                'title': 'Patchwork Tote Bag',
                'slug': 'patchwork-tote-bag',
                'description': 'Colorful tote bag made from fabric scraps and old clothing pieces.',
                'price': 899.00,
                'stock': 5,
                'tags': 'bag, accessories, patchwork, eco-friendly',
                'is_featured': False
            },
            {
                'title': 'Redesigned Silk Scarf',
                'slug': 'redesigned-silk-scarf',
                'description': 'Luxurious silk scarf created from repurposed silk garments.',
                'price': 1299.00,
                'stock': 4,
                'tags': 'silk, scarf, accessories, luxury',
                'is_featured': True
            },
            {
                'title': 'Upcycled Wool Sweater',
                'slug': 'upcycled-wool-sweater',
                'description': 'Cozy wool sweater redesigned with contemporary patterns.',
                'price': 3299.00,
                'stock': 1,
                'tags': 'wool, sweater, winter, warm',
                'is_featured': False
            },
            {
                'title': 'Denim Patchwork Skirt',
                'slug': 'denim-patchwork-skirt',
                'description': 'Trendy skirt made from various denim pieces in different washes.',
                'price': 1699.00,
                'stock': 3,
                'tags': 'denim, skirt, patchwork, trendy',
                'is_featured': False
            }
        ]
        
        for product_data in products_data:
            product = Product(
                title=product_data['title'],
                slug=product_data['slug'],
                description=product_data['description'],
                price=product_data['price'],
                stock=product_data['stock'],
                designer_id=designer.id,
                tags=product_data['tags'],
                is_featured=product_data['is_featured']
            )
            db.session.add(product)
        
        db.session.commit()
        
        # Create some transactions
        for i in range(8):
            transaction = Transaction(
                user_id=users[i % len(users)].id,
                product_id=(i % 6) + 1,
                amount=random.uniform(899, 3299),
                status='completed'
            )
            db.session.add(transaction)
        
        # Create city expansion data
        cities = [
            {'name': 'Bangalore', 'is_active': True},
            {'name': 'Delhi', 'is_active': True},
            {'name': 'Mumbai', 'is_active': True},
            {'name': 'Chennai', 'is_active': False},
            {'name': 'Hyderabad', 'is_active': False},
            {'name': 'Pune', 'is_active': False},
        ]
        
        for city_data in cities:
            city = CityExpansion(
                name=city_data['name'],
                is_active=city_data['is_active']
            )
            db.session.add(city)
        
        # Create activity logs
        for i in range(20):
            activity = ActivityLog(
                subject_type='order',
                subject_id=(i % 15) + 1,
                action=f'Status updated to {random.choice(order_statuses)}',
                user_id=admin.id
            )
            db.session.add(activity)
        
        db.session.commit()
        
        print("Database seeded successfully!")
        print("\nSample login credentials:")
        print("Admin: admin@restitch.com / admin123")
        print("Designer: designer@restitch.com / designer123")
        print("User: priya@example.com / password123")

if __name__ == '__main__':
    seed_database()