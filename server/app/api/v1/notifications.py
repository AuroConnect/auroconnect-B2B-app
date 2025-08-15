from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.user import User
from app.models.order import Order, OrderChat
from app.models.inventory import Inventory
from app.models.product import Product
from app.utils.decorators import roles_required
from app import db
from datetime import datetime, timedelta
from sqlalchemy import and_, or_
from app.models.whatsapp import WhatsAppNotification

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
        
        # Get notifications based on user role
        notifications = []
        
        # Low stock alerts
        if user.role in ['manufacturer', 'distributor']:
            low_stock_items = get_low_stock_notifications(user)
            notifications.extend(low_stock_items)
        
        # Order status updates
        order_notifications = get_order_notifications(user)
        notifications.extend(order_notifications)
        
        # Backorder alerts
        if user.role in ['distributor', 'retailer']:
            backorder_notifications = get_backorder_notifications(user)
            notifications.extend(backorder_notifications)
        
        # Sort by created_at (newest first)
        notifications.sort(key=lambda x: x['created_at'], reverse=True)
        
        return jsonify(notifications), 200
        
    except Exception as e:
        return jsonify({'message': 'Error fetching notifications', 'error': str(e)}), 500

def get_low_stock_notifications(user):
    """Get low stock notifications"""
    notifications = []
    
    if user.role == 'manufacturer':
        # Manufacturers see low stock across all distributors
        low_stock_items = db.session.query(Inventory).join(Product).filter(
            and_(
                Product.manufacturer_id == user.id,
                Inventory.available_quantity <= Inventory.low_stock_threshold
            )
        ).all()
        
        for item in low_stock_items:
            notifications.append({
                'id': f"low_stock_{item.id}",
                'type': 'LOW_STOCK',
                'title': 'Low Stock Alert',
                'message': f'Product {item.product.name} is running low on stock (Available: {item.available_quantity})',
                'severity': 'WARNING',
                'created_at': item.updated_at.isoformat(),
                'data': {
                    'product_id': item.product_id,
                    'available_quantity': item.available_quantity,
                    'low_stock_threshold': item.low_stock_threshold
                }
            })
    
    elif user.role == 'distributor':
        # Distributors see their own low stock
        low_stock_items = Inventory.query.filter(
            and_(
                Inventory.distributor_id == user.id,
                Inventory.available_quantity <= Inventory.low_stock_threshold
            )
        ).all()
        
        for item in low_stock_items:
            notifications.append({
                'id': f"low_stock_{item.id}",
                'type': 'LOW_STOCK',
                'title': 'Low Stock Alert',
                'message': f'Product {item.product.name} is running low on stock (Available: {item.available_quantity})',
                'severity': 'WARNING',
                'created_at': item.updated_at.isoformat(),
                'data': {
                    'product_id': item.product_id,
                    'available_quantity': item.available_quantity,
                    'low_stock_threshold': item.low_stock_threshold
                }
            })
    
    return notifications

