from functools import wraps
from flask import request, jsonify
from flask_jwt_extended import get_jwt_identity
from app.models import User

def validate_json(required_fields=None):
    """Decorator to validate JSON request"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not request.is_json:
                return jsonify({'message': 'Content-Type must be application/json'}), 400
            
            if required_fields:
                data = request.get_json()
                if not data:
                    return jsonify({'message': 'No JSON data provided'}), 400
                
                missing_fields = [field for field in required_fields if field not in data]
                if missing_fields:
                    return jsonify({'message': f'Missing required fields: {", ".join(missing_fields)}'}), 400
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def role_required(required_role):
    """Decorator to check user role"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            current_user_id = get_jwt_identity()
            user = User.query.get(current_user_id)
            
            if not user:
                return jsonify({'message': 'User not found'}), 404
            
            if user.role != required_role:
                return jsonify({'message': f'Access denied. {required_role} role required'}), 403
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def roles_required(required_roles):
    """Decorator to check if user has any of the required roles"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            current_user_id = get_jwt_identity()
            user = User.query.get(current_user_id)
            
            if not user:
                return jsonify({'message': 'User not found'}), 404
            
            if user.role not in required_roles:
                return jsonify({'message': f'Access denied. One of {required_roles} roles required'}), 403
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator 