from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import User, Order, OrderItem, Product, WhatsAppNotification
from app import db
from datetime import datetime
import uuid
from app.utils.decorators import role_required, validate_json

orders_bp = Blueprint('orders', __name__)

@orders_bp.route('/', methods=['GET'])
@jwt_required()
def get_orders():
    """Get orders for current user based on role"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'message': 'User not found'}), 404
        
        if user.role == 'retailer':
            # Retailers see their own orders
            orders = Order.query.filter_by(retailer_id=current_user_id).order_by(Order.created_at.desc()).all()
        elif user.role == 'distributor':
            # Distributors see orders assigned to them
            orders = Order.query.filter_by(distributor_id=current_user_id).order_by(Order.created_at.desc()).all()
        elif user.role == 'manufacturer':
            # Manufacturers see orders for their products
            # This would require joining through products and order items
            orders = Order.query.join(OrderItem).join(Product).filter(
                Product.manufacturer_id == current_user_id
            ).order_by(Order.created_at.desc()).all()
        else:
            return jsonify({'message': 'Invalid user role'}), 400
        
        return jsonify([order.to_dict() for order in orders]), 200
        
    except Exception as e:
        return jsonify({'message': 'Failed to fetch orders', 'error': str(e)}), 500

@orders_bp.route('/<order_id>', methods=['GET'])
@jwt_required()
def get_order(order_id):
    """Get specific order details"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        order = Order.query.get(order_id)
        if not order:
            return jsonify({'message': 'Order not found'}), 404
        
        # Check access permissions
        if user.role == 'retailer' and order.retailer_id != current_user_id:
            return jsonify({'message': 'Access denied'}), 403
        
        if user.role == 'distributor' and order.distributor_id != current_user_id:
            return jsonify({'message': 'Access denied'}), 403
        
        return jsonify(order.to_dict()), 200
        
    except Exception as e:
        return jsonify({'message': 'Failed to fetch order', 'error': str(e)}), 500

@orders_bp.route('/', methods=['POST'])
@jwt_required()
@role_required('retailer')
@validate_json
def create_order():
    """Create new order (retailers only)"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        distributor_id = data.get('distributorId')
        items = data.get('items', [])
        notes = data.get('notes')
        delivery_mode = data.get('deliveryMode', 'delivery')
        
        if not distributor_id or not items:
            return jsonify({'message': 'Distributor ID and items are required'}), 400
        
        # Verify distributor exists
        distributor = User.query.get(distributor_id)
        if not distributor or distributor.role != 'distributor':
            return jsonify({'message': 'Invalid distributor'}), 400
        
        # Generate order number
        order_number = f"ORD-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"
        
        # Calculate total amount
        total_amount = 0
        order_items = []
        
        for item_data in items:
            product_id = item_data.get('productId')
            quantity = item_data.get('quantity', 0)
            unit_price = item_data.get('unitPrice', 0)
            
            if not product_id or quantity <= 0 or unit_price <= 0:
                return jsonify({'message': 'Invalid item data'}), 400
            
            # Verify product exists
            product = Product.query.get(product_id)
            if not product:
                return jsonify({'message': f'Product {product_id} not found'}), 404
            
            total_price = quantity * unit_price
            total_amount += total_price
            
            order_items.append({
                'product_id': product_id,
                'quantity': quantity,
                'unit_price': unit_price,
                'total_price': total_price
            })
        
        # Create order
        new_order = Order(
            order_number=order_number,
            retailer_id=current_user_id,
            distributor_id=distributor_id,
            status='pending',
            delivery_mode=delivery_mode,
            total_amount=total_amount,
            notes=notes
        )
        
        db.session.add(new_order)
        db.session.flush()  # Get the order ID
        
        # Create order items
        for item_data in order_items:
            order_item = OrderItem(
                order_id=new_order.id,
                product_id=item_data['product_id'],
                quantity=item_data['quantity'],
                unit_price=item_data['unit_price'],
                total_price=item_data['total_price']
            )
            db.session.add(order_item)
        
        db.session.commit()
        
        # Send WhatsApp alert to distributor
        retailer = User.query.get(current_user_id)
        message = f"🛒 New order from {retailer.firstName} {retailer.lastName}\n"
        message += f"Order: {order_number}\n"
        message += f"Amount: ₹{total_amount}\n"
        message += f"Items: {len(items)} products\n"
        message += f"Delivery Mode: {delivery_mode.title()}\n\n"
        message += "Please acknowledge:\n"
        message += "1️⃣ Accept\n"
        message += "2️⃣ Reject"
        
        notification = WhatsAppNotification(
            user_id=distributor_id,
            message=message,
            type='order_alert',
            sent_at=datetime.utcnow(),
            is_delivered=True
        )
        
        db.session.add(notification)
        db.session.commit()
        
        print(f"📱 Order Alert to Distributor {distributor.email}: {message}")
        
        return jsonify(new_order.to_dict()), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Failed to create order', 'error': str(e)}), 500

@orders_bp.route('/<order_id>/status', methods=['PUT'])
@jwt_required()
@role_required('distributor')
def update_order_status(order_id):
    """Update order status (distributors only)"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        new_status = data.get('status')
        delivery_mode = data.get('deliveryMode')
        
        if not new_status:
            return jsonify({'message': 'Status is required'}), 400
        
        order = Order.query.get(order_id)
        if not order:
            return jsonify({'message': 'Order not found'}), 404
        
        # Verify distributor owns this order
        if order.distributor_id != current_user_id:
            return jsonify({'message': 'Access denied'}), 403
        
        # Update status
        old_status = order.status
        order.status = new_status
        
        if delivery_mode:
            order.delivery_mode = delivery_mode
        
        order.updated_at = datetime.utcnow()
        db.session.commit()
        
        # Send WhatsApp notification to retailer
        retailer = User.query.get(order.retailer_id)
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
        elif new_status == 'accepted':
            message += "\nYour order has been accepted! ✅"
        elif new_status == 'rejected':
            message += "\nYour order has been rejected. Please contact us."
        
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
            'message': 'Order status updated successfully',
            'order': order.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Failed to update order status', 'error': str(e)}), 500

