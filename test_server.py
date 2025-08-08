#!/usr/bin/env python3
"""
Minimal test server for authentication endpoints
"""
import sys
import os
from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_jwt_extended import JWTManager

# Add server directory to path
server_path = os.path.join(os.path.dirname(__file__), 'server')
sys.path.insert(0, server_path)

# Import the app's database instance
from server.app import db, login_manager, migrate
from server.app.config import Config

def create_test_app():
    """Create a minimal test app with just auth endpoints"""
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(Config)
    
    # Initialize extensions with the app
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    
    # Setup CORS
    CORS(app, 
         origins=app.config['CORS_ORIGINS'],
         supports_credentials=True,
         methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
         allow_headers=['Content-Type', 'Authorization', 'X-Requested-With'],
         expose_headers=['Content-Type', 'Authorization'])
    
    # Register auth blueprint
    from server.app.api.v1.auth import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    
    return app

if __name__ == "__main__":
    app = create_test_app()
    app.run(host='0.0.0.0', port=5000, debug=True)