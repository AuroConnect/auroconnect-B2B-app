from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models import Order, OrderItem, User, Product
from app.utils.decorators import validate_json, role_required
from datetime import datetime
import uuid

orders_bp = Blueprint('orders', __name__)

@orders_bp.route('/', methods=['GET'])
@jwt_required()
def get_orders():
    """Get user orders"""
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        if not current_user:
            return jsonify({'message': 'User not found'}), 404
        
        # Get orders based on user role
        if current_user.role == 'retailer':
            orders = Order.query.filter_by(retailer_id=current_user_id).all()
        elif current_user.role == 'distributor':
            orders = Order.query.filter_by(distributor_id=current_user_id).all()
        else:
            return jsonify({'message': 'Unauthorized'}), 403
        
        return jsonify([order.to_dict() for order in orders]), 200
        
    except Exception as e:
        return jsonify({'message': 'Failed to fetch orders', 'error': str(e)}), 500

@orders_bp.route('/<order_id>', methods=['GET'])
@jwt_required()
def get_order(order_id):
    """Get specific order"""
    try:
        current_user_id = get_jwt_identity()
        
        order = Order.query.get(order_id)
        
        if not order:
            return jsonify({'message': 'Order not found'}), 404
        
        # Check if user has access to this order
        if str(order.retailer_id) != current_user_id and str(order.distributor_id) != current_user_id:
            return jsonify({'message': 'Unauthorized'}), 403
        
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
        
        return jsonify(new_order.to_dict()), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Failed to create order', 'error': str(e)}), 500

@orders_bp.route('/<order_id>/status', methods=['PATCH'])
@jwt_required()
@role_required('distributor')
@validate_json
def update_order_status(order_id):
    """Update order status (distributors only)"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        status = data.get('status')
        
        if status not in ['pending', 'confirmed', 'packed', 'out_for_delivery', 'delivered', 'cancelled']:
            return jsonify({'message': 'Invalid status'}), 400
        
        order = Order.query.get(order_id)
        
        if not order:
            return jsonify({'message': 'Order not found'}), 404
        
        # Check if current user is the distributor for this order
        if str(order.distributor_id) != current_user_id:
            return jsonify({'message': 'Unauthorized'}), 403
        
        order.status = status
        db.session.commit()
        
        return jsonify(order.to_dict()), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Failed to update order status', 'error': str(e)}), 500 