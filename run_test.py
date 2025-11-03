#!/usr/bin/env python3

from app import create_app
import os

if __name__ == '__main__':
    # Set environment variables
    os.environ['FLASK_ENV'] = 'development'
    os.environ['FLASK_DEBUG'] = '1'
    
    app = create_app()
    
    print("Starting Flask app...")
    print("Store routes available:")
    
    with app.app_context():
        for rule in app.url_map.iter_rules():
            if 'store' in rule.rule:
                print(f"  {rule.rule} -> {rule.endpoint}")
    
    print("\nAccess the store at: http://localhost:5000/store/")
    print("Press Ctrl+C to stop")
    
    app.run(host='0.0.0.0', port=5000, debug=True)