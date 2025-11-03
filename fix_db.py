#!/usr/bin/env python3

from app import create_app, db
from app.models import *
import os

def fix_database():
    app = create_app()
    
    with app.app_context():
        try:
            # Drop all tables and recreate
            db.drop_all()
            db.create_all()
            
            print("Database tables recreated successfully!")
            
            # Run seed script
            from seed import seed_database
            seed_database()
            
        except Exception as e:
            print(f"Error fixing database: {e}")

if __name__ == '__main__':
    fix_database()