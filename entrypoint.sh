#!/bin/bash

# Wait for database to be ready
echo "Waiting for database..."
sleep 5

# Run database migrations
echo "Running database migrations..."
flask db upgrade

# Check if we need to seed the database
echo "Checking if database needs seeding..."
python -c "
from app import create_app, db
from app.models import User
import sys
app = create_app()
with app.app_context():
    try:
        user_count = User.query.count()
        if user_count == 0:
            print('Database is empty, needs seeding')
            sys.exit(1)
        else:
            print(f'Database has {user_count} users, no seeding needed')
            sys.exit(0)
    except Exception as e:
        print(f'Error checking database: {e}')
        sys.exit(1)
"

# If exit code is 1, run seeding
if [ $? -eq 1 ]; then
    echo "Seeding database..."
    python seed.py
fi

echo "Starting application..."
exec "$@"