#!/usr/bin/env python3
"""
Development server runner for ReStitch application.
Use this for local development only.
"""

from app import create_app, db
from app.models import User, Address, PickupRequest, Order, Product, Transaction, ActivityLog, CityExpansion

app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {
        'db': db,
        'User': User,
        'Address': Address,
        'PickupRequest': PickupRequest,
        'Order': Order,
        'Product': Product,
        'Transaction': Transaction,
        'ActivityLog': ActivityLog,
        'CityExpansion': CityExpansion
    }

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=5000)