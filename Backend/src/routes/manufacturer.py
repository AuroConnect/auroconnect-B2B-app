from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from models import db
from models.user import User
from models.product import Product, ProductCategoryEnum
from models.inventory import Inventory
from models.order import Order, OrderItem
from datetime import datetime
import os

manufacturer_bp = Blueprint('manufacturer', __name__)

# Helper function to check if user is manufacturer
def check_manufacturer():
    if not current_user.is_manufacturer():
        return jsonify({'error': {'code': 'UNAUTHORIZED', 'message': 'Access denied. Manufacturer role required.'}}), 403
    return None

@manufacturer_bp.route('/products', methods=['GET'])
@login_required
def list_products():
    """Get list of all products for manufacturer"""
    # Check if user is manufacturer
    error = check_manufacturer()
    if error:
        return error
    
    try:
        # Get query parameters
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        search = request.args.get('search', '', type=str)
        category = request.args.get('category', '', type=str)
        sort = request.args.get('sort', 'created_at', type=str)
        order = request.args.get('order', 'desc', type=str)
        
        # Build query
        query = Product.query.filter_by(manufacturer_id=current_user.id)
        
        # Apply search filter
        if search:
            search_filter = f"%{search}%"
            query = query.filter(
                db.or_(
                    Product.name.ilike(search_filter),
                    Product.description.ilike(search_filter),
                    Product.sku.ilike(search_filter)
                )
            )
        
        # Apply category filter
        if category:
            try:
                category_enum = ProductCategoryEnum(category)
                query = query.filter_by(category=category_enum)
            except ValueError:
                pass  # Invalid category, ignore filter
        
        # Apply sorting
        if sort == 'name':
            query = query.order_by(Product.name.asc() if order == 'asc' else Product.name.desc())
        elif sort == 'price':
            query = query.order_by(Product.price.asc() if order == 'asc' else Product.price.desc())
        else:  # default to created_at
            query = query.order_by(Product.created_at.asc() if order == 'asc' else Product.created_at.desc())
        
        # Paginate results
        products = query.paginate(page=page, per_page=per_page, error_out=False)
        
        return jsonify({
            'data': [product.to_dict() for product in products.items],
            'meta': {
                'pagination': {
                    'page': page,
                    'per_page': per_page,
                    'total': products.total,
                    'pages': products.pages
                }
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': {'code': 'LIST_PRODUCTS_ERROR', 'message': 'Failed to list products', 'details': str(e)}}), 500

@manufacturer_bp.route('/products', methods=['POST'])
@login_required
def create_product():
    """Create a new product"""
    # Check if user is manufacturer
    error = check_manufacturer()
    if error:
        return error
    
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['name', 'description', 'category', 'price']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({'error': {'code': 'MISSING_FIELD', 'message': f'{field} is required'}}), 400
        
        # Validate category
        try:
            category_enum = ProductCategoryEnum(data['category'])
        except ValueError:
            return jsonify({'error': {'code': 'INVALID_CATEGORY', 'message': 'Invalid category'}}), 400
        
        # Validate price
        try:
            price = float(data['price'])
            if price <= 0:
                return jsonify({'error': {'code': 'INVALID_PRICE', 'message': 'Price must be positive'}}), 400
        except (ValueError, TypeError):
            return jsonify({'error': {'code': 'INVALID_PRICE', 'message': 'Invalid price format'}}), 400
        
        # Create new product
        product = Product(
            name=data['name'],
            description=data['description'],
            category=category_enum,
            price=price,
            manufacturer_id=current_user.id,
            sku=data.get('sku'),
            image_url=data.get('image_url')
        )
        
        # Add to database
        db.session.add(product)
        db.session.commit()
        
        return jsonify({
            'data': product.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': {'code': 'CREATE_PRODUCT_ERROR', 'message': 'Failed to create product', 'details': str(e)}}), 500

@manufacturer_bp.route('/products/<int:product_id>', methods=['GET'])
@login_required
def get_product(product_id):
    """Get details of a specific product"""
    # Check if user is manufacturer
    error = check_manufacturer()
    if error:
        return error
    
    try:
        # Get product and ensure it belongs to current manufacturer
        product = Product.query.filter_by(id=product_id, manufacturer_id=current_user.id).first()
        if not product:
            return jsonify({'error': {'code': 'PRODUCT_NOT_FOUND', 'message': 'Product not found'}}), 404
        
        return jsonify({
            'data': product.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': {'code': 'GET_PRODUCT_ERROR', 'message': 'Failed to get product', 'details': str(e)}}), 500

@manufacturer_bp.route('/products/<int:product_id>', methods=['PUT'])
@login_required
def update_product(product_id):
    """Update an existing product"""
    # Check if user is manufacturer
    error = check_manufacturer()
    if error:
        return error
    
    try:
        # Get product and ensure it belongs to current manufacturer
        product = Product.query.filter_by(id=product_id, manufacturer_id=current_user.id).first()
        if not product:
            return jsonify({'error': {'code': 'PRODUCT_NOT_FOUND', 'message': 'Product not found'}}), 404
        
        data = request.get_json()
        
        # Update fields if provided
        if 'name' in data:
            product.name = data['name']
        if 'description' in data:
            product.description = data['description']
        if 'category' in data:
            try:
                product.category = ProductCategoryEnum(data['category'])
            except ValueError:
                return jsonify({'error': {'code': 'INVALID_CATEGORY', 'message': 'Invalid category'}}), 400
        if 'price' in data:
            try:
                price = float(data['price'])
                if price <= 0:
                    return jsonify({'error': {'code': 'INVALID_PRICE', 'message': 'Price must be positive'}}), 400
                product.price = price
            except (ValueError, TypeError):
                return jsonify({'error': {'code': 'INVALID_PRICE', 'message': 'Invalid price format'}}), 400
        if 'sku' in data:
            product.sku = data['sku']
        if 'image_url' in data:
            product.image_url = data['image_url']
        
        product.updated_at = datetime.utcnow()
        
        # Commit changes
        db.session.commit()
        
        return jsonify({
            'data': product.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': {'code': 'UPDATE_PRODUCT_ERROR', 'message': 'Failed to update product', 'details': str(e)}}), 500

@manufacturer_bp.route('/products/<int:product_id>', methods=['DELETE'])
@login_required
def delete_product(product_id):
    """Delete a product"""
    # Check if user is manufacturer
    error = check_manufacturer()
    if error:
        return error
    
    try:
        # Get product and ensure it belongs to current manufacturer
        product = Product.query.filter_by(id=product_id, manufacturer_id=current_user.id).first()
        if not product:
            return jsonify({'error': {'code': 'PRODUCT_NOT_FOUND', 'message': 'Product not found'}}), 404
        
        # Delete product (will cascade delete related inventories and order items)
        db.session.delete(product)
        db.session.commit()
        
        return jsonify({
            'data': {'message': 'Product deleted successfully'}
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': {'code': 'DELETE_PRODUCT_ERROR', 'message': 'Failed to delete product', 'details': str(e)}}), 500

@manufacturer_bp.route('/inventory/assign', methods=['POST'])
@login_required
def assign_inventory():
    """Assign products to distributors"""
    # Check if user is manufacturer
    error = check_manufacturer()
    if error:
        return error
    
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['product_id', 'distributor_id', 'quantity']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': {'code': 'MISSING_FIELD', 'message': f'{field} is required'}}), 400
        
        # Validate quantity
        try:
            quantity = int(data['quantity'])
            if quantity <= 0:
                return jsonify({'error': {'code': 'INVALID_QUANTITY', 'message': 'Quantity must be positive'}}), 400
        except (ValueError, TypeError):
            return jsonify({'error': {'code': 'INVALID_QUANTITY', 'message': 'Invalid quantity format'}}), 400
        
        # Check if product belongs to manufacturer
        product = Product.query.filter_by(id=data['product_id'], manufacturer_id=current_user.id).first()
        if not product:
            return jsonify({'error': {'code': 'PRODUCT_NOT_FOUND', 'message': 'Product not found or not owned by manufacturer'}}), 404
        
        # Check if distributor exists and is actually a distributor
        distributor = User.query.filter_by(id=data['distributor_id']).first()
        if not distributor or not distributor.is_distributor():
            return jsonify({'error': {'code': 'INVALID_DISTRIBUTOR', 'message': 'Invalid distributor'}}), 400
        
        # Check if inventory assignment already exists
        inventory = Inventory.query.filter_by(
            product_id=data['product_id'],
            distributor_id=data['distributor_id']
        ).first()
        
        if inventory:
            # Update existing inventory
            inventory.quantity = quantity
            inventory.last_updated = datetime.utcnow()
        else:
            # Create new inventory assignment
            inventory = Inventory(
                product_id=data['product_id'],
                distributor_id=data['distributor_id'],
                quantity=quantity
            )
            db.session.add(inventory)
        
        # Commit changes
        db.session.commit()
        
        return jsonify({
            'data': inventory.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': {'code': 'ASSIGN_INVENTORY_ERROR', 'message': 'Failed to assign inventory', 'details': str(e)}}), 500

@manufacturer_bp.route('/orders', methods=['GET'])
@login_required
def list_orders():
    """Get all downstream orders"""
    # Check if user is manufacturer
    error = check_manufacturer()
    if error:
        return error
    
    try:
        # Get query parameters
        distributor_id = request.args.get('distributor_id', type=int)
        product_id = request.args.get('product_id', type=int)
        status = request.args.get('status', '', type=str)
        start_date = request.args.get('start_date', '', type=str)
        end_date = request.args.get('end_date', '', type=str)
        
        # Build query for orders related to manufacturer's products
        query = db.session.query(Order).join(OrderItem).join(Product).filter(
            Product.manufacturer_id == current_user.id
        ).distinct()
        
        # Apply filters
        if distributor_id:
            query = query.filter(Order.distributor_id == distributor_id)
        
        if product_id:
            query = query.filter(OrderItem.product_id == product_id)
        
        if status:
            query = query.filter(Order.status == status)
        
        if start_date:
            try:
                start_datetime = datetime.fromisoformat(start_date)
                query = query.filter(Order.created_at >= start_datetime)
            except ValueError:
                pass  # Invalid date format, ignore filter
        
        if end_date:
            try:
                end_datetime = datetime.fromisoformat(end_date)
                query = query.filter(Order.created_at <= end_datetime)
            except ValueError:
                pass  # Invalid date format, ignore filter
        
        # Order by creation date
        query = query.order_by(Order.created_at.desc())
        
        # Execute query
        orders = query.all()
        
        return jsonify({
            'data': [order.to_dict() for order in orders]
        }), 200
        
    except Exception as e:
        return jsonify({'error': {'code': 'LIST_ORDERS_ERROR', 'message': 'Failed to list orders', 'details': str(e)}}), 500