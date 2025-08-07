from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models import User, Product, Order, PartnerLink
from sqlalchemy import or_

distributor_bp = Blueprint('distributor', __name__)

@distributor_bp.route('/dashboard', methods=['GET'])
@login_required
def dashboard():
    """Distributor dashboard"""
    if current_user.role != 'distributor':
        return jsonify({'message': 'Access denied'}), 403
    
    try:
        # Get manufacturer's products
        manufacturer_link = PartnerLink.get_distributor_manufacturer(current_user.id)
        if not manufacturer_link:
            return jsonify({'message': 'No manufacturer connected'}), 404
        
        products = Product.query.filter_by(
            created_by=manufacturer_link.manufacturer_id,
            is_active=True
        ).all()
        
        # Get orders from retailers
        retailer_orders = Order.query.filter_by(
            seller_id=current_user.id,
            status='pending'
        ).all()
        
        # Get orders to manufacturer
        manufacturer_orders = Order.query.filter_by(
            buyer_id=current_user.id
        ).order_by(Order.created_at.desc()).all()
        
        # Get retailers
        retailer_links = PartnerLink.get_distributor_retailers(current_user.id)
        retailers = [link.retailer for link in retailer_links if link.retailer]
        
        return jsonify({
            'products': [p.to_dict() for p in products],
            'retailerOrders': [o.to_dict() for o in retailer_orders],
            'manufacturerOrders': [o.to_dict() for o in manufacturer_orders],
            'retailers': [r.to_public_dict() for r in retailers],
            'manufacturer': manufacturer_link.manufacturer.to_public_dict() if manufacturer_link.manufacturer else None
        }), 200
        
    except Exception as e:
        return jsonify({'message': 'Failed to load dashboard', 'error': str(e)}), 500

@distributor_bp.route('/products', methods=['GET'])
@login_required
def get_products():
    """Get manufacturer's products"""
    if current_user.role != 'distributor':
        return jsonify({'message': 'Access denied'}), 403
    
    try:
        manufacturer_link = PartnerLink.get_distributor_manufacturer(current_user.id)
        if not manufacturer_link:
            return jsonify({'message': 'No manufacturer connected'}), 404
        
        products = Product.query.filter_by(
            created_by=manufacturer_link.manufacturer_id,
            is_active=True
        ).all()
        
        return jsonify([p.to_dict() for p in products]), 200
    except Exception as e:
        return jsonify({'message': 'Failed to fetch products', 'error': str(e)}), 500

@distributor_bp.route('/orders', methods=['POST'])
@login_required
def place_order():
    """Place order to manufacturer"""
    if current_user.role != 'distributor':
        return jsonify({'message': 'Access denied'}), 403
    
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['productId', 'quantity']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'message': f'{field} is required'}), 400
        
        # Get manufacturer
        manufacturer_link = PartnerLink.get_distributor_manufacturer(current_user.id)
        if not manufacturer_link:
            return jsonify({'message': 'No manufacturer connected'}), 404
        
        # Check if product exists and belongs to manufacturer
        product = Product.query.get(data['productId'])
        if not product or product.created_by != manufacturer_link.manufacturer_id:
            return jsonify({'message': 'Product not found'}), 404
        
        # Check stock
        if product.stock < data['quantity']:
            return jsonify({'message': 'Insufficient stock'}), 400
        
        # Create order
        new_order = Order(
            buyer_id=current_user.id,
            seller_id=manufacturer_link.manufacturer_id,
            product_id=data['productId'],
            quantity=data['quantity'],
            status='pending',
            notes=data.get('notes')
        )
        
        db.session.add(new_order)
        db.session.commit()
        
        return jsonify(new_order.to_dict()), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Failed to place order', 'error': str(e)}), 500

@distributor_bp.route('/orders', methods=['GET'])
@login_required
def get_orders():
    """Get distributor's orders"""
    if current_user.role != 'distributor':
        return jsonify({'message': 'Access denied'}), 403
    
    try:
        # Get orders to manufacturer
        manufacturer_orders = Order.query.filter_by(buyer_id=current_user.id).order_by(Order.created_at.desc()).all()
        
        # Get orders from retailers
        retailer_orders = Order.query.filter_by(seller_id=current_user.id).order_by(Order.created_at.desc()).all()
        
        return jsonify({
            'manufacturerOrders': [o.to_dict() for o in manufacturer_orders],
            'retailerOrders': [o.to_dict() for o in retailer_orders]
        }), 200
    except Exception as e:
        return jsonify({'message': 'Failed to fetch orders', 'error': str(e)}), 500

@distributor_bp.route('/orders/<order_id>/status', methods=['PUT'])
@login_required
def update_order_status(order_id):
    """Update order status (for retailer orders)"""
    if current_user.role != 'distributor':
        return jsonify({'message': 'Access denied'}), 403
    
    try:
        order = Order.query.get(order_id)
        if not order or order.seller_id != current_user.id:
            return jsonify({'message': 'Order not found'}), 404
        
        data = request.get_json()
        new_status = data.get('status')
        delivery_method = data.get('deliveryMethod')
        delivery_address = data.get('deliveryAddress')
        
        if not new_status:
            return jsonify({'message': 'Status is required'}), 400
        
        # Validate status transition
        valid_transitions = {
            'pending': ['accepted', 'rejected'],
            'accepted': ['packed'],
            'packed': ['shipped'],
            'shipped': ['delivered']
        }
        
        if new_status not in valid_transitions.get(order.status, []):
            return jsonify({'message': f'Invalid status transition from {order.status} to {new_status}'}), 400
        
        order.status = new_status
        if delivery_method:
            order.delivery_method = delivery_method
        if delivery_address:
            order.delivery_address = delivery_address
        
        db.session.commit()
        
        return jsonify(order.to_dict()), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Failed to update order status', 'error': str(e)}), 500

@distributor_bp.route('/retailers', methods=['GET'])
@login_required
def get_retailers():
    """Get distributor's retailers"""
    if current_user.role != 'distributor':
        return jsonify({'message': 'Access denied'}), 403
    
    try:
        retailer_links = PartnerLink.get_distributor_retailers(current_user.id)
        retailers = [link.retailer for link in retailer_links if link.retailer]
        return jsonify([r.to_public_dict() for r in retailers]), 200
    except Exception as e:
        return jsonify({'message': 'Failed to fetch retailers', 'error': str(e)}), 500

@distributor_bp.route('/manufacturer', methods=['GET'])
@login_required
def get_manufacturer():
    """Get distributor's manufacturer"""
    if current_user.role != 'distributor':
        return jsonify({'message': 'Access denied'}), 403
    
    try:
        manufacturer_link = PartnerLink.get_distributor_manufacturer(current_user.id)
        if not manufacturer_link or not manufacturer_link.manufacturer:
            return jsonify({'message': 'No manufacturer connected'}), 404
        
        return jsonify(manufacturer_link.manufacturer.to_public_dict()), 200
    except Exception as e:
        return jsonify({'message': 'Failed to fetch manufacturer', 'error': str(e)}), 500
