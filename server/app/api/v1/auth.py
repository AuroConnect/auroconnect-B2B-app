from flask import Blueprint, request, jsonify, redirect, url_for
from app import db
from app.models import User
from app.utils.decorators import validate_json
from app.utils.validators import UserSchema
from marshmallow import ValidationError
import uuid
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from flask_login import login_user

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new user"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'message': 'No data provided'}), 400
        
        # Log the incoming data for debugging
        print(f"Registration attempt for email: {data.get('email', 'N/A')}")
        
        # Validate required fields - updated to match frontend field names
        required_fields = ['firstName', 'lastName', 'email', 'password', 'role']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'message': f'{field} is required'}), 400
        
        # Validate role
        valid_roles = ['manufacturer', 'distributor', 'retailer']
        if data['role'] not in valid_roles:
            return jsonify({'message': f'Role must be one of: {", ".join(valid_roles)}'}), 400
        
        # Validate email format
        if '@' not in data['email']:
            return jsonify({'message': 'Invalid email format'}), 400
        
        # Validate password length
        if len(data['password']) < 6:
            return jsonify({'message': 'Password must be at least 6 characters long'}), 400
        
        # Check if user already exists
        existing_user = User.query.filter_by(email=data['email']).first()
        if existing_user:
            return jsonify({'message': 'User with this email already exists'}), 409
        
        # Create new user with proper field mapping
        new_user = User(
            name=f"{data['firstName']} {data['lastName']}",
            email=data['email'],
            role=data['role'],
            business_name=data.get('businessName'),
            address=data.get('address'),
            phone_number=data.get('phoneNumber') or data.get('whatsappNumber'),
            is_active=True
        )
        
        # Set password
        new_user.set_password(data['password'])
        
        # Ensure the user has an ID
        if not new_user.id:
            new_user.id = str(uuid.uuid4())
        
        db.session.add(new_user)
        db.session.commit()
        
        print(f"User registered successfully: {new_user.email}")
        
        return jsonify({
            'message': 'Registration successful',
            'user': new_user.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        print(f"Registration error: {str(e)}")
        return jsonify({'message': 'Registration failed', 'error': str(e)}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """Login user and redirect to appropriate dashboard"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'message': 'No data provided'}), 400
            
        email = data.get('email')
        password = data.get('password')
        
        print(f"Login attempt for email: {email}")
        
        if not email or not password:
            return jsonify({'message': 'Email and password are required'}), 400
        
        # Find user
        user = User.query.filter_by(email=email, is_active=True).first()
        if not user:
            print(f"Login failed: User not found for email {email}")
            return jsonify({'message': 'Invalid email or password'}), 401
        
        # Check password
        if not user.check_password(password):
            print(f"Login failed: Invalid password for email {email}")
            return jsonify({'message': 'Invalid email or password'}), 401
        
        # Login user with Flask-Login
        login_user(user)
        print(f"Login successful for user: {user.email}")
        
        # Return JWT token for frontend authentication
        from flask_jwt_extended import create_access_token
        access_token = create_access_token(identity=user.id)
        
        return jsonify({
            'message': 'Login successful',
            'user': user.to_dict(),
            'access_token': access_token,
            'redirectUrl': user.get_dashboard_url()
        }), 200
        
    except Exception as e:
        print(f"Login error: {str(e)}")
        return jsonify({'message': 'Login failed', 'error': str(e)}), 500

@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """Logout user"""
    try:
        # For JWT, we don't need to do anything on logout
        # The client will simply remove the token
        return jsonify({'message': 'Logout successful'}), 200
    except Exception as e:
        return jsonify({'message': 'Logout failed', 'error': str(e)}), 500

@auth_bp.route('/user', methods=['GET'])
@jwt_required()
def get_user():
    """Get current user information"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        if not user:
            return jsonify({'message': 'User not found'}), 404
        return jsonify(user.to_dict()), 200
    except Exception as e:
        return jsonify({'message': 'Failed to get user', 'error': str(e)}), 500

@auth_bp.route('/dashboard', methods=['GET'])
@jwt_required()
def dashboard():
    """Redirect to appropriate dashboard based on user role"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        if not user:
            return jsonify({'message': 'User not found'}), 404
            
        dashboard_url = user.get_dashboard_url()
        return jsonify({
            'redirectUrl': dashboard_url,
            'user': user.to_dict()
        }), 200
    except Exception as e:
        return jsonify({'message': 'Failed to get dashboard', 'error': str(e)}), 500