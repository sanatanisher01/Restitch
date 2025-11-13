#!/usr/bin/env python3
"""
Debug script to check product images
"""

from app import create_app, db
from app.models import Product
import json

def debug_images():
    app = create_app()
    
    with app.app_context():
        products = Product.query.all()
        print(f"Found {len(products)} products:")
        
        for product in products:
            print(f"\n--- {product.title} ---")
            print(f"Images field: {product.images}")
            print(f"get_images(): {product.get_images()}")
            
            # Try to fix images if they're not working
            if not product.get_images():
                # Map product titles to their correct images
                image_map = {
                    'Patchwork Denim Sherpa Jacket': 'https://res.cloudinary.com/dgtud2toy/image/upload/v1763014112/img1_gfaqjk.jpg',
                    'Handmade Patchwork Hippo Plushie': 'https://res.cloudinary.com/dgtud2toy/image/upload/v1763014118/img2_g01qu2.jpg',
                    'Cute Patchwork Cushion Pillow': 'https://res.cloudinary.com/dgtud2toy/image/upload/v1763014124/img3_bssdv3.jpg',
                    'Upcycled Denim Patchwork Tote Bag': 'https://res.cloudinary.com/dgtud2toy/image/upload/v1763014132/img4_rgsaky.jpg',
                    'Vintage-Style Patchwork Maxi Skirt': 'https://res.cloudinary.com/dgtud2toy/image/upload/v1763014139/img5_mbbwdg.jpg',
                    'Personalized Patchwork Memory Blanket': 'https://res.cloudinary.com/dgtud2toy/image/upload/v1763014149/img6_r0acom.jpg',
                    'Custom T-Shirt Memory Quilt': 'https://res.cloudinary.com/dgtud2toy/image/upload/v1763014156/img7_pb7hc1.jpg',
                    'Colorful Boho Patchwork Skirt': 'https://res.cloudinary.com/dgtud2toy/image/upload/v1763014194/img8_juan8g.jpg',
                    'Geometric Patchwork Tote Bag': 'https://res.cloudinary.com/dgtud2toy/image/upload/v1763014199/img9_owpqs5.jpg',
                    'Quilt-Patch Denim Jacket with Embroidered Accents': 'https://res.cloudinary.com/dgtud2toy/image/upload/v1763014204/img10_owsh0x.jpg'
                }
                
                if product.title in image_map:
                    product.images = json.dumps([image_map[product.title]])
                    print(f"Fixed image for {product.title}")
        
        db.session.commit()
        print("\n=== AFTER FIX ===")
        
        for product in products:
            images = product.get_images()
            print(f"{product.title}: {images[0] if images else 'NO IMAGE'}")

if __name__ == '__main__':
    debug_images()