from flask import current_app
import razorpay
import hashlib
import hmac

def create_payment_order(amount):
    """Create a Razorpay payment order"""
    if not current_app.config.get('RAZORPAY_KEY_ID'):
        # Return mock order for development
        return {
            'id': f'order_mock_{int(amount)}',
            'amount': int(amount * 100),  # Convert to paise
            'currency': 'INR'
        }
    
    try:
        client = razorpay.Client(
            auth=(current_app.config['RAZORPAY_KEY_ID'], 
                  current_app.config['RAZORPAY_KEY_SECRET'])
        )
        
        order_data = {
            'amount': int(amount * 100),  # Convert to paise
            'currency': 'INR',
            'payment_capture': 1
        }
        
        order = client.order.create(data=order_data)
        return order
    except Exception as e:
        print(f"Payment order creation failed: {e}")
        return None

def verify_payment_signature(payment_id, order_id, signature):
    """Verify Razorpay payment signature"""
    if not current_app.config.get('RAZORPAY_KEY_SECRET'):
        return True  # Mock verification for development
    
    try:
        key_secret = current_app.config['RAZORPAY_KEY_SECRET']
        message = f"{order_id}|{payment_id}"
        
        generated_signature = hmac.new(
            key_secret.encode(),
            message.encode(),
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(generated_signature, signature)
    except Exception as e:
        print(f"Payment verification failed: {e}")
        return False

def process_payment(user_id, cart_items, payment_data):
    """Process payment and update database"""
    try:
        # Verify payment signature
        if not verify_payment_signature(
            payment_data['payment_id'],
            payment_data['order_id'],
            payment_data['signature']
        ):
            return False, "Payment verification failed"
        
        # In a real implementation, you would:
        # 1. Create transaction records
        # 2. Update product stock
        # 3. Award points to user
        # 4. Send confirmation email
        
        return True, "Payment processed successfully"
    except Exception as e:
        print(f"Payment processing failed: {e}")
        return False, "Payment processing failed"