from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.product import Product
from app.models.user import User
from app.models.partnership import PartnerLink
from app import db
from app.utils.decorators import validate_json

products_bp = Blueprint('products', __name__)

@products_bp.route('/', methods=['GET'])
@jwt_required()
def get_products():
    """Get products based on user role and partnerships"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Get query parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        category = request.args.get('category')
        search = request.args.get('search')
        
        # Build query based on user role
        query = Product.query
        
        if user.role == 'manufacturer':
            # Manufacturers see only their own products
            query = query.filter(Product.created_by == current_user_id)
            
        elif user.role == 'distributor':
            # Distributors see products from their manufacturer
            manufacturer_link = PartnerLink.get_distributor_manufacturer(current_user_id)
            if manufacturer_link and manufacturer_link.manufacturer_id:
                query = query.filter(Product.created_by == manufacturer_link.manufacturer_id)
            else:
                # If no manufacturer link, return empty results
                query = query.filter(Product.id.is_(None))  # This will return empty results
                
        elif user.role == 'retailer':
            # Retailers see products from their distributor
            distributor_link = PartnerLink.get_retailer_distributor(current_user_id)
            if distributor_link and distributor_link.distributor_id:
                # Get the manufacturer of the distributor to show their products
                distributor_manufacturer_link = PartnerLink.get_distributor_manufacturer(distributor_link.distributor_id)
                if distributor_manufacturer_link and distributor_manufacturer_link.manufacturer_id:
                    query = query.filter(Product.created_by == distributor_manufacturer_link.manufacturer_id)
                else:
                    # If no manufacturer link, return empty results
                    query = query.filter(Product.id.is_(None))
            else:
                # If no distributor link, return empty results
                query = query.filter(Product.id.is_(None))
        
        # Apply category filter
        if category:
            query = query.filter(Product.category == category)
        
        # Apply search filter
        if search:
            query = query.filter(
                Product.name.ilike(f'%{search}%') |
                Product.description.ilike(f'%{search}%')
            )
        
        # Paginate results
        products = query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        
        return jsonify({
            'message': 'Products retrieved successfully',
            'data': {
                'products': [product.to_dict() for product in products.items],
                'pagination': {
                    'page': page,
                    'per_page': per_page,
                    'total': products.total,
                    'pages': products.pages,
                    'has_next': products.has_next,
                    'has_prev': products.has_prev
                }
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@products_bp.route('/<int:product_id>', methods=['GET'])
@jwt_required()
def get_product(product_id):
    """Get a specific product based on user role and partnerships"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        product = Product.query.get(product_id)
        
        if not product:
            return jsonify({'error': 'Product not found'}), 404
        
        # Check access based on user role
        if user.role == 'manufacturer':
            # Manufacturers can only see their own products
            if product.created_by != current_user_id:
                return jsonify({'error': 'Product not found'}), 404
                
        elif user.role == 'distributor':
            # Distributors can only see products from their manufacturer
            manufacturer_link = PartnerLink.get_distributor_manufacturer(current_user_id)
            if not manufacturer_link or manufacturer_link.manufacturer_id != product.created_by:
                return jsonify({'error': 'Product not found'}), 404
                
        elif user.role == 'retailer':
            # Retailers can only see products from their distributor's manufacturer
            distributor_link = PartnerLink.get_retailer_distributor(current_user_id)
            if distributor_link and distributor_link.distributor_id:
                distributor_manufacturer_link = PartnerLink.get_distributor_manufacturer(distributor_link.distributor_id)
                if not distributor_manufacturer_link or distributor_manufacturer_link.manufacturer_id != product.created_by:
                    return jsonify({'error': 'Product not found'}), 404
            else:
                return jsonify({'error': 'Product not found'}), 404
        
        return jsonify({
            'message': 'Product retrieved successfully',
            'data': product.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@products_bp.route('/', methods=['POST'])
@jwt_required()
@validate_json(['name', 'description', 'price', 'category'])
def create_product():
    """Create a new product"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user or user.role != 'manufacturer':
            return jsonify({'error': 'Only manufacturers can create products'}), 403
        
        data = request.get_json()
        
        # Generate SKU if not provided
        sku = data.get('sku') or Product.generate_sku()
        
        product = Product(
            name=data['name'],
            sku=sku,
            description=data.get('description', ''),
            price=data['price'],
            category=data['category'],
            created_by=current_user_id,
            stock=data.get('stock_quantity', 0) or data.get('stock', 0),
            unit=data.get('unit', 'piece'),
            is_active=data.get('is_active', True)
        )
        
        db.session.add(product)
        db.session.commit()
        
        return jsonify({
            'message': 'Product created successfully',
            'data': product.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@products_bp.route('/<int:product_id>', methods=['PUT'])
@jwt_required()
def update_product(product_id):
    """Update a product"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        product = Product.query.get(product_id)
        
        if not product:
            return jsonify({'error': 'Product not found'}), 404
        
        # Only manufacturer can update their own products
        if user.role != 'manufacturer' or product.manufacturer_id != current_user_id:
            return jsonify({'error': 'Unauthorized to update this product'}), 403
        
        data = request.get_json()
        
        # Update fields
        if 'name' in data:
            product.name = data['name']
        if 'description' in data:
            product.description = data['description']
        if 'price' in data:
            product.price = data['price']
        if 'category' in data:
            product.category = data['category']
        if 'stock_quantity' in data:
            product.stock_quantity = data['stock_quantity']
        if 'unit' in data:
            product.unit = data['unit']
        if 'min_order_quantity' in data:
            product.min_order_quantity = data['min_order_quantity']
        
        db.session.commit()
        
        return jsonify({
            'message': 'Product updated successfully',
            'data': product.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@products_bp.route('/<int:product_id>', methods=['DELETE'])
@jwt_required()
def delete_product(product_id):
    """Delete a product"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        product = Product.query.get(product_id)
        
        if not product:
            return jsonify({'error': 'Product not found'}), 404
        
        # Only manufacturer can delete their own products
        if user.role != 'manufacturer' or product.manufacturer_id != current_user_id:
            return jsonify({'error': 'Unauthorized to delete this product'}), 403
        
        db.session.delete(product)
        db.session.commit()
        
        return jsonify({
            'message': 'Product deleted successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@products_bp.route('/categories', methods=['GET'])
@jwt_required()
def get_categories():
    """Get all product categories"""
    try:
        categories = db.session.query(Product.category).distinct().all()
        category_list = [category[0] for category in categories if category[0]]
        
        return jsonify({
            'message': 'Categories retrieved successfully',
            'data': category_list
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
