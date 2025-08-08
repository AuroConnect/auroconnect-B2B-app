#!/usr/bin/env python3
"""
Minimal Flask backend for testing auth without pandas dependency
"""
import os
import sys
from pathlib import Path

# Add the server directory to Python path
server_dir = Path(__file__).parent / "server"
sys.path.insert(0, str(server_dir))

# Set environment variables for MySQL connection
# URL encode the password to handle special characters like '@'
os.environ['DATABASE_URL'] = 'mysql+pymysql://admin:123%40Hrushi@3.249.132.231:3306/wa'
os.environ['FLASK_ENV'] = 'development'
os.environ['SECRET_KEY'] = 'auromart-secret-key-2024-super-secure'
os.environ['JWT_SECRET_KEY'] = 'auromart-jwt-secret-key-2024-super-secure'

# Mock pandas to avoid import issues
class MockPandas:
    pass

# Add mock to sys.modules before importing app
sys.modules['pandas'] = MockPandas()

try:
    from app import create_app, db
    from app.models.user import User
    
    def init_database():
        """Initialize the database with tables"""
        print("Initializing database tables...")
        
        try:
            # Create Flask app
            app = create_app()
            
            with app.app_context():
                # Create all tables
                db.create_all()
                print("Database tables created successfully!")
                return True
                
        except Exception as e:
            print(f"Database initialization failed: {e}")
            return False
    
    def main():
        """Main function to start the backend"""
        print("Starting minimal AuroMart Backend...")
        print("Connecting to MySQL database on EC2...")
        
        # Initialize database
        if init_database():
            print("Database ready!")
        else:
            print("Database initialization failed, but continuing...")
        
        # Create and run Flask app
        app = create_app()
        
        print("Starting Flask server on http://localhost:5000")
        
        app.run(
            host='0.0.0.0',
            port=5000,
            debug=True
        )
    
    if __name__ == "__main__":
        main()
        
except ImportError as e:
    print(f"Import error: {e}")
    print("Trying alternative approach...")
    
    # Alternative approach without pandas dependency
    import pymysql
    from flask import Flask, request, jsonify
    from werkzeug.security import generate_password_hash, check_password_hash
    import uuid
    from datetime import datetime
    
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'auromart-secret-key-2024-super-secure'
    
    # Database configuration
    DB_CONFIG = {
        'host': '3.249.132.231',
        'port': 3306,
        'user': 'admin',
        'password': '123@Hrushi',
        'database': 'wa'
    }
    
    def get_db_connection():
        """Get database connection"""
        return pymysql.connect(**DB_CONFIG)
    
    @app.route('/api/auth/register', methods=['POST'])
    def register():
        """Register a new user"""
        try:
            data = request.get_json()
            if not data:
                return jsonify({'message': 'No data provided'}), 400
            
            # Validate required fields
            required_fields = ['firstName', 'lastName', 'email', 'password', 'role']
            for field in required_fields:
                if not data.get(field):
                    return jsonify({'message': f'{field} is required'}), 400
            
            # Connect to database
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Check if user already exists
            cursor.execute("SELECT id FROM users WHERE email = %s", (data['email'],))
            if cursor.fetchone():
                cursor.close()
                conn.close()
                return jsonify({'message': 'User with this email already exists'}), 409
            
            # Create new user
            user_id = str(uuid.uuid4())
            name = f"{data['firstName']} {data['lastName']}"
            password_hash = generate_password_hash(data['password'])
            role = data['role']
            business_name = data.get('businessName')
            address = data.get('address')
            phone_number = data.get('phoneNumber') or data.get('whatsappNumber')
            
            # Insert user
            cursor.execute("""
                INSERT INTO users (id, name, email, password_hash, role, business_name, address, phone_number, is_active, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (user_id, name, data['email'], password_hash, role, business_name, address, phone_number, True, datetime.now(), datetime.now()))
            
            conn.commit()
            cursor.close()
            conn.close()
            
            return jsonify({
                'message': 'Registration successful',
                'user': {
                    'id': user_id,
                    'name': name,
                    'email': data['email'],
                    'role': role,
                    'businessName': business_name,
                    'address': address,
                    'phoneNumber': phone_number,
                    'isActive': True
                }
            }), 201
            
        except Exception as e:
            return jsonify({'message': 'Registration failed', 'error': str(e)}), 500
    
    @app.route('/api/auth/login', methods=['POST'])
    def login():
        """Login user"""
        try:
            data = request.get_json()
            if not data:
                return jsonify({'message': 'No data provided'}), 400
                
            email = data.get('email')
            password = data.get('password')
            
            if not email or not password:
                return jsonify({'message': 'Email and password are required'}), 400
            
            # Connect to database
            conn = get_db_connection()
            cursor = conn.cursor(pymysql.cursors.DictCursor)
            
            # Find user
            cursor.execute("SELECT * FROM users WHERE email = %s AND is_active = 1", (email,))
            user = cursor.fetchone()
            
            if not user or not check_password_hash(user['password_hash'], password):
                cursor.close()
                conn.close()
                return jsonify({'message': 'Invalid email or password'}), 401
            
            cursor.close()
            conn.close()
            
            return jsonify({
                'message': 'Login successful',
                'user': {
                    'id': user['id'],
                    'name': user['name'],
                    'email': user['email'],
                    'role': user['role'],
                    'businessName': user['business_name'],
                    'address': user['address'],
                    'phoneNumber': user['phone_number'],
                    'isActive': user['is_active']
                }
            }), 200
            
        except Exception as e:
            return jsonify({'message': 'Login failed', 'error': str(e)}), 500
    
    @app.route('/')
    def home():
        return "Minimal AuroMart Backend is running!"
    
    if __name__ == "__main__":
        print("Starting minimal backend on http://localhost:5000")
        app.run(host='0.0.0.0', port=5000, debug=True)