from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from app import db
from app.models import User
from app.utils.decorators import validate_json
from app.utils.validators import UserSchema
from marshmallow import ValidationError
import uuid

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
@validate_json
def register():
    """Register a new user"""
    try:
        # Validate input data
        schema = UserSchema()
        data = schema.load(request.get_json())
        
        # Check if user already exists
        existing_user = User.query.filter_by(email=data['email']).first()
        if existing_user:
            return jsonify({'message': 'User with this email already exists'}), 409
        
        # Create new user without password first
        new_user = User(
            email=data['email'],
            first_name=data['firstName'],
            last_name=data['lastName'],
            role=data['role'],
            business_name=data.get('businessName'),
            address=data.get('address'),
            phone_number=data.get('phoneNumber'),
            whatsapp_number=data.get('whatsappNumber'),
            is_active=True
        )
        
        # Manually set the password
        new_user.set_password(data['password'])
        
        db.session.add(new_user)
        db.session.commit()
        
        return jsonify({
            'message': 'Registration successful',
            'user': new_user.to_dict()
        }), 201
        
    except ValidationError as e:
        return jsonify({'message': 'Validation error', 'errors': e.messages}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Registration failed', 'error': str(e)}), 500

@auth_bp.route('/login', methods=['POST'])
@validate_json
def login():
    """Login user and return JWT token"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'message': 'No data provided'}), 400
            
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return jsonify({'message': 'Email and password are required'}), 400
        
        # Find user
        user = User.query.filter_by(email=email, is_active=True).first()
        if not user:
            return jsonify({'message': 'Invalid email or password'}), 401
        
        # Check password
        if not user.check_password(password):
            return jsonify({'message': 'Invalid email or password'}), 401
        
        # Create access token
        try:
            access_token = create_access_token(identity=str(user.id))
        except Exception as e:
            return jsonify({'message': 'Token creation failed', 'error': str(e)}), 500
        
        return jsonify({
            'message': 'Login successful',
            'access_token': access_token,
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'message': 'Login failed', 'error': str(e)}), 500

@auth_bp.route('/user', methods=['GET'])
@jwt_required()
def get_user():
    """Get current user information"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'message': 'User not found'}), 404
        
        return jsonify(user.to_dict()), 200
        
    except Exception as e:
        return jsonify({'message': 'Failed to get user', 'error': str(e)}), 500

@auth_bp.route('/refresh', methods=['POST'])
@jwt_required()
def refresh():
    """Refresh JWT token"""
    try:
        current_user_id = get_jwt_identity()
        new_token = create_access_token(identity=current_user_id)
        
        return jsonify({
            'access_token': new_token
        }), 200
        
    except Exception as e:
        return jsonify({'message': 'Token refresh failed', 'error': str(e)}), 500 