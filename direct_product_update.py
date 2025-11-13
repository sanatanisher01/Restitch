#!/usr/bin/env python3
"""
Direct product update script - run this manually to force update products
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import Product, User

def main():
    app = create_app()
    
    with app.app_context():
        try:
            print("Starting product update...")
            
            # Get designer
            designer = User.query.filter_by(role='designer').first()
            if not designer:
                print("No designer found!")
                return
            
            print(f"Found designer: {designer.name}")
            
            # Delete all products
            deleted_count = Product.query.count()
            Product.query.delete()
            db.session.commit()
            print(f"Deleted {deleted_count} old products")
            
            # Create new products
            products = [
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
            
            # Add new products
            for i, product_data in enumerate(products, 1):
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
                product.set_images([product_data['image_url']])
                db.session.add(product)
                print(f"Added product {i}: {product_data['title']}")
            
            db.session.commit()
            
            # Verify products were added
            new_count = Product.query.count()
            print(f"Successfully added {new_count} new products!")
            
            # List all products
            all_products = Product.query.all()
            print("\nCurrent products in database:")
            for p in all_products:
                print(f"- {p.title} (Rs.{p.price})")
                
        except Exception as e:
            db.session.rollback()
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    main()