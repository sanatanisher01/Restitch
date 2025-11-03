from functools import wraps
from flask import request, abort, current_app
from flask_wtf.csrf import validate_csrf, ValidationError
import logging

def csrf_required(f):
    """Decorator to require CSRF token validation"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if request.method == 'POST':
            try:
                validate_csrf(request.form.get('csrf_token'))
            except ValidationError:
                current_app.logger.warning(f"CSRF validation failed for {request.endpoint}")
                abort(400, "CSRF token missing or invalid")
        return f(*args, **kwargs)
    return decorated_function

def validate_file_upload(file):
    """Validate uploaded file for security"""
    if not file:
        return False, "No file provided"
    
    # Check file size
    if hasattr(file, 'content_length') and file.content_length > current_app.config.get('MAX_CONTENT_LENGTH', 16 * 1024 * 1024):
        return False, "File too large"
    
    # Check file extension
    allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'doc', 'docx'}
    if '.' not in file.filename or file.filename.rsplit('.', 1)[1].lower() not in allowed_extensions:
        return False, "File type not allowed"
    
    return True, "Valid file"

def sanitize_input(text):
    """Basic input sanitization"""
    if not text:
        return ""
    
    # Remove potential XSS characters
    import html
    return html.escape(str(text).strip())

def log_security_event(event_type, details):
    """Log security-related events"""
    current_app.logger.warning(f"Security Event - {event_type}: {details}")