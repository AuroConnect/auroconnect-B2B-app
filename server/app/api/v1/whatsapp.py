from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.user import User
from app import db

whatsapp_bp = Blueprint('whatsapp', __name__)

@whatsapp_bp.route('/notifications', methods=['GET'])
@jwt_required()
def get_notifications():
    """Get WhatsApp notifications for current user"""
    try:
        current_user_id = get_jwt_identity()
        
        # Return empty notifications for now
        notifications = []
        
        return jsonify(notifications), 200
        
    except Exception as e:
        return jsonify({'message': 'Failed to fetch notifications', 'error': str(e)}), 500 