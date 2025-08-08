#!/usr/bin/env python3
"""
Minimal test server for authentication endpoints
"""
import sys
import os
from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager

# Add server directory to path
server_path = os.path.join(os.path.dirname(__file__), 'server')
sys.path.insert(0, server_path)

# Create new database instance for this test server
db = SQLAlchemy()

def create_test_app():
    """Create a minimal test app with just auth endpoints"""
    app = Flask(__name__)
    
    # Load configuration with SQLite for testing
    app.config['SECRET_KEY'] = 'test-secret-key'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = 'test-jwt-secret'
    
    # Initialize extensions with the app
    db.init_app(app)
    
    # Setup JWT
    jwt = JWTManager(app)
    
    # Setup CORS
    CORS(app, 
         origins=['*'],
         supports_credentials=True,
         methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
         allow_headers=['Content-Type', 'Authorization', 'X-Requested-With'],
         expose_headers=['Content-Type', 'Authorization'])
    
    # Create tables
    with app.app_context():
        # Import models after db is initialized
        from server.app.models.user import User
        db.create_all()
    
    # Register auth blueprint
    from server.app.api.v1.auth import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    
    return app

if __name__ == "__main__":
    app = create_test_app()
    app.run(host='0.0.0.0', port=5000, debug=True)