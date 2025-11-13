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
                'title': 'Patchwork Denim Sherpa Jacket',
                'slug': 'patchwork-denim-sherpa-jacket',
                'description': 'A cozy and stylish oversized jacket crafted from mixed denim patches and lined with soft sherpa. Perfect for adding texture and warmth to your everyday outfits. Each piece is uniquely pieced, giving it a one-of-a-kind look.',
                'price': 899.00,
                'stock': 2,
                'tags': 'denim, jacket, sherpa, patchwork, cozy',
                'is_featured': True,
                'image_url': 'https://res.cloudinary.com/dgtud2toy/image/upload/v1763014112/img1_gfaqjk.jpg'
            },
            {
                'title': 'Handmade Patchwork Hippo Plushie',
                'slug': 'handmade-patchwork-hippo-plushie',
                'description': 'A cute, soft, and child-safe plush hippo made from assorted patterned fabrics. Ideal as a nursery decoration, cuddle toy, or meaningful handmade gift.',
                'price': 599.00,
                'stock': 5,
                'tags': 'plushie, kids, handmade, patchwork, gift',
                'is_featured': True,
                'image_url': 'https://res.cloudinary.com/dgtud2toy/image/upload/v1763014118/img2_g01qu2.jpg'
            },
            {
                'title': 'Cute Patchwork Cushion Pillow',
                'slug': 'cute-patchwork-cushion-pillow',
                'description': 'A charming decorative pillow stitched with pastel patchwork squares. Perfect for kids rooms, nurseries, or adding a soft touch to any couch or bed.',
                'price': 549.00,
                'stock': 8,
                'tags': 'cushion, pillow, home decor, patchwork, pastel',
                'is_featured': False,
                'image_url': 'https://res.cloudinary.com/dgtud2toy/image/upload/v1763014124/img3_bssdv3.jpg'
            },
            {
                'title': 'Upcycled Denim Patchwork Tote Bag',
                'slug': 'upcycled-denim-patchwork-tote-bag',
                'description': 'A durable eco-friendly tote made from repurposed denim patches. Stylish, spacious, and strong—perfect for daily errands, shopping, or casual outings.',
                'price': 699.00,
                'stock': 6,
                'tags': 'tote bag, denim, eco-friendly, patchwork, accessories',
                'is_featured': True,
                'image_url': 'https://res.cloudinary.com/dgtud2toy/image/upload/v1763014132/img4_rgsaky.jpg'
            },
            {
                'title': 'Vintage-Style Patchwork Maxi Skirt',
                'slug': 'vintage-style-patchwork-maxi-skirt',
                'description': 'A beautifully flowy maxi skirt featuring a denim waistband and patchwork fabric panels. Lightweight, boho-inspired, and uniquely handmade from mixed prints.',
                'price': 799.00,
                'stock': 3,
                'tags': 'maxi skirt, vintage, boho, patchwork, denim',
                'is_featured': True,
                'image_url': 'https://res.cloudinary.com/dgtud2toy/image/upload/v1763014139/img5_mbbwdg.jpg'
            },
            {
                'title': 'Personalized Patchwork Memory Blanket',
                'slug': 'personalized-patchwork-memory-blanket',
                'description': 'A cozy keepsake blanket made from meaningful fabrics such as baby clothes, T-shirts, or special garments. Soft backing ensures comfort while preserving precious memories.',
                'price': 999.00,
                'stock': 2,
                'tags': 'blanket, memory, keepsake, patchwork, personalized',
                'is_featured': False,
                'image_url': 'https://res.cloudinary.com/dgtud2toy/image/upload/v1763014149/img6_r0acom.jpg'
            },
            {
                'title': 'Custom T-Shirt Memory Quilt',
                'slug': 'custom-t-shirt-memory-quilt',
                'description': 'A large, beautifully arranged quilt made from sentimental T-shirts. Perfect as a graduation gift, milestone keepsake, or a way to preserve childhood favorites.',
                'price': 899.00,
                'stock': 1,
                'tags': 'quilt, t-shirt, memory, custom, keepsake',
                'is_featured': True,
                'image_url': 'https://res.cloudinary.com/dgtud2toy/image/upload/v1763014156/img7_pb7hc1.jpg'
            },
            {
                'title': 'Colorful Boho Patchwork Skirt',
                'slug': 'colorful-boho-patchwork-skirt',
                'description': 'A vibrant statement skirt made from assorted colorful fabric blocks. Flowy, bold, and artistic—ideal for boho fashion lovers who enjoy unique handmade style.',
                'price': 749.00,
                'stock': 4,
                'tags': 'boho, skirt, colorful, patchwork, artistic',
                'is_featured': False,
                'image_url': 'https://res.cloudinary.com/dgtud2toy/image/upload/v1763014194/img8_juan8g.jpg'
            },
            {
                'title': 'Geometric Patchwork Tote Bag',
                'slug': 'geometric-patchwork-tote-bag',
                'description': 'A modern quilt-style tote with bold geometric shapes and soft tones. Lightweight yet sturdy, great for books, crafts, or everyday carry.',
                'price': 649.00,
                'stock': 7,
                'tags': 'tote bag, geometric, modern, patchwork, quilt',
                'is_featured': False,
                'image_url': 'https://res.cloudinary.com/dgtud2toy/image/upload/v1763014199/img9_owpqs5.jpg'
            },
            {
                'title': 'Quilt-Patch Denim Jacket with Embroidered Accents',
                'slug': 'quilt-patch-denim-jacket-embroidered',
                'description': 'A denim jacket decorated with colorful quilt blocks and embroidered embellishments. A perfect blend of classic denim and vibrant quilt art—truly one of a kind.',
                'price': 949.00,
                'stock': 2,
                'tags': 'denim jacket, quilt, embroidered, unique, artistic',
                'is_featured': True,
                'image_url': 'https://res.cloudinary.com/dgtud2toy/image/upload/v1763014204/img10_owsh0x.jpg'
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
            # Set the image URL
            product.set_images([product_data['image_url']])
            db.session.add(product)
        
        db.session.commit()
        
        # Create some transactions
        for i in range(8):
            transaction = Transaction(
                user_id=users[i % len(users)].id,
                product_id=(i % 10) + 1,
                amount=random.uniform(549, 999),
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