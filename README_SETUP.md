# ReStitch - Quick Setup Guide

## One-Click Setup (Windows)

Simply double-click `start.bat` and the application will automatically:
1. Check Python installation
2. Install all dependencies
3. Set up the database with sample data
4. Start the web server

## Manual Setup

If you prefer manual setup:

```bash
# Install dependencies
pip install -r requirements.txt

# Setup database
python seed.py

# Start application
python restitch.py
```

## Access the Application

- **URL**: http://localhost:5000
- **Admin**: admin@restitch.com / admin123
- **User**: priya@example.com / password123

## Team

- **CEO & Founder**: Saloni Gupta
- **Operation Head**: Ayushi Gupta  
- **Design Head**: Urvashi Chaudhary
- **Marketing Head**: Natasha
- **Sales Head**: Smriti Dawra

## Requirements

- Python 3.10+
- Windows (for .bat file) or any OS for manual setup