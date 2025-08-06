from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
import os
from datetime import timedelta

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()

def create_app(config_name=None):
    """Application factory pattern"""
    app = Flask(__name__)
    
    # Load configuration
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    if config_name == 'production':
        app.config.from_object('app.config.ProductionConfig')
    elif config_name == 'testing':
        app.config.from_object('app.config.TestingConfig')
    else:
        app.config.from_object('app.config.DevelopmentConfig')
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    
    # Setup CORS
    CORS(app, resources={
        r"/api/*": {
            "origins": app.config.get('CORS_ORIGINS', ['http://localhost:3000', 'http://localhost:3001', 'http://localhost:80']),
            "methods": ["GET", "POST", "PUT", "DELETE", "PATCH"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })
    
    # Register blueprints
    from app.api.v1.auth import auth_bp
    from app.api.v1.partners import partners_bp
    from app.api.v1.products import products_bp
    from app.api.v1.orders import orders_bp
    from app.api.v1.favorites import favorites_bp
    from app.api.v1.partnerships import partnerships_bp
    from app.api.v1.search import search_bp
    from app.api.v1.health import health_bp
    from app.api.v1.analytics import analytics_bp
    from app.api.v1.notifications import notifications_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(partners_bp, url_prefix='/api/partners')
    app.register_blueprint(products_bp, url_prefix='/api/products')
    app.register_blueprint(orders_bp, url_prefix='/api/orders')
    app.register_blueprint(favorites_bp, url_prefix='/api/favorites')
    app.register_blueprint(partnerships_bp, url_prefix='/api/partnerships')
    app.register_blueprint(search_bp, url_prefix='/api/search')
    app.register_blueprint(health_bp, url_prefix='/api')
    app.register_blueprint(analytics_bp, url_prefix='/api/analytics')
    app.register_blueprint(notifications_bp, url_prefix='/api/notifications')
    
    # Error handlers
    from app.errors import register_error_handlers
    register_error_handlers(app)
    
    # CLI commands
    from app.cli import register_commands
    register_commands(app)
    
    return app 