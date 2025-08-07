from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from app.config import Config

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()

@login_manager.user_loader
def load_user(user_id):
    from app.models import User
    return User.query.get(user_id)

def create_app(config_class=Config):
    """Application factory pattern"""
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config_class)
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    
    # Setup CORS
    CORS(app, 
         origins=app.config['CORS_ORIGINS'],
         supports_credentials=True,
         methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
         allow_headers=['Content-Type', 'Authorization', 'X-Requested-With'],
         expose_headers=['Content-Type', 'Authorization'])
    
    # Register blueprints
    from app.api.v1.auth import auth_bp
    from app.api.v1.products import products_bp
    from app.api.v1.orders import orders_bp
    from app.api.v1.partners import partners_bp
    from app.api.v1.manufacturer import manufacturer_bp
    from app.api.v1.distributor import distributor_bp
    from app.api.v1.retailer import retailer_bp
    from app.api.v1.invoices import invoices_bp
    from app.api.v1.health import health_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(products_bp, url_prefix='/api/products')
    app.register_blueprint(orders_bp, url_prefix='/api/orders')
    app.register_blueprint(partners_bp, url_prefix='/api/partners')
    app.register_blueprint(manufacturer_bp, url_prefix='/api/manufacturer')
    app.register_blueprint(distributor_bp, url_prefix='/api/distributor')
    app.register_blueprint(retailer_bp, url_prefix='/api/retailer')
    app.register_blueprint(invoices_bp, url_prefix='/api/invoices')
    app.register_blueprint(health_bp, url_prefix='/api')
    
    # Error handlers
    from app.errors import register_error_handlers
    register_error_handlers(app)
    
    # CLI commands
    from app.cli import register_commands
    register_commands(app)
    
    return app 