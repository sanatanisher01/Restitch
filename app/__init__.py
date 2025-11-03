from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_mail import Mail
from flask_wtf.csrf import CSRFProtect
from flask_socketio import SocketIO
from config import config
import os

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
mail = Mail()
csrf = CSRFProtect()
socketio = SocketIO()

def create_app(config_name=None):
    app = Flask(__name__)
    
    if config_name is None:
        config_name = os.environ.get('FLASK_CONFIG', 'default')
    
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    mail.init_app(app)
    csrf.init_app(app)
    socketio.init_app(app, cors_allowed_origins="*")
    
    # Login manager settings
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'
    
    # Register blueprints
    from app.main import bp as main_bp
    app.register_blueprint(main_bp)
    
    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')
    
    from app.admin import bp as admin_bp
    app.register_blueprint(admin_bp, url_prefix='/admin')
    
    from app.store import bp as store_bp
    app.register_blueprint(store_bp, url_prefix='/store')
    
    from app.api import bp as api_bp
    app.register_blueprint(api_bp, url_prefix='/api')
    
    from app.designer import bp as designer_bp
    app.register_blueprint(designer_bp, url_prefix='/designer')
    
    # Register mobile API
    register_mobile_api(app)
    
    # Register error handlers
    try:
        from app.errors import register_error_handlers
        register_error_handlers(app)
    except ImportError:
        pass
    
    # Create upload directory
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    return app

from app import models
try:
    from app.socketio_events import *
except ImportError:
    pass
try:
    from app.api_mobile import register_mobile_api
except ImportError:
    def register_mobile_api(app):
        pass