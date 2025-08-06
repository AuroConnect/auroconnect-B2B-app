from flask import Blueprint, request, jsonify, session
from flask_login import login_user, logout_user, login_required, current_user
from models import db
from models.user import User, UserRole
from datetime import datetime
import re

auth_bp = Blueprint('auth', __name__)

def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password(password):
    """Validate password strength"""
    # At least 8 characters, one uppercase, one lowercase, one digit
    if len(password) < 8:
        return False
    if not re.search(r'[A-Z]', password):
        return False
    if not re.search(r'[a-z]', password):
        return False
    if not re.search(r'\d', password):
        return False
    return True

@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new user"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['email', 'password', 'name', 'company_name', 'address', 'phone', 'role']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({'error': {'code': 'MISSING_FIELD', 'message': f'{field} is required'}}), 400
        
        # Validate email format
        if not validate_email(data['email']):
            return jsonify({'error': {'code': 'INVALID_EMAIL', 'message': 'Invalid email format'}}), 400
        
        # Validate password strength
        if not validate_password(data['password']):
            return jsonify({'error': {'code': 'WEAK_PASSWORD', 'message': 'Password must be at least 8 characters with uppercase, lowercase, and digit'}}), 400
        
        # Validate role
        valid_roles = ['manufacturer', 'distributor', 'retailer']
        if data['role'] not in valid_roles:
            return jsonify({'error': {'code': 'INVALID_ROLE', 'message': f'Role must be one of {valid_roles}'}}), 400
        
        # Check if user already exists
        existing_user = User.query.filter_by(email=data['email']).first()
        if existing_user:
            return jsonify({'error': {'code': 'EMAIL_EXISTS', 'message': 'Email already registered'}}), 409
        
        # Create new user
        user = User(
            email=data['email'],
            name=data['name'],
            company_name=data['company_name'],
            address=data['address'],
            phone=data['phone'],
            role=data['role']
        )
        user.set_password(data['password'])
        
        # Add user to database
        db.session.add(user)
        db.session.flush()  # Get the user ID without committing
        
        # Create user role entry
        user_role = UserRole(
            user_id=user.id,
            role=data['role']
        )
        db.session.add(user_role)
        
        # Commit changes
        db.session.commit()
        
        # Return user data (without password)
        return jsonify({
            'data': {
                'id': user.id,
                'email': user.email,
                'name': user.name,
                'company_name': user.company_name,
                'address': user.address,
                'phone': user.phone,
                'role': user.role,
                'created_at': user.created_at.isoformat()
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': {'code': 'REGISTRATION_ERROR', 'message': 'Registration failed', 'details': str(e)}}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """Login user"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if 'email' not in data or not data['email']:
            return jsonify({'error': {'code': 'MISSING_EMAIL', 'message': 'Email is required'}}), 400
        
        if 'password' not in data or not data['password']:
            return jsonify({'error': {'code': 'MISSING_PASSWORD', 'message': 'Password is required'}}), 400
        
        # Find user by email
        user = User.query.filter_by(email=data['email']).first()
        
        # Check if user exists and password is correct
        if not user or not user.check_password(data['password']):
            return jsonify({'error': {'code': 'INVALID_CREDENTIALS', 'message': 'Invalid email or password'}}), 401
        
        # Login user
        login_user(user, remember=data.get('remember', False))
        
        # Return success response
        return jsonify({
            'data': {
                'message': 'Login successful',
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'name': user.name,
                    'company_name': user.company_name,
                    'role': user.role,
                    'role_display': user.get_role_display()
                }
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': {'code': 'LOGIN_ERROR', 'message': 'Login failed', 'details': str(e)}}), 500

@auth_bp.route('/logout', methods=['POST'])
@login_required
def logout():
    """Logout user"""
    try:
        logout_user()
        return jsonify({'data': {'message': 'Logout successful'}}), 200
    except Exception as e:
        return jsonify({'error': {'code': 'LOGOUT_ERROR', 'message': 'Logout failed', 'details': str(e)}}), 500

@auth_bp.route('/profile', methods=['GET'])
@login_required
def profile():
    """Get current user profile"""
    try:
        return jsonify({
            'data': {
                'id': current_user.id,
                'email': current_user.email,
                'name': current_user.name,
                'company_name': current_user.company_name,
                'address': current_user.address,
                'phone': current_user.phone,
                'role': current_user.role,
                'role_display': current_user.get_role_display(),
                'created_at': current_user.created_at.isoformat()
            }
        }), 200
    except Exception as e:
        return jsonify({'error': {'code': 'PROFILE_ERROR', 'message': 'Failed to retrieve profile', 'details': str(e)}}), 500

@auth_bp.route('/profile', methods=['PUT'])
@login_required
def update_profile():
    """Update current user profile"""
    try:
        data = request.get_json()
        
        # Update allowed fields
        if 'name' in data:
            current_user.name = data['name']
        if 'company_name' in data:
            current_user.company_name = data['company_name']
        if 'address' in data:
            current_user.address = data['address']
        if 'phone' in data:
            current_user.phone = data['phone']
        
        current_user.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'data': {
                'message': 'Profile updated successfully',
                'user': current_user.to_dict()
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': {'code': 'UPDATE_PROFILE_ERROR', 'message': 'Failed to update profile', 'details': str(e)}}), 500