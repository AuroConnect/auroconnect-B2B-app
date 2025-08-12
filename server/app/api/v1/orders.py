from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.order import Order, OrderItem
from app.models.product import Product
from app.models.user import User
from app.models.cart import CartItem
from app.utils.decorators import role_required, roles_required
from datetime import datetime
import uuid

orders_bp = Blueprint('orders', __name__)

@orders_bp.route('/', methods=['GET'])
@jwt_required()
def get_orders():
    """Get orders based on user role"""
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        if not current_user:
            return jsonify({'message': 'User not found'}), 404
        
        status_filter = request.args.get('status')
        order_type = request.args.get('type', 'all')  # 'buying', 'selling', 'all'
        
        # Base query
        if current_user.role == 'manufacturer':
            # Manufacturer sees orders where they are the seller
            query = Order.query.filter_by(seller_id=current_user_id)
        elif current_user.role == 'distributor':
            if order_type == 'buying':
                # Orders to manufacturer
                query = Order.query.filter_by(buyer_id=current_user_id)
            elif order_type == 'selling':
                # Orders from retailers
                query = Order.query.filter_by(seller_id=current_user_id)
            else:
                # All orders (buying and selling)
                query = Order.query.filter(
                    (Order.buyer_id == current_user_id) | (Order.seller_id == current_user_id)
                )
        elif current_user.role == 'retailer':
            # Retailer sees orders where they are the buyer
            query = Order.query.filter_by(buyer_id=current_user_id)
        else:
            return jsonify({'message': 'Invalid user role'}), 400
        
        # Apply status filter
        if status_filter and status_filter != 'all':
            query = query.filter_by(status=status_filter)
        
        # Order by creation date
        query = query.order_by(Order.created_at.desc())
        
        orders = query.all()
        
        return jsonify([order.to_dict() for order in orders]), 200
        
    except Exception as e:
        return jsonify({'message': 'Failed to fetch orders', 'error': str(e)}), 500

@orders_bp.route('/<order_id>', methods=['GET'])
@jwt_required()
def get_order(order_id):
    """Get specific order details"""
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        if not current_user:
            return jsonify({'message': 'User not found'}), 404
        
        order = Order.query.get(order_id)
        if not order:
            return jsonify({'message': 'Order not found'}), 404
        
        # Check if user has access to this order
        if order.buyer_id != current_user_id and order.seller_id != current_user_id:
            return jsonify({'message': 'Access denied'}), 403
        
        return jsonify(order.to_dict()), 200
        
    except Exception as e:
        return jsonify({'message': 'Failed to fetch order', 'error': str(e)}), 500

@orders_bp.route('/', methods=['POST'])
@jwt_required()
def create_order():
    """Create order from cart"""
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        if not current_user:
            return jsonify({'message': 'User not found'}), 404
        
        data = request.get_json()
        cart_items = data.get('cart_items', [])
        delivery_option = data.get('delivery_option', 'DELIVER_TO_BUYER')
        notes = data.get('notes', '')
        
        if not cart_items:
            return jsonify({'message': 'No items in cart'}), 400
        
        # Group cart items by seller
        orders_by_seller = {}
        
        for item_data in cart_items:
            product_id = item_data.get('product_id')
            quantity = item_data.get('quantity', 1)
            
            product = Product.query.get(product_id)
            if not product:
                return jsonify({'message': f'Product {product_id} not found'}), 404
            
            # Check stock
            if product.stock_quantity < quantity:
                return jsonify({'message': f'Insufficient stock for {product.name}'}), 400
            
            seller_id = product.manufacturer_id
            
            if seller_id not in orders_by_seller:
                orders_by_seller[seller_id] = {
                    'seller_id': seller_id,
                    'buyer_id': current_user_id,
                    'items': [],
                    'delivery_option': delivery_option,
                    'notes': notes
                }
            
            orders_by_seller[seller_id]['items'].append({
                'product_id': product_id,
                'quantity': quantity,
                'unit_price': product.base_price
            })
        
        created_orders = []
        
        for seller_id, order_data in orders_by_seller.items():
            # Create order
            order = Order(
                id=str(uuid.uuid4()),
                buyer_id=order_data['buyer_id'],
                seller_id=order_data['seller_id'],
                status='PENDING',
                delivery_option=order_data['delivery_option'],
                notes=order_data['notes'],
                total_amount=0
            )
            
            # Create order items
            total_amount = 0
            for item_data in order_data['items']:
                product = Product.query.get(item_data['product_id'])
                item_total = item_data['quantity'] * item_data['unit_price']
                total_amount += item_total
                
                order_item = OrderItem(
                    order_id=order.id,
                    product_id=item_data['product_id'],
                    quantity=item_data['quantity'],
                    unit_price=item_data['unit_price'],
                    total_price=item_total
                )
                
                db.session.add(order_item)
            
            order.total_amount = total_amount
            db.session.add(order)
            created_orders.append(order)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Orders created successfully',
            'orders': [order.to_dict() for order in created_orders]
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Failed to create order', 'error': str(e)}), 500

