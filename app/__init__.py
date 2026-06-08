"""
Hospital Token System - Flask Application Factory
Initialize and configure the Flask application with all extensions and blueprints
"""

from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv
import os
from app.models.database import db_init

# Load environment variables from .env file
load_dotenv()


def create_app():
    """
    Application factory function to create and configure Flask app
    Returns:
        Flask: Configured Flask application instance
    """
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # Enable CORS for all routes
    CORS(app)
    
    # Register blueprints
    from app.routes.main import main_bp
    from app.routes.auth import auth_bp
    from app.routes.token import token_bp
    from app.routes.admin import admin_bp
    from app.utils.auth import get_current_admin_info, get_current_user_info
    
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(token_bp, url_prefix='/token')
    app.register_blueprint(admin_bp, url_prefix='/admin')

    @app.context_processor
    def inject_user_and_admin():
        return {
            'user': get_current_user_info(),
            'admin': get_current_admin_info()
        }

    with app.app_context():
        db_init()
    
    return app
