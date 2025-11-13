#!/usr/bin/env python3
"""
Production setup script - runs migrations and rebuilds store
"""

import os
import sys
from app import create_app, db
from flask_migrate import upgrade

def setup_production():
    print("=== PRODUCTION SETUP START ===")
    
    app = create_app()
    
    with app.app_context():
        try:
            # Run migrations first
            print("Running database migrations...")
            upgrade()
            print("Migrations completed")
            
            # Now rebuild store
            print("Rebuilding store...")
            exec(open('rebuild_store.py').read())
            
        except Exception as e:
            print(f"Setup error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    setup_production()