def get_order_notifications(user):
    """Get order status notifications"""
    notifications = []
    
    # Get recent orders (last 7 days)
    recent_date = datetime.utcnow() - timedelta(days=7)
    
    if user.role == 'manufacturer':
        # Manufacturers see orders they sold
        orders = Order.query.filter(
            and_(
                Order.seller_id == user.id,
                Order.updated_at >= recent_date
            )
        ).all()
    elif user.role == 'distributor':
        # Distributors see both buying and selling orders
        orders = Order.query.filter(
            and_(
                or_(Order.buyer_id == user.id, Order.seller_id == user.id),
                Order.updated_at >= recent_date
            )
        ).all()
    elif user.role == 'retailer':
        # Retailers see orders they bought
        orders = Order.query.filter(
            and_(
                Order.buyer_id == user.id,
                Order.updated_at >= recent_date
            )
        ).all()
    else:
        return notifications
    
    for order in orders:
        # New order notification
        if order.status == 'PENDING' and order.created_at >= recent_date:
            notifications.append({
                'id': f"new_order_{order.id}",
                'type': 'NEW_ORDER',
                'title': 'New Order Received',
                'message': f'New order #{order.id[:8]} received from {order.buyer.business_name}',
                'severity': 'INFO',
                'created_at': order.created_at.isoformat(),
                'data': {
                    'order_id': order.id,
                    'buyer_name': order.buyer.business_name,
                    'total_amount': order.total_amount
                }
            })
        
        # Status change notifications
        if order.status in ['ACCEPTED', 'REJECTED', 'PARTIAL']:
            notifications.append({
                'id': f"order_status_{order.id}",
                'type': 'ORDER_STATUS',
                'title': f'Order {order.status.title()}',
                'message': f'Order #{order.id[:8]} has been {order.status.lower()}',
                'severity': 'INFO' if order.status == 'ACCEPTED' else 'WARNING',
                'created_at': order.updated_at.isoformat(),
                'data': {
                    'order_id': order.id,
                    'status': order.status,
                    'seller_name': order.seller.business_name
                }
            })
        
        # Shipment notifications
        if order.status in ['SHIPPED', 'OUT_FOR_DELIVERY', 'DELIVERED']:
            notifications.append({
                'id': f"shipment_{order.id}",
                'type': 'SHIPMENT',
                'title': f'Order {order.status.replace("_", " ").title()}',
                'message': f'Order #{order.id[:8]} has been {order.status.lower().replace("_", " ")}',
                'severity': 'INFO',
                'created_at': order.updated_at.isoformat(),
                'data': {
                    'order_id': order.id,
                    'status': order.status
                }
            })
    
    return notifications

def get_backorder_notifications(user):
    """Get backorder notifications"""
    notifications = []
    
    if user.role in ['distributor', 'retailer']:
        # Get orders with backordered items
        orders = Order.query.filter(
            and_(
                Order.buyer_id == user.id,
                Order.status.in_(['ACCEPTED', 'PARTIAL'])
            )
        ).all()
        
        for order in orders:
            backordered_items = [item for item in order.items if item.is_backordered]
            if backordered_items:
                notifications.append({
                    'id': f"backorder_{order.id}",
                    'type': 'BACKORDER',
                    'title': 'Backorder Alert',
                    'message': f'Order #{order.id[:8]} has {len(backordered_items)} backordered items',
                    'severity': 'WARNING',
                    'created_at': order.updated_at.isoformat(),
                    'data': {
                        'order_id': order.id,
                        'backordered_items': [item.to_dict() for item in backordered_items]
                    }
                })
    
    return notifications

@notifications_bp.route('/<notification_id>/read', methods=['PATCH'])
@jwt_required()
def mark_notification_read(notification_id):
    """Mark a notification as read"""
    try:
        current_user_id = get_jwt_identity()
        
        notification = WhatsAppNotification.query.filter_by(
            id=notification_id,
            user_id=current_user_id
        ).first()
        
        if not notification:
            return jsonify({'message': 'Notification not found'}), 404
        
        notification.mark_as_read()
        
        return jsonify({'message': 'Notification marked as read'}), 200
        
    except Exception as e:
        return jsonify({'message': f'Failed to mark notification as read: {str(e)}'}), 500

