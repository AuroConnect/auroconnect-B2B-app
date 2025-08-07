from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from app.config import Config

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()

def create_app(config_class=Config):
    """Application factory pattern"""
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config_class)
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    
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
    from app.api.v1.partnerships import partnerships_bp
    from app.api.v1.favorites import favorites_bp
    from app.api.v1.search import search_bp
    from app.api.v1.health import health_bp
    from app.api.v1.analytics import analytics_bp
    from app.api.v1.notifications import notifications_bp
    from app.api.v1.whatsapp import whatsapp_bp
    from app.api.v1.invoices import invoices_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(products_bp, url_prefix='/api/products')
    app.register_blueprint(orders_bp, url_prefix='/api/orders')
    app.register_blueprint(partners_bp, url_prefix='/api/partners')
    app.register_blueprint(partnerships_bp, url_prefix='/api/partnerships')
    app.register_blueprint(favorites_bp, url_prefix='/api/favorites')
    app.register_blueprint(search_bp, url_prefix='/api/search')
    app.register_blueprint(health_bp, url_prefix='/api')
    app.register_blueprint(analytics_bp, url_prefix='/api/analytics')
    app.register_blueprint(notifications_bp, url_prefix='/api/notifications')
    app.register_blueprint(whatsapp_bp, url_prefix='/api/whatsapp')
    app.register_blueprint(invoices_bp, url_prefix='/api/invoices')
    
    # Error handlers
    from app.errors import register_error_handlers
    register_error_handlers(app)
    
    # CLI commands
    from app.cli import register_commands
    register_commands(app)
    
    return app 