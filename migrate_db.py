#!/usr/bin/env python3

from app import create_app, db
import sqlite3
import os

def migrate_database():
    app = create_app()
    
    with app.app_context():
        try:
            # Get database path
            db_path = app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
            
            # Connect to SQLite database
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Check if service_type column exists
            cursor.execute("PRAGMA table_info('order')")
            columns = [column[1] for column in cursor.fetchall()]
            
            if 'service_type' not in columns:
                print("Adding service_type column to order table...")
                cursor.execute("ALTER TABLE 'order' ADD COLUMN service_type VARCHAR(20) DEFAULT 'redesign'")
                conn.commit()
                print("Column added successfully!")
            else:
                print("service_type column already exists")
            
            conn.close()
            print("Database migration completed!")
            
        except Exception as e:
            print(f"Migration error: {e}")
            # If migration fails, recreate database
            print("Recreating database...")
            db.drop_all()
            db.create_all()
            
            # Run seed
            from seed import seed_database
            seed_database()

if __name__ == '__main__':
    migrate_database()