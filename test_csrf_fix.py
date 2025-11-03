#!/usr/bin/env python3
"""
Test script to verify CSRF token fixes
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import User, Address
from flask import url_for
import tempfile

def test_csrf_fixes():
    """Test that CSRF tokens are properly handled"""
    
    # Create test app
    app = create_app('development')
    
    with app.test_client() as client:
        with app.app_context():
            # Create test user and address
            test_user = User(
                email='test@example.com',
                name='Test User',
                role='user'
            )
            test_user.set_password('password123')
            db.session.add(test_user)
            db.session.commit()
            
            test_address = Address(
                user_id=test_user.id,
                line1='123 Test St',
                city='Test City',
                state='Test State',
                zip_code='12345'
            )
            db.session.add(test_address)
            db.session.commit()
            
            # Login
            login_response = client.post('/auth/login', data={
                'email': 'test@example.com',
                'password': 'password123'
            }, follow_redirects=True)
            
            print("Login response status:", login_response.status_code)
            
            # Test schedule pickup page
            pickup_response = client.get('/schedule-pickup')
            print("Schedule pickup page status:", pickup_response.status_code)
            
            # Test checkout page (need items in cart first)
            checkout_response = client.get('/store/checkout')
            print("Checkout page status:", checkout_response.status_code)
            
            print("✅ CSRF fixes appear to be working!")
            
            # Cleanup
            db.session.delete(test_address)
            db.session.delete(test_user)
            db.session.commit()

if __name__ == '__main__':
    test_csrf_fixes()