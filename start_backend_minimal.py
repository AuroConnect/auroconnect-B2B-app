#!/usr/bin/env python3
"""
Start Flask backend connecting to EC2 MySQL database (Minimal version)
"""

import os
import sys
from pathlib import Path

# Add the server directory to Python path
server_dir = Path(__file__).parent / "server"
sys.path.insert(0, str(server_dir))

# Set environment variables for EC2 MySQL connection
os.environ['DATABASE_URL'] = 'mysql+pymysql://admin:123%40Hrushi@3.249.132.231:3306/wa'
os.environ['FLASK_ENV'] = 'development'
os.environ['SECRET_KEY'] = 'auromart-secret-key-2024-super-secure'
os.environ['JWT_SECRET_KEY'] = 'auromart-jwt-secret-key-2024-super-secure'
os.environ['REDIS_URL'] = 'redis://localhost:6379'

def main():
    """Main function to start the backend"""
    print("🚀 Starting AuroMart Backend...")
    print("📊 Connecting to MySQL database on EC2 (3.249.132.231)...")
    
    try:
        # Import Flask and create a simple app
        from flask import Flask, jsonify
        from flask_cors import CORS
        from flask_sqlalchemy import SQLAlchemy
        
        # Create a simple Flask app
        app = Flask(__name__)
        
        # Configure database
        app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        app.config['SECRET_KEY'] = os.environ['SECRET_KEY']
        
        # Initialize extensions
        db = SQLAlchemy(app)
        CORS(app)
        
        # Simple health endpoint
        @app.route('/api/health', methods=['GET'])
        def health_check():
            try:
                # Test database connection
                db.session.execute(db.text('SELECT 1'))
                return jsonify({
                    'status': 'healthy',
                    'database': 'connected',
                    'message': 'AuroMart API is running successfully'
                }), 200
            except Exception as e:
                return jsonify({
                    'status': 'unhealthy',
                    'database': 'disconnected',
                    'error': str(e)
                }), 500
        
        # Root endpoint
        @app.route('/', methods=['GET'])
        def root():
            return jsonify({
                'message': 'AuroMart B2B Platform API',
                'status': 'running'
            }), 200
        
        # Registration endpoint
        @app.route('/api/auth/register', methods=['POST'])
        def register():
            try:
                from flask import request
                import hashlib
                import uuid
                from datetime import datetime
                
                data = request.get_json()
                
                # Validate required fields
                required_fields = ['email', 'password', 'first_name', 'last_name', 'role']
                for field in required_fields:
                    if not data.get(field):
                        return jsonify({'error': f'Missing required field: {field}'}), 400
                
                # Check if user already exists
                existing_user = db.session.execute(
                    db.text("SELECT id FROM users WHERE email = :email"),
                    {"email": data['email']}
                ).fetchone()
                
                if existing_user:
                    return jsonify({'error': 'User with this email already exists'}), 409
                
                # Hash password
                password_hash = hashlib.sha256(data['password'].encode()).hexdigest()
                
                # Create user
                user_id = str(uuid.uuid4())
                now = datetime.utcnow()
                
                db.session.execute(
                    db.text("""
                        INSERT INTO users (id, email, password_hash, first_name, last_name, 
                        role, business_name, address, phone_number, created_at, updated_at)
                        VALUES (:id, :email, :password_hash, :first_name, :last_name, 
                        :role, :business_name, :address, :phone_number, :created_at, :updated_at)
                    """),
                    {
                        "id": user_id,
                        "email": data['email'],
                        "password_hash": password_hash,
                        "first_name": data['first_name'],
                        "last_name": data['last_name'],
                        "role": data['role'],
                        "business_name": data.get('business_name', ''),
                        "address": data.get('address', ''),
                        "phone_number": data.get('phone_number', ''),
                        "created_at": now,
                        "updated_at": now
                    }
                )
                
                db.session.commit()
                
                return jsonify({
                    'message': 'User registered successfully',
                    'user_id': user_id
                }), 201
                
            except Exception as e:
                db.session.rollback()
                print(f"Registration error: {e}")
                return jsonify({'error': 'Server error occurred. Please try again later.'}), 500
        
        # Login endpoint
        @app.route('/api/auth/login', methods=['POST'])
        def login():
            try:
                from flask import request
                import hashlib
                import jwt
                import datetime
                
                data = request.get_json()
                
                if not data.get('email') or not data.get('password'):
                    return jsonify({'error': 'Email and password are required'}), 400
                
                # Hash password
                password_hash = hashlib.sha256(data['password'].encode()).hexdigest()
                
                # Find user
                user = db.session.execute(
                    db.text("SELECT * FROM users WHERE email = :email AND password_hash = :password_hash"),
                    {"email": data['email'], "password_hash": password_hash}
                ).fetchone()
                
                if not user:
                    return jsonify({'error': 'Invalid email or password'}), 401
                
                # Generate JWT token
                token = jwt.encode(
                    {
                        'user_id': user.id,
                        'email': user.email,
                        'role': user.role,
                        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
                    },
                    os.environ['SECRET_KEY'],
                    algorithm='HS256'
                )
                
                return jsonify({
                    'message': 'Login successful',
                    'token': token,
                    'user': {
                        'id': user.id,
                        'email': user.email,
                        'first_name': user.first_name,
                        'last_name': user.last_name,
                        'role': user.role
                    }
                }), 200
                
            except Exception as e:
                print(f"Login error: {e}")
                return jsonify({'error': 'Server error occurred. Please try again later.'}), 500
        
        print("🌐 Starting Flask server on http://localhost:5000")
        print("📱 Frontend will be available on http://localhost:3000")
        print("🔗 API endpoints available at http://localhost:5000/api")
        
        # Start the Flask server
        app.run(
            host='0.0.0.0',
            port=5000,
            debug=True,
            use_reloader=False
        )
        
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("💡 Please install dependencies: pip install PyMySQL cryptography")
    except Exception as e:
        print(f"❌ Error starting backend: {e}")
        print("💡 Make sure your EC2 MySQL server is accessible")

if __name__ == "__main__":
    main()
