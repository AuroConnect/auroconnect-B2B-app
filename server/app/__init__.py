from flask import Flask, request, make_response
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
    
    # Setup CORS with more specific configuration
    CORS(app, 
         origins=['http://localhost:3000', 'http://127.0.0.1:3000'],
         supports_credentials=True,
         methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
         allow_headers=['Content-Type', 'Authorization', 'X-Requested-With', 'Accept'],
         expose_headers=['Content-Type', 'Authorization'],
         max_age=3600,
         automatic_options=True)
    
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
    from app.api.v1.cart import cart_bp
    from app.api.v1.my_products import my_products_bp
    from app.api.v1.reports import reports_bp
    from app.api.v1.inventory import inventory_bp
    from app.api.v1.product_allocations import product_allocations_bp
    from app.api.v1.users import users_bp
    
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
    app.register_blueprint(cart_bp, url_prefix='/api/cart')
    app.register_blueprint(my_products_bp, url_prefix='/api/my-products')
    app.register_blueprint(reports_bp, url_prefix='/api/reports')
    app.register_blueprint(inventory_bp, url_prefix='/api/inventory')
    app.register_blueprint(product_allocations_bp, url_prefix='/api/product-allocations')
    app.register_blueprint(users_bp, url_prefix='/api/users')
    
    # Error handlers
    from app.errors import register_error_handlers
    register_error_handlers(app)
    
    # CLI commands
    from app.cli import register_commands
    register_commands(app)
    
    # Add CORS headers to all responses
    @app.before_request
    def add_cors_headers():
        if request.method == 'OPTIONS':
            response = make_response()
            response.status_code = 200
            response.headers['Access-Control-Allow-Origin'] = 'http://localhost:3000'
            response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
            response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Requested-With, Accept'
            response.headers['Access-Control-Allow-Credentials'] = 'true'
            response.headers['Access-Control-Max-Age'] = '3600'
            return response
    
    # Handle OPTIONS requests for CORS preflight
    @app.route('/api/<path:path>', methods=['OPTIONS'])
    def handle_options(path):
        from flask import make_response
        response = make_response()
        response.status_code = 200
        response.headers['Access-Control-Allow-Origin'] = 'http://localhost:3000'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Requested-With, Accept'
        response.headers['Access-Control-Allow-Credentials'] = 'true'
        response.headers['Access-Control-Max-Age'] = '3600'
        return response
    
    return app 