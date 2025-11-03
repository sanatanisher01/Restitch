#!/bin/bash

# Database migration and seeding script for production deployment

echo "Starting deployment process..."

# Run database migrations
echo "Running database migrations..."
flask db upgrade

# Check if database is empty (no users exist)
python -c "
from app import create_app, db
from app.models import User
app = create_app()
with app.app_context():
    user_count = User.query.count()
    if user_count == 0:
        print('Database is empty, running seed script...')
        import subprocess
        subprocess.run(['python', 'seed.py'])
    else:
        print(f'Database already has {user_count} users, skipping seed.')
"

echo "Deployment process completed!"