@orders_bp.route('/<order_id>/delivery-mode', methods=['PUT'])
@jwt_required()
@role_required('distributor')
def update_delivery_mode(order_id):
    """Update delivery mode (distributors only)"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        delivery_mode = data.get('deliveryMode')
        
        if not delivery_mode:
            return jsonify({'message': 'Delivery mode is required'}), 400
        
        order = Order.query.get(order_id)
        if not order:
            return jsonify({'message': 'Order not found'}), 404
        
        # Verify distributor owns this order
        if order.distributor_id != current_user_id:
            return jsonify({'message': 'Access denied'}), 403
        
        # Update delivery mode
        order.delivery_mode = delivery_mode
        order.updated_at = datetime.utcnow()
        db.session.commit()
        
        # Send WhatsApp notification to retailer
        retailer = User.query.get(order.retailer_id)
        mode_emojis = {
            'delivery': '🚚',
            'pickup': '🏬'
        }
        
        emoji = mode_emojis.get(delivery_mode, '📋')
        message = f"{emoji} Delivery Mode Updated\n"
        message += f"Order: {order.order_number}\n"
        message += f"Mode: {delivery_mode.title()}\n"
        
        if delivery_mode == 'delivery':
            message += "\nWe will deliver your order to your address."
        elif delivery_mode == 'pickup':
            message += "\nPlease pick up your order from our location."
        
        notification = WhatsAppNotification(
            user_id=order.retailer_id,
            message=message,
            type='delivery_update',
            sent_at=datetime.utcnow(),
            is_delivered=True
        )
        
        db.session.add(notification)
        db.session.commit()
        
        print(f"📱 Delivery Update to Retailer {retailer.email}: {message}")
        
        return jsonify({
            'message': 'Delivery mode updated successfully',
            'order': order.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Failed to update delivery mode', 'error': str(e)}), 500 

@orders_bp.route('/history/<partner_id>', methods=['GET'])
@jwt_required()
def get_order_history(partner_id):
    """Get order history with a specific partner"""
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        partner = User.query.get(partner_id)
        
        if not partner:
            return jsonify({'message': 'Partner not found'}), 404
        
        # Determine the relationship and get appropriate orders
        orders = []
        
        if current_user.role == 'distributor' and partner.role == 'retailer':
            # Distributor viewing orders with a retailer
            orders = Order.query.filter_by(
                distributor_id=current_user_id,
                retailer_id=partner_id
            ).order_by(Order.created_at.desc()).all()
            
        elif current_user.role == 'manufacturer' and partner.role == 'distributor':
            # Manufacturer viewing orders with a distributor
            orders = Order.query.filter_by(
                distributor_id=partner_id
            ).join(OrderItem).join(Product).filter(
                Product.manufacturer_id == current_user_id
            ).order_by(Order.created_at.desc()).all()
            
        elif current_user.role == 'retailer' and partner.role == 'distributor':
            # Retailer viewing orders with a distributor
            orders = Order.query.filter_by(
                retailer_id=current_user_id,
                distributor_id=partner_id
            ).order_by(Order.created_at.desc()).all()
            
        else:
            return jsonify({'message': 'Access denied'}), 403
        
        # Convert to dict with items
        order_data = []
        for order in orders:
            order_dict = order.to_dict()
            order_dict['items'] = [item.to_dict() for item in order.items]
            order_data.append(order_dict)
        
        return jsonify(order_data), 200
        
    except Exception as e:
        return jsonify({'message': 'Failed to fetch order history', 'error': str(e)}), 500 