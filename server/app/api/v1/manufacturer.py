from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models import User, Product, Order, PartnerLink
import pandas as pd
import io
import os
from werkzeug.utils import secure_filename

manufacturer_bp = Blueprint('manufacturer', __name__)

@manufacturer_bp.route('/dashboard', methods=['GET'])
@login_required
def dashboard():
    """Manufacturer dashboard"""
    if current_user.role != 'manufacturer':
        return jsonify({'message': 'Access denied'}), 403
    
    try:
        # Get manufacturer's products
        products = Product.query.filter_by(created_by=current_user.id, is_active=True).all()
        
        # Get pending orders from distributors
        pending_orders = Order.query.filter_by(
            seller_id=current_user.id,
            status='pending'
        ).all()
        
        # Get distributors
        distributor_links = PartnerLink.get_manufacturer_distributors(current_user.id)
        distributors = [link.distributor for link in distributor_links if link.distributor]
        
        return jsonify({
            'products': [p.to_dict() for p in products],
            'pendingOrders': [o.to_dict() for o in pending_orders],
            'distributors': [d.to_public_dict() for d in distributors]
        }), 200
        
    except Exception as e:
        return jsonify({'message': 'Failed to load dashboard', 'error': str(e)}), 500

@manufacturer_bp.route('/products', methods=['GET'])
@login_required
def get_products():
    """Get manufacturer's products"""
    if current_user.role != 'manufacturer':
        return jsonify({'message': 'Access denied'}), 403
    
    try:
        products = Product.query.filter_by(created_by=current_user.id, is_active=True).all()
        return jsonify([p.to_dict() for p in products]), 200
    except Exception as e:
        return jsonify({'message': 'Failed to fetch products', 'error': str(e)}), 500

@manufacturer_bp.route('/products', methods=['POST'])
@login_required
def add_product():
    """Add new product"""
    if current_user.role != 'manufacturer':
        return jsonify({'message': 'Access denied'}), 403
    
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['name', 'category', 'price', 'unit', 'stock']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'message': f'{field} is required'}), 400
        
        # Generate SKU if not provided
        sku = data.get('sku')
        if not sku:
            sku = Product.generate_sku()
        
        # Check if SKU already exists
        existing_product = Product.query.filter_by(sku=sku).first()
        if existing_product:
            return jsonify({'message': 'Product with this SKU already exists'}), 409
        
        new_product = Product(
            name=data['name'],
            sku=sku,
            category=data['category'],
            description=data.get('description'),
            price=data['price'],
            unit=data['unit'],
            stock=data['stock'],
            image_url=data.get('imageUrl'),
            created_by=current_user.id
        )
        
        db.session.add(new_product)
        db.session.commit()
        
        return jsonify(new_product.to_dict()), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Failed to add product', 'error': str(e)}), 500

@manufacturer_bp.route('/products/<product_id>', methods=['PUT'])
@login_required
def update_product(product_id):
    """Update product"""
    if current_user.role != 'manufacturer':
        return jsonify({'message': 'Access denied'}), 403
    
    try:
        product = Product.query.get(product_id)
        if not product or product.created_by != current_user.id:
            return jsonify({'message': 'Product not found'}), 404
        
        data = request.get_json()
        
        # Update fields
        if 'name' in data:
            product.name = data['name']
        if 'category' in data:
            product.category = data['category']
        if 'description' in data:
            product.description = data['description']
        if 'price' in data:
            product.price = data['price']
        if 'unit' in data:
            product.unit = data['unit']
        if 'stock' in data:
            product.stock = data['stock']
        if 'imageUrl' in data:
            product.image_url = data['imageUrl']
        
        db.session.commit()
        
        return jsonify(product.to_dict()), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Failed to update product', 'error': str(e)}), 500

@manufacturer_bp.route('/products/<product_id>', methods=['DELETE'])
@login_required
def delete_product(product_id):
    """Delete product"""
    if current_user.role != 'manufacturer':
        return jsonify({'message': 'Access denied'}), 403
    
    try:
        product = Product.query.get(product_id)
        if not product or product.created_by != current_user.id:
            return jsonify({'message': 'Product not found'}), 404
        
        product.is_active = False
        db.session.commit()
        
        return jsonify({'message': 'Product deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Failed to delete product', 'error': str(e)}), 500

@manufacturer_bp.route('/products/upload', methods=['POST'])
@login_required
def upload_products():
    """Upload products via Excel file"""
    if current_user.role != 'manufacturer':
        return jsonify({'message': 'Access denied'}), 403
    
    try:
        if 'file' not in request.files:
            return jsonify({'message': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'message': 'No file selected'}), 400
        
        if not file.filename.endswith('.xlsx'):
            return jsonify({'message': 'Please upload an Excel file (.xlsx)'}), 400
        
        # Read Excel file
        df = pd.read_excel(file)
        
        # Validate required columns
        required_columns = ['name', 'category', 'price', 'unit', 'stock']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            return jsonify({'message': f'Missing columns: {", ".join(missing_columns)}'}), 400
        
        added_count = 0
        failed_count = 0
        errors = []
        
        for index, row in df.iterrows():
            try:
                # Generate SKU if not provided
                sku = row.get('sku')
                if not sku:
                    sku = Product.generate_sku()
                
                # Check if SKU already exists
                existing_product = Product.query.filter_by(sku=sku).first()
                if existing_product:
                    failed_count += 1
                    errors.append(f"Row {index + 1}: SKU {sku} already exists")
                    continue
                
                new_product = Product(
                    name=row['name'],
                    sku=sku,
                    category=row['category'],
                    description=row.get('description', ''),
                    price=float(row['price']),
                    unit=row['unit'],
                    stock=int(row['stock']),
                    image_url=row.get('image_url', ''),
                    created_by=current_user.id
                )
                
                db.session.add(new_product)
                added_count += 1
                
            except Exception as e:
                failed_count += 1
                errors.append(f"Row {index + 1}: {str(e)}")
        
        db.session.commit()
        
        return jsonify({
            'message': f'{added_count} products added, {failed_count} failed',
            'addedCount': added_count,
            'failedCount': failed_count,
            'errors': errors
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Failed to upload products', 'error': str(e)}), 500

@manufacturer_bp.route('/orders', methods=['GET'])
@login_required
def get_orders():
    """Get manufacturer's orders"""
    if current_user.role != 'manufacturer':
        return jsonify({'message': 'Access denied'}), 403
    
    try:
        orders = Order.query.filter_by(seller_id=current_user.id).order_by(Order.created_at.desc()).all()
        return jsonify([o.to_dict() for o in orders]), 200
    except Exception as e:
        return jsonify({'message': 'Failed to fetch orders', 'error': str(e)}), 500

@manufacturer_bp.route('/orders/<order_id>/status', methods=['PUT'])
@login_required
def update_order_status(order_id):
    """Update order status"""
    if current_user.role != 'manufacturer':
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

@manufacturer_bp.route('/distributors', methods=['GET'])
@login_required
def get_distributors():
    """Get manufacturer's distributors"""
    if current_user.role != 'manufacturer':
        return jsonify({'message': 'Access denied'}), 403
    
    try:
        distributor_links = PartnerLink.get_manufacturer_distributors(current_user.id)
        distributors = [link.distributor for link in distributor_links if link.distributor]
        return jsonify([d.to_public_dict() for d in distributors]), 200
    except Exception as e:
        return jsonify({'message': 'Failed to fetch distributors', 'error': str(e)}), 500
