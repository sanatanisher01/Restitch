from app import create_app, db
from app.models import User, Address, PickupRequest, Order, Product, Transaction, ActivityLog, CityExpansion, DesignerApplication, StoreOrder, StoreOrderItem

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
        'CityExpansion': CityExpansion,
        'DesignerApplication': DesignerApplication,
        'StoreOrder': StoreOrder,
        'StoreOrderItem': StoreOrderItem
    }

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') != 'production'
    app.run(host='0.0.0.0', port=port, debug=debug)