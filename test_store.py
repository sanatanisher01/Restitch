#!/usr/bin/env python3

from app import create_app, db
from app.models import Product, User

def test_store_functionality():
    app = create_app()
    
    with app.app_context():
        # Check if products exist
        products = Product.query.all()
        print(f"Total products in database: {len(products)}")
        
        if products:
            for product in products[:3]:
                print(f"- {product.title} (Rs.{product.price}) - Stock: {product.stock}")
        else:
            print("No products found! Run seed.py first.")
            return
        
        # Check if users exist
        users = User.query.all()
        print(f"\nTotal users in database: {len(users)}")
        
        # Test URL generation
        with app.test_request_context():
            from flask import url_for
            
            try:
                store_index = url_for('store.index')
                print(f"\nStore index URL: {store_index}")
                
                if products:
                    product_detail = url_for('store.product_detail', slug=products[0].slug)
                    print(f"Product detail URL: {product_detail}")
                    
                    add_to_cart = url_for('store.add_to_cart', product_id=products[0].id)
                    print(f"Add to cart URL: {add_to_cart}")
                
            except Exception as e:
                print(f"URL generation error: {e}")

if __name__ == '__main__':
    test_store_functionality()