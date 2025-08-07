from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models import User, Product, Order, PartnerLink
from datetime import datetime
import csv
import io

retailer_bp = Blueprint('retailer', __name__)

@retailer_bp.route('/dashboard', methods=['GET'])
@login_required
def dashboard():
    """Retailer dashboard"""
    if current_user.role != 'retailer':
        return jsonify({'message': 'Access denied'}), 403
    
    try:
        # Get distributor's products
        distributor_link = PartnerLink.get_retailer_distributor(current_user.id)
        if not distributor_link:
            return jsonify({'message': 'No distributor connected'}), 404
        
        products = Product.query.filter_by(
            created_by=distributor_link.distributor_id,
            is_active=True
        ).all()
        
        # Get retailer's orders
        orders = Order.query.filter_by(buyer_id=current_user.id).order_by(Order.created_at.desc()).all()
        
        return jsonify({
            'products': [p.to_dict() for p in products],
            'orders': [o.to_dict() for o in orders],
            'distributor': distributor_link.distributor.to_public_dict() if distributor_link.distributor else None
        }), 200
        
    except Exception as e:
        return jsonify({'message': 'Failed to load dashboard', 'error': str(e)}), 500

@retailer_bp.route('/products', methods=['GET'])
@login_required
def get_products():
    """Get distributor's products"""
    if current_user.role != 'retailer':
        return jsonify({'message': 'Access denied'}), 403
    
    try:
        distributor_link = PartnerLink.get_retailer_distributor(current_user.id)
        if not distributor_link:
            return jsonify({'message': 'No distributor connected'}), 404
        
        products = Product.query.filter_by(
            created_by=distributor_link.distributor_id,
            is_active=True
        ).all()
        
        return jsonify([p.to_dict() for p in products]), 200
    except Exception as e:
        return jsonify({'message': 'Failed to fetch products', 'error': str(e)}), 500

@retailer_bp.route('/orders', methods=['POST'])
@login_required
def place_order():
    """Place order to distributor"""
    if current_user.role != 'retailer':
        return jsonify({'message': 'Access denied'}), 403
    
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['productId', 'quantity']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'message': f'{field} is required'}), 400
        
        # Get distributor
        distributor_link = PartnerLink.get_retailer_distributor(current_user.id)
        if not distributor_link:
            return jsonify({'message': 'No distributor connected'}), 404
        
        # Check if product exists and belongs to distributor
        product = Product.query.get(data['productId'])
        if not product or product.created_by != distributor_link.distributor_id:
            return jsonify({'message': 'Product not found'}), 404
        
        # Check stock
        if product.stock < data['quantity']:
            return jsonify({'message': 'Insufficient stock'}), 400
        
        # Create order
        new_order = Order(
            buyer_id=current_user.id,
            seller_id=distributor_link.distributor_id,
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

@retailer_bp.route('/orders', methods=['GET'])
@login_required
def get_orders():
    """Get retailer's orders"""
    if current_user.role != 'retailer':
        return jsonify({'message': 'Access denied'}), 403
    
    try:
        orders = Order.query.filter_by(buyer_id=current_user.id).order_by(Order.created_at.desc()).all()
        return jsonify([o.to_dict() for o in orders]), 200
    except Exception as e:
        return jsonify({'message': 'Failed to fetch orders', 'error': str(e)}), 500

@retailer_bp.route('/orders/<order_id>', methods=['GET'])
@login_required
def get_order(order_id):
    """Get specific order"""
    if current_user.role != 'retailer':
        return jsonify({'message': 'Access denied'}), 403
    
    try:
        order = Order.query.get(order_id)
        if not order or order.buyer_id != current_user.id:
            return jsonify({'message': 'Order not found'}), 404
        
        return jsonify(order.to_dict()), 200
    except Exception as e:
        return jsonify({'message': 'Failed to fetch order', 'error': str(e)}), 500

@retailer_bp.route('/orders/<order_id>/delivered', methods=['PUT'])
@login_required
def mark_delivered(order_id):
    """Mark order as delivered"""
    if current_user.role != 'retailer':
        return jsonify({'message': 'Access denied'}), 403
    
    try:
        order = Order.query.get(order_id)
        if not order or order.buyer_id != current_user.id:
            return jsonify({'message': 'Order not found'}), 404
        
        if order.status != 'shipped':
            return jsonify({'message': 'Order must be shipped before marking as delivered'}), 400
        
        order.status = 'delivered'
        db.session.commit()
        
        return jsonify(order.to_dict()), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Failed to update order status', 'error': str(e)}), 500

@retailer_bp.route('/distributor', methods=['GET'])
@login_required
def get_distributor():
    """Get retailer's distributor"""
    if current_user.role != 'retailer':
        return jsonify({'message': 'Access denied'}), 403
    
    try:
        distributor_link = PartnerLink.get_retailer_distributor(current_user.id)
        if not distributor_link or not distributor_link.distributor:
            return jsonify({'message': 'No distributor connected'}), 404
        
        return jsonify(distributor_link.distributor.to_public_dict()), 200
    except Exception as e:
        return jsonify({'message': 'Failed to fetch distributor', 'error': str(e)}), 500

@retailer_bp.route('/reports/monthly', methods=['GET'])
@login_required
def monthly_report():
    """Generate monthly report"""
    if current_user.role != 'retailer':
        return jsonify({'message': 'Access denied'}), 403
    
    try:
        month = request.args.get('month')
        year = request.args.get('year')
        
        if not month or not year:
            return jsonify({'message': 'Month and year are required'}), 400
        
        # Get orders for the specified month
        start_date = datetime(int(year), int(month), 1)
        if int(month) == 12:
            end_date = datetime(int(year) + 1, 1, 1)
        else:
            end_date = datetime(int(year), int(month) + 1, 1)
        
        orders = Order.query.filter(
            Order.buyer_id == current_user.id,
            Order.created_at >= start_date,
            Order.created_at < end_date
        ).order_by(Order.created_at.desc()).all()
        
        # Generate CSV
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow([
            'Order ID', 'Product', 'Quantity', 'Total Price', 
            'Status', 'Order Date', 'Delivery Method', 'Notes'
        ])
        
        # Write data
        for order in orders:
            total_price = order.get_total_price()
            writer.writerow([
                order.id,
                order.product.name if order.product else 'N/A',
                order.quantity,
                f"${total_price:.2f}",
                order.status,
                order.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                order.delivery_method or 'N/A',
                order.notes or ''
            ])
        
        csv_content = output.getvalue()
        output.close()
        
        return jsonify({
            'csvContent': csv_content,
            'orderCount': len(orders),
            'month': month,
            'year': year
        }), 200
        
    except Exception as e:
        return jsonify({'message': 'Failed to generate report', 'error': str(e)}), 500
