import os
import datetime
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
bcrypt = Bcrypt()

def create_app(config_class=None):
    app = Flask(__name__)
    
    # Config from environment variables
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-key-for-testing')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///ytsp.db') # if enironment variable is not set, default to local sqlite db
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # turn off to improve performance
    
    # Initialize extensions with app
    db.init_app(app) # connect database instance to flask app
    migrate.init_app(app, db) 
    login_manager.init_app(app)
    bcrypt.init_app(app)
    
    # Configure login
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'info'
    
    # Add context processor to provide 'now' to all templates
    @app.context_processor
    def inject_now():
        return {'now': datetime.datetime.now()}
    
    # Import and register blueprints
    from app.controllers.auth import auth_bp
    from app.controllers.main import main_bp
    from app.controllers.trading import trading_bp
    from app.controllers.social import social_bp
    from app.api.stock_api import stock_api_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(trading_bp)
    app.register_blueprint(social_bp)
    app.register_blueprint(stock_api_bp, url_prefix='/api')
    
    # Create database tables when app is created
    with app.app_context():
        db.create_all()
    
    return app 