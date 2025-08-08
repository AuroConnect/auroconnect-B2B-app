from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import User, Order, OrderItem, Product, PartnerLink, Inventory
from app import db
from datetime import datetime, timedelta
from sqlalchemy import and_

orders_bp = Blueprint('orders', __name__)

@orders_bp.route('/', methods=['GET'])
@jwt_required()
def get_orders():
    """Get orders based on user role and partnerships"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'message': 'User not found'}), 404
        
        # Get query parameters
        status_filter = request.args.get('status')
        
        # Role-based order visibility
        if user.role == 'manufacturer':
            # Manufacturers see orders where they are the seller
            orders = Order.query.filter_by(seller_id=current_user_id).all()
            
        elif user.role == 'distributor':
            # Distributors see orders where they are either buyer or seller
            orders = Order.query.filter(
                (Order.buyer_id == current_user_id) | (Order.seller_id == current_user_id)
            ).all()
            
        elif user.role == 'retailer':
            # Retailers see orders where they are the buyer
            orders = Order.query.filter_by(buyer_id=current_user_id).all()
            
        else:
            return jsonify({'message': 'Invalid user role'}), 400
        
        # Apply filters
        if status_filter and status_filter != 'all':
            orders = [order for order in orders if order.status == status_filter]
        
        return jsonify([order.to_dict() for order in orders]), 200
        
    except Exception as e:
        return jsonify({'message': 'Failed to fetch orders', 'error': str(e)}), 500

@orders_bp.route('/<order_id>', methods=['GET'])
@jwt_required()
def get_order_details(order_id):
    """Get detailed order information with role-based access control"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'message': 'User not found'}), 404
        
        order = Order.query.get(order_id)
        if not order:
            return jsonify({'message': 'Order not found'}), 404
        
        # Role-based access control
        if user.role == 'manufacturer':
            if order.manufacturer_id != current_user_id:
                return jsonify({'message': 'Access denied'}), 403
                
        elif user.role == 'distributor':
            if order.distributor_id != current_user_id:
                return jsonify({'message': 'Access denied'}), 403
                
        elif user.role == 'retailer':
            if order.retailer_id != current_user_id:
                return jsonify({'message': 'Access denied'}), 403
        
        return jsonify(order.to_dict()), 200
        
    except Exception as e:
        return jsonify({'message': 'Failed to fetch order details', 'error': str(e)}), 500

