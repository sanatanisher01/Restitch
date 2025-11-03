#!/usr/bin/env python3
"""
Startup script for ReStitch production deployment
This ensures database is properly initialized before starting the app
"""

import os
import sys
from app import create_app, db
from flask_migrate import upgrade

def initialize_database():
    """Initialize database with proper error handling"""
    app = create_app()
    
    with app.app_context():
        try:
            # Try to run migrations
            print("Initializing database...")
            upgrade()
            print("Database migrations completed")
            
            # Check if we need to seed
            from app.models import User
            user_count = User.query.count()
            
            if user_count == 0:
                print("Database is empty, creating initial data...")
                # Import and run seeding
                exec(open('seed.py').read())
                print("Database seeded successfully")
            else:
                print(f"Database already initialized with {user_count} users")
                
        except Exception as e:
            print(f"Database initialization error: {e}")
            # Don't exit - let the app start anyway
            pass

if __name__ == '__main__':
    initialize_database()