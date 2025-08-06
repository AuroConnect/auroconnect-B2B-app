from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import User, Order, WhatsAppNotification
from app import db
from datetime import datetime
import uuid

whatsapp_bp = Blueprint('whatsapp', __name__)

@whatsapp_bp.route('/send', methods=['POST'])
@jwt_required()
def send_whatsapp():
    """Send WhatsApp notification (simulated)"""
    try:
        data = request.get_json()
        user_id = data.get('userId')
        message = data.get('message')
        notification_type = data.get('type', 'general')
        
        if not user_id or not message:
            return jsonify({'message': 'User ID and message are required'}), 400
        
        # Create notification record
        notification = WhatsAppNotification(
            user_id=user_id,
            message=message,
            type=notification_type,
            sent_at=datetime.utcnow(),
            is_delivered=True  # Simulated as delivered
        )
        
        db.session.add(notification)
        db.session.commit()
        
        # In a real app, this would integrate with WhatsApp Business API
        print(f"📱 WhatsApp to User {user_id}: {message}")
        
        return jsonify({
            'message': 'WhatsApp notification sent successfully',
            'notification': {
                'id': str(notification.id),
                'message': notification.message,
                'type': notification.type,
                'sentAt': notification.sent_at.isoformat() if notification.sent_at else None
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Failed to send WhatsApp notification', 'error': str(e)}), 500

@whatsapp_bp.route('/notifications', methods=['GET'])
@jwt_required()
def get_notifications():
    """Get WhatsApp notifications for current user"""
    try:
        current_user_id = get_jwt_identity()
        
        notifications = WhatsAppNotification.query.filter_by(
            user_id=current_user_id
        ).order_by(WhatsAppNotification.created_at.desc()).limit(50).all()
        
        return jsonify([{
            'id': str(n.id),
            'message': n.message,
            'type': n.type,
            'sentAt': n.sent_at.isoformat() if n.sent_at else None,
            'isDelivered': n.is_delivered,
            'createdAt': n.created_at.isoformat() if n.created_at else None
        } for n in notifications]), 200
        
    except Exception as e:
        return jsonify({'message': 'Failed to fetch notifications', 'error': str(e)}), 500

@whatsapp_bp.route('/order-alert/<order_id>', methods=['POST'])
@jwt_required()
def send_order_alert(order_id):
    """Send order alert to distributor"""
    try:
        order = Order.query.get(order_id)
        if not order:
            return jsonify({'message': 'Order not found'}), 404
        
        distributor = User.query.get(order.distributor_id)
        retailer = User.query.get(order.retailer_id)
        
        if not distributor or not retailer:
            return jsonify({'message': 'Invalid order data'}), 400
        
        # Create WhatsApp alert message
        message = f"🛒 New order from {retailer.firstName} {retailer.lastName}\n"
        message += f"Order: {order.order_number}\n"
        message += f"Amount: ₹{order.total_amount}\n"
        message += f"Items: {len(order.items)} products\n\n"
        message += "Please acknowledge:\n"
        message += "1️⃣ Accept\n"
        message += "2️⃣ Reject"
        
        # Send to distributor
        notification = WhatsAppNotification(
            user_id=order.distributor_id,
            message=message,
            type='order_alert',
            sent_at=datetime.utcnow(),
            is_delivered=True
        )
        
        db.session.add(notification)
        db.session.commit()
        
        print(f"📱 Order Alert to Distributor {distributor.email}: {message}")
        
        return jsonify({
            'message': 'Order alert sent successfully',
            'notification': {
                'id': str(notification.id),
                'message': notification.message,
                'type': notification.type
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Failed to send order alert', 'error': str(e)}), 500

@whatsapp_bp.route('/status-update/<order_id>', methods=['POST'])
@jwt_required()
def send_status_update(order_id):
    """Send order status update to retailer"""
    try:
        data = request.get_json()
        new_status = data.get('status')
        
        order = Order.query.get(order_id)
        if not order:
            return jsonify({'message': 'Order not found'}), 404
        
        retailer = User.query.get(order.retailer_id)
        if not retailer:
            return jsonify({'message': 'Invalid order data'}), 400
        
        # Create status update message
        status_emojis = {
            'accepted': '✅',
            'packed': '📦',
            'dispatched': '🚚',
            'delivered': '🎉',
            'rejected': '❌'
        }
        
        emoji = status_emojis.get(new_status, '📋')
        message = f"{emoji} Order Status Update\n"
        message += f"Order: {order.order_number}\n"
        message += f"Status: {new_status.title()}\n"
        
        if new_status == 'delivered':
            message += "\nYour order has been delivered! 🎉"
        elif new_status == 'dispatched':
            message += "\nYour order is on the way! 🚚"
        elif new_status == 'packed':
            message += "\nYour order is packed and ready! 📦"
        
        # Send to retailer
        notification = WhatsAppNotification(
            user_id=order.retailer_id,
            message=message,
            type='status_update',
            sent_at=datetime.utcnow(),
            is_delivered=True
        )
        
        db.session.add(notification)
        db.session.commit()
        
        print(f"📱 Status Update to Retailer {retailer.email}: {message}")
        
        return jsonify({
            'message': 'Status update sent successfully',
            'notification': {
                'id': str(notification.id),
                'message': notification.message,
                'type': notification.type
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Failed to send status update', 'error': str(e)}), 500 