@orders_bp.route('/', methods=['POST'])
@jwt_required()
def create_order():
    """Create new order based on user role"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        data = request.get_json()
        
        if not user:
            return jsonify({'message': 'User not found'}), 404
        
        # Validate required fields
        required_fields = ['items', 'delivery_address']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'message': f'Missing required field: {field}'}), 400
        
        items = data.get('items', [])
        if not items:
            return jsonify({'message': 'Order must contain at least one item'}), 400
        
        # Role-based order creation
        if user.role == 'distributor':
            # Distributor ordering from manufacturer
            manufacturer_partnership = PartnerLink.get_distributor_manufacturer(current_user_id)
            if not manufacturer_partnership:
                return jsonify({'message': 'No manufacturer connected'}), 400
            
            order = Order(
                order_type='manufacturer_distributor',
                manufacturer_id=manufacturer_partnership.manufacturer_id,
                distributor_id=current_user_id,
                order_number=Order.generate_order_number(),
                delivery_address=data['delivery_address'],
                delivery_method=data.get('delivery_method', 'delivery'),
                notes=data.get('notes'),
                status='pending'
            )
            
        elif user.role == 'retailer':
            # Retailer ordering from distributor
            distributor_partnership = PartnerLink.get_retailer_distributor(current_user_id)
            if not distributor_partnership:
                return jsonify({'message': 'No distributor connected'}), 400
            
            order = Order(
                order_type='distributor_retailer',
                distributor_id=distributor_partnership.distributor_id,
                retailer_id=current_user_id,
                order_number=Order.generate_order_number(),
                delivery_address=data['delivery_address'],
                delivery_method=data.get('delivery_method', 'delivery'),
                notes=data.get('notes'),
                status='pending'
            )
            
        else:
            return jsonify({'message': 'Manufacturers cannot create orders'}), 400
        
        # Calculate totals
        subtotal = 0
        order_items = []
        
        for item_data in items:
            product_id = item_data.get('product_id')
            quantity = item_data.get('quantity', 0)
            
            if not product_id or quantity <= 0:
                continue
            
            product = Product.query.get(product_id)
            if not product:
                continue
            
            # Get unit price based on user role
            unit_price = product.base_price
            if user.role == 'retailer':
                # For retailers, get price from distributor's inventory
                inventory_item = Inventory.query.filter_by(
                    distributor_id=distributor_partnership.distributor_id,
                    product_id=product_id
                ).first()
                if inventory_item and inventory_item.selling_price:
                    unit_price = inventory_item.selling_price
            
            total_price = unit_price * quantity
            subtotal += total_price
            
            order_item = OrderItem(
                order_id=order.id,
                product_id=product_id,
                quantity=quantity,
                unit_price=unit_price,
                total_price=total_price,
                product_name=product.name,
                product_sku=product.sku
            )
            order_items.append(order_item)
        
        if not order_items:
            return jsonify({'message': 'No valid items in order'}), 400
        
        # Set order totals
        tax_amount = data.get('tax_amount', 0)
        shipping_amount = data.get('shipping_amount', 0)
        order.total_amount = subtotal + tax_amount + shipping_amount
        order.tax_amount = tax_amount
        order.shipping_amount = shipping_amount
        
        # Save order and items
        db.session.add(order)
        for item in order_items:
            db.session.add(item)
        
        db.session.commit()
        
        return jsonify(order.to_dict()), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Failed to create order', 'error': str(e)}), 500

@orders_bp.route('/<order_id>/status', methods=['PUT'])
@jwt_required()
def update_order_status(order_id):
    """Update order status (manufacturers and distributors)"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'message': 'User not found'}), 404
        
        if user.role not in ['manufacturer', 'distributor']:
            return jsonify({'message': 'Only manufacturers and distributors can update order status'}), 403
        
        data = request.get_json()
        new_status = data.get('status')
        notes = data.get('notes')
        
        if not new_status:
            return jsonify({'message': 'Status is required'}), 400
        
        valid_statuses = ['pending', 'accepted', 'processing', 'shipped', 'delivered', 'cancelled']
        if new_status not in valid_statuses:
            return jsonify({'message': f'Invalid status. Must be one of: {", ".join(valid_statuses)}'}), 400
        
        order = Order.query.get(order_id)
        if not order:
            return jsonify({'message': 'Order not found'}), 404
        
        # Check if user has access to this order
        if user.role == 'manufacturer':
            if order.manufacturer_id != current_user_id:
                return jsonify({'message': 'Access denied'}), 403
        elif user.role == 'distributor':
            if order.distributor_id != current_user_id:
                return jsonify({'message': 'Access denied'}), 403
        
        # Update order status
        order.status = new_status
        if notes:
            order.notes = notes
        
        # Set delivery date if status is delivered
        if new_status == 'delivered':
            order.actual_delivery_date = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify(order.to_dict()), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Failed to update order status', 'error': str(e)}), 500

@orders_bp.route('/<order_id>/tracking', methods=['PUT'])
@jwt_required()
def update_tracking_info(order_id):
    """Update tracking information for shipped orders"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'message': 'User not found'}), 404
        
        if user.role not in ['manufacturer', 'distributor']:
            return jsonify({'message': 'Only manufacturers and distributors can update tracking'}), 403
        
        data = request.get_json()
        tracking_number = data.get('tracking_number')
        expected_delivery_date = data.get('expected_delivery_date')
        
        order = Order.query.get(order_id)
        if not order:
            return jsonify({'message': 'Order not found'}), 404
        
        # Check if user has access to this order
        if user.role == 'manufacturer':
            if order.manufacturer_id != current_user_id:
                return jsonify({'message': 'Access denied'}), 403
        elif user.role == 'distributor':
            if order.distributor_id != current_user_id:
                return jsonify({'message': 'Access denied'}), 403
        
        # Update tracking information
        if tracking_number:
            order.tracking_number = tracking_number
        
        if expected_delivery_date:
            try:
                order.expected_delivery_date = datetime.fromisoformat(expected_delivery_date.replace('Z', '+00:00'))
            except ValueError:
                return jsonify({'message': 'Invalid date format'}), 400
        
        db.session.commit()
        
        return jsonify(order.to_dict()), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Failed to update tracking information', 'error': str(e)}), 500 