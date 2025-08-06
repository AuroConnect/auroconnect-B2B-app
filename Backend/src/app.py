import os
from flask import Flask
from flask_login import LoginManager
from flask_migrate import Migrate
from config import config
from models import db

def create_app(config_name=None):
    """Application factory function"""
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'default')
    
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    
    # Initialize extensions
    db.init_app(app)
    migrate = Migrate(app, db)
    
    # Initialize Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    
    @login_manager.user_loader
    def load_user(user_id):
        from models.user import User
        return User.query.get(int(user_id))
    
    # Register blueprints
    from routes import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')
    
    from routes import manufacturer_bp
    app.register_blueprint(manufacturer_bp, url_prefix='/manufacturer')
    
    from routes import distributor_bp
    app.register_blueprint(distributor_bp, url_prefix='/distributor')
    
    from routes import retailer_bp
    app.register_blueprint(retailer_bp, url_prefix='/retailer')
    
    from routes import api_bp
    app.register_blueprint(api_bp, url_prefix='/api/v1')
    
    # Create upload directories if they don't exist
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['INVOICE_FOLDER'], exist_ok=True)
    os.makedirs(app.config['REPORT_FOLDER'], exist_ok=True)
    
    return app

# For running the application directly
if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)