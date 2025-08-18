from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models import User
from app.utils.decorators import roles_required

users_bp = Blueprint('users', __name__)

@users_bp.route('/distributors', methods=['GET'])
@jwt_required()
@roles_required(['manufacturer'])
def get_distributors():
    """Get all distributors for manufacturer to assign products"""
    try:
        current_user_id = get_jwt_identity()
        
        # Get all active distributors
        distributors = User.query.filter_by(
            role='distributor',
            is_active=True
        ).all()
        
        distributors_data = []
        for distributor in distributors:
            distributors_data.append({
                'id': str(distributor.id),
                'firstName': distributor.first_name,
                'lastName': distributor.last_name,
                'email': distributor.email,
                'businessName': distributor.business_name,
                'phoneNumber': distributor.phone_number,
                'address': distributor.address
            })
        
        return jsonify(distributors_data), 200
        
    except Exception as e:
        return jsonify({'message': 'Failed to fetch distributors', 'error': str(e)}), 500