@notifications_bp.route('/mark-all-read', methods=['PATCH'])
@jwt_required()
def mark_all_notifications_read():
    """Mark all notifications as read for current user"""
    try:
        current_user_id = get_jwt_identity()
        
        notifications = WhatsAppNotification.query.filter_by(
            user_id=current_user_id,
            is_read=False
        ).all()
        
        for notification in notifications:
            notification.is_read = True
        
        db.session.commit()
        
        return jsonify({'message': f'Marked {len(notifications)} notifications as read'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Failed to mark notifications as read: {str(e)}'}), 500

@notifications_bp.route('/order-chat/<order_id>', methods=['GET'])
@jwt_required()
def get_order_chat(order_id):
    """Get chat messages for an order"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'message': 'User not found'}), 404
        
        # Get order and check access
        order = Order.query.get(order_id)
        if not order:
            return jsonify({'message': 'Order not found'}), 404
        
        # Check if user has access to this order
        if order.buyer_id != current_user_id and order.seller_id != current_user_id:
            return jsonify({'message': 'Access denied'}), 403
        
        # Get chat messages
        chat_messages = OrderChat.query.filter_by(order_id=order_id).order_by(OrderChat.created_at).all()
        
        return jsonify({
            'order_id': order_id,
            'messages': [message.to_dict() for message in chat_messages]
        }), 200
        
    except Exception as e:
        return jsonify({'message': 'Error fetching chat messages', 'error': str(e)}), 500

@notifications_bp.route('/order-chat/<order_id>', methods=['POST'])
@jwt_required()
def send_order_chat_message(order_id):
    """Send a chat message for an order"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'message': 'User not found'}), 404
        
        # Get order and check access
        order = Order.query.get(order_id)
        if not order:
            return jsonify({'message': 'Order not found'}), 404
        
        # Check if user has access to this order
        if order.buyer_id != current_user_id and order.seller_id != current_user_id:
            return jsonify({'message': 'Access denied'}), 403
        
        data = request.get_json()
        message_text = data.get('message', '').strip()
        message_type = data.get('type', 'TEXT')
        
        if not message_text:
            return jsonify({'message': 'Message cannot be empty'}), 400
        
        # Create chat message
        chat_message = OrderChat(
            order_id=order_id,
            user_id=current_user_id,
            message=message_text,
            message_type=message_type
        )
        
        db.session.add(chat_message)
        db.session.commit()
        
        return jsonify({
            'message': 'Chat message sent successfully',
            'chat_message': chat_message.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Error sending chat message', 'error': str(e)}), 500

@notifications_bp.route('/low-stock-alerts', methods=['GET'])
@jwt_required()
@roles_required(['manufacturer', 'distributor'])
def get_low_stock_alerts():
    """Get detailed low stock alerts"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if user.role == 'manufacturer':
            low_stock_items = db.session.query(Inventory).join(Product).filter(
                and_(
                    Product.manufacturer_id == current_user_id,
                    Inventory.available_quantity <= Inventory.low_stock_threshold
                )
            ).all()
        else:  # distributor
            low_stock_items = Inventory.query.filter(
                and_(
                    Inventory.distributor_id == current_user_id,
                    Inventory.available_quantity <= Inventory.low_stock_threshold
                )
            ).all()
        
        return jsonify({
            'low_stock_items': [item.to_dict() for item in low_stock_items],
            'count': len(low_stock_items)
        }), 200
        
    except Exception as e:
        return jsonify({'message': 'Error fetching low stock alerts', 'error': str(e)}), 500

@notifications_bp.route('/backorder-alerts', methods=['GET'])
@jwt_required()
@roles_required(['distributor', 'retailer'])
def get_backorder_alerts():
    """Get backorder alerts"""
    try:
        current_user_id = get_jwt_identity()
        
        # Get orders with backordered items
        orders = Order.query.filter(
            and_(
                Order.buyer_id == current_user_id,
                Order.status.in_(['ACCEPTED', 'PARTIAL'])
            )
        ).all()
        
        backorder_alerts = []
        for order in orders:
            backordered_items = [item for item in order.items if item.is_backordered]
            if backordered_items:
                backorder_alerts.append({
                    'order': order.to_dict(),
                    'backordered_items': [item.to_dict() for item in backordered_items]
                })
        
        return jsonify({
            'backorder_alerts': backorder_alerts,
            'count': len(backorder_alerts)
        }), 200
        
    except Exception as e:
        return jsonify({'message': 'Error fetching backorder alerts', 'error': str(e)}), 500 