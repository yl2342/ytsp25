"""
Initialize the Flask application and configure all necessary extensions.
This is the main entry point for the Yale Trading Simulation Platform.
"""
import os
import datetime
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_cas import CAS
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize Flask extensions
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
bcrypt = Bcrypt()
cas = CAS()

def create_app(config_class=None):
    """
    Application factory function that creates and configures the Flask app.
    
    Args:
        config_class: Optional configuration class to use instead of environment variables
        
    Returns:
        A configured Flask application instance
    """
    app = Flask(__name__)
    
    # Configure app from environment variables
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-key-for-testing')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'postgresql://ytsp_server:cpsc519sp25@localhost:5432/ytsp')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Disable to improve performance
    
    # Basic CAS configuration - use simpler, minimal config
    app.config['CAS_SERVER'] = 'https://secure6.its.yale.edu/cas'
    app.config['CAS_AFTER_LOGIN'] = 'main.dashboard'
    app.config['CAS_VALIDATE_CERT'] = False  # Set to True in production
    
    # Initialize extensions with the app
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    
    # Configure login settings
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'info'
    
    # Add context processor to provide 'now' to all templates
    @app.context_processor
    def inject_now():
        """Inject current datetime into all templates"""
        return {'now': datetime.datetime.now(datetime.timezone.utc)}
    
    # Import and register blueprints
    from app.controllers.auth import auth_bp
    from app.controllers.main import main_bp
    from app.controllers.trading import trading_bp
    from app.controllers.social import social_bp
    from app.api.stock_api import stock_api_bp
    from app.api.user_api import user_api_bp
    from app.api.ai_api import ai_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(trading_bp)
    app.register_blueprint(social_bp)
    app.register_blueprint(stock_api_bp, url_prefix='/api')
    app.register_blueprint(user_api_bp, url_prefix='/api')
    app.register_blueprint(ai_bp, url_prefix='/api/ai')
    
    # Create database tables when app is created
    with app.app_context():
        db.create_all()
        
    # Initialize CAS after blueprints are registered
    cas.init_app(app)
    
    return app 