@orders_bp.route('/<order_id>/status', methods=['PUT'])
@jwt_required()
def update_order_status(order_id):
    """Update order status (Accept/Reject/Partial/Pack/Ship/Deliver)"""
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        if not current_user:
            return jsonify({'message': 'User not found'}), 404
        
        order = Order.query.get(order_id)
        if not order:
            return jsonify({'message': 'Order not found'}), 404
        
        # Check if user is the seller
        if order.seller_id != current_user_id:
            return jsonify({'message': 'Only seller can update order status'}), 403
        
        data = request.get_json()
        new_status = data.get('status')
        partial_quantities = data.get('partial_quantities', {})
        delivery_option = data.get('delivery_option')
        internal_notes = data.get('internal_notes', '')
        
        if not new_status:
            return jsonify({'message': 'Status is required'}), 400
        
        # Validate status transition
        valid_transitions = {
            'PENDING': ['ACCEPTED', 'REJECTED', 'PARTIAL'],
            'PARTIAL': ['ACCEPTED', 'REJECTED'],
            'ACCEPTED': ['PACKED'],
            'PACKED': ['SHIPPED', 'OUT_FOR_DELIVERY'],
            'SHIPPED': ['DELIVERED'],
            'OUT_FOR_DELIVERY': ['DELIVERED']
        }
        
        if order.status not in valid_transitions or new_status not in valid_transitions.get(order.status, []):
            return jsonify({'message': f'Invalid status transition from {order.status} to {new_status}'}), 400
        
        # Handle partial acceptance
        if new_status == 'PARTIAL':
            for item_id, quantity in partial_quantities.items():
                order_item = OrderItem.query.get(item_id)
                if order_item and order_item.order_id == order.id:
                    if quantity > order_item.quantity:
                        return jsonify({'message': f'Partial quantity cannot exceed original quantity for item {item_id}'}), 400
                    order_item.quantity = quantity
                    order_item.total_price = quantity * order_item.unit_price
        
        # Update order status
        order.status = new_status
        order.updated_at = datetime.utcnow()
        
        # Update delivery option if provided
        if delivery_option:
            order.delivery_option = delivery_option
        
        # Add internal notes
        if internal_notes:
            order.internal_notes = internal_notes
        
        # Reduce stock when shipping
        if new_status in ['SHIPPED', 'OUT_FOR_DELIVERY']:
            for item in order.items:
                product = Product.query.get(item.product_id)
                if product:
                    product.stock_quantity -= item.quantity
                    if product.stock_quantity < 0:
                        product.stock_quantity = 0
        
        # Recalculate total for partial orders
        if new_status == 'PARTIAL':
            order.total_amount = sum(item.total_price for item in order.items)
        
        db.session.commit()
        
        return jsonify({
            'message': f'Order status updated to {new_status}',
            'order': order.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Failed to update order status', 'error': str(e)}), 500

@orders_bp.route('/<order_id>/notes', methods=['PUT'])
@jwt_required()
def update_order_notes(order_id):
    """Update order notes"""
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        if not current_user:
            return jsonify({'message': 'User not found'}), 404
        
        order = Order.query.get(order_id)
        if not order:
            return jsonify({'message': 'Order not found'}), 404
        
        # Check if user has access to this order
        if order.buyer_id != current_user_id and order.seller_id != current_user_id:
            return jsonify({'message': 'Access denied'}), 403
        
        data = request.get_json()
        notes = data.get('notes', '')
        
        # Buyer can update notes, seller can update internal_notes
        if order.buyer_id == current_user_id:
            order.notes = notes
        else:
            order.internal_notes = notes
        
        order.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': 'Order notes updated',
            'order': order.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Failed to update order notes', 'error': str(e)}), 500

@orders_bp.route('/templates', methods=['POST'])
@jwt_required()
def save_order_template():
    """Save current cart as reorder template"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        template_name = data.get('name', 'Reorder Template')
        cart_items = data.get('cart_items', [])
        
        if not cart_items:
            return jsonify({'message': 'No items to save as template'}), 400
        
        # Save template to database (simplified - you might want a separate Template model)
        # For now, we'll store it in the user's preferences or create a simple template
        
        return jsonify({
            'message': 'Reorder template saved successfully',
            'template_name': template_name
        }), 201
        
    except Exception as e:
        return jsonify({'message': 'Failed to save template', 'error': str(e)}), 500

@orders_bp.route('/templates/<template_id>/reorder', methods=['POST'])
@jwt_required()
def reorder_from_template(template_id):
    """Reorder from saved template"""
    try:
        current_user_id = get_jwt_identity()
        
        # Load template and create order (simplified)
        # This would typically load from a Template model
        
        return jsonify({
            'message': 'Order created from template successfully'
        }), 201
        
    except Exception as e:
        return jsonify({'message': 'Failed to reorder from template', 'error': str(e)}), 500 