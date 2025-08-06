from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import User
from app import db
from datetime import datetime, timedelta

notifications_bp = Blueprint('notifications', __name__)

@notifications_bp.route('/', methods=['GET'])
@jwt_required()
def get_notifications():
    """Get notifications for the current user"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'message': 'User not found'}), 404
        
        # Return empty array - notifications are now handled by WhatsApp API
        return jsonify([]), 200
        
    except Exception as e:
        return jsonify({'message': 'Error fetching notifications', 'error': str(e)}), 500 