#!/usr/bin/env python3
"""
Production migration script for ReStitch
Run this script to set up the database in production
"""

import os
import sys
from flask_migrate import upgrade
from app import create_app, db
from app.models import User

def run_migrations():
    """Run database migrations"""
    app = create_app()
    
    with app.app_context():
        try:
            print("Running database migrations...")
            upgrade()
            print("✓ Migrations completed successfully")
            
            # Check if database needs seeding
            user_count = User.query.count()
            if user_count == 0:
                print("Database is empty, running seed script...")
                from seed import seed_database
                seed_database()
                print("✓ Database seeded successfully")
            else:
                print(f"✓ Database already has {user_count} users")
                
        except Exception as e:
            print(f"✗ Error during migration: {e}")
            sys.exit(1)

if __name__ == '__main__':
    run_migrations()