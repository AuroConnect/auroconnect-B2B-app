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
        
        # For now, return mock notifications
        # In a real app, you'd have a notifications table
        mock_notifications = [
            {
                'id': '1',
                'message': 'Your order #ORD-001 has been confirmed',
                'type': 'order_update',
                'createdAt': (datetime.utcnow() - timedelta(hours=2)).isoformat(),
                'read': False
            },
            {
                'id': '2', 
                'message': 'New product available from your favorite distributor',
                'type': 'product_update',
                'createdAt': (datetime.utcnow() - timedelta(hours=5)).isoformat(),
                'read': False
            },
            {
                'id': '3',
                'message': 'Invoice for order #ORD-002 is ready for download',
                'type': 'invoice',
                'createdAt': (datetime.utcnow() - timedelta(days=1)).isoformat(),
                'read': True
            }
        ]
        
        return jsonify(mock_notifications), 200
        
    except Exception as e:
        return jsonify({'message': 'Error fetching notifications', 'error': str(e)}), 500 