import os
import uuid
from PIL import Image
from flask import current_app
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_uploaded_file(file, folder='general'):
    """Save uploaded file and return filename"""
    if not file or not allowed_file(file.filename):
        return None
        
    try:
        # Sanitize folder name to prevent path traversal
        folder = secure_filename(folder) or 'general'
        
        # Generate unique filename
        filename = secure_filename(file.filename)
        if not filename:
            return None
            
        name, ext = os.path.splitext(filename)
        unique_filename = f"{name}_{uuid.uuid4().hex[:8]}{ext}"
        
        # Validate upload folder exists and is within allowed directory
        base_upload_path = os.path.abspath(current_app.config['UPLOAD_FOLDER'])
        upload_path = os.path.abspath(os.path.join(base_upload_path, folder))
        
        # Prevent path traversal
        if not upload_path.startswith(base_upload_path):
            return None
            
        os.makedirs(upload_path, exist_ok=True)
        
        # Save file
        file_path = os.path.join(upload_path, unique_filename)
        file.save(file_path)
        
        # Resize image if it's too large
        try:
            with Image.open(file_path) as img:
                if img.width > 1200 or img.height > 1200:
                    img.thumbnail((1200, 1200), Image.Resampling.LANCZOS)
                    img.save(file_path, optimize=True, quality=85)
        except Exception as e:
            current_app.logger.error(f"Image processing failed: {e}")
            # Delete the file if processing failed
            try:
                os.remove(file_path)
            except:
                pass
            return None
        
        return os.path.join(folder, unique_filename)
        
    except Exception as e:
        current_app.logger.error(f"File upload failed: {e}")
        return None

def delete_file(filepath):
    """Delete uploaded file"""
    try:
        # Prevent path traversal
        base_upload_path = os.path.abspath(current_app.config['UPLOAD_FOLDER'])
        full_path = os.path.abspath(os.path.join(base_upload_path, filepath))
        
        # Ensure file is within upload directory
        if not full_path.startswith(base_upload_path):
            current_app.logger.warning(f"Attempted path traversal: {filepath}")
            return False
            
        if os.path.exists(full_path) and os.path.isfile(full_path):
            os.remove(full_path)
            return True
    except Exception as e:
        current_app.logger.error(f"File deletion failed: {e}")
    return False

def format_currency(amount):
    """Format amount as Indian currency"""
    return f"₹{amount:,.2f}"

def generate_slug(title):
    """Generate URL-friendly slug from title"""
    import re
    slug = title.lower()
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = re.sub(r'\s+', '-', slug)
    slug = slug.strip('-')
    return slug