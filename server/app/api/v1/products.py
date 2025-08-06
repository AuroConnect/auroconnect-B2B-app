from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models import Product, Category, Inventory
from app.utils.decorators import role_required
from sqlalchemy import or_

products_bp = Blueprint('products', __name__)

@products_bp.route('/', methods=['GET'])
def get_products():
    """Get all products"""
    try:
        category_id = request.args.get('categoryId')
        
        query = Product.query.filter_by(is_active=True)
        
        if category_id:
            query = query.filter_by(category_id=category_id)
        
        products = query.all()
        return jsonify([prod.to_dict() for prod in products]), 200
        
    except Exception as e:
        return jsonify({'message': 'Failed to fetch products', 'error': str(e)}), 500

@products_bp.route('/<product_id>', methods=['GET'])
def get_product(product_id):
    """Get specific product"""
    try:
        product = Product.query.get(product_id)
        
        if not product:
            return jsonify({'message': 'Product not found'}), 404
        
        return jsonify(product.to_dict()), 200
        
    except Exception as e:
        return jsonify({'message': 'Failed to fetch product', 'error': str(e)}), 500

@products_bp.route('/', methods=['POST'])
@jwt_required()
@role_required('manufacturer')
def create_product():
    """Create new product (manufacturers only)"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['name', 'sku']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'message': f'Missing required field: {field}'}), 400
        
        # Check if SKU already exists
        existing_product = Product.query.filter_by(sku=data['sku']).first()
        if existing_product:
            return jsonify({'message': 'Product with this SKU already exists'}), 409
        
        new_product = Product(
            name=data['name'],
            description=data.get('description'),
            sku=data['sku'],
            category_id=data.get('categoryId'),
            manufacturer_id=current_user_id,
            image_url=data.get('imageUrl'),
            base_price=data.get('basePrice'),
            is_active=True
        )
        
        db.session.add(new_product)
        db.session.commit()
        
        return jsonify(new_product.to_dict()), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Failed to create product', 'error': str(e)}), 500

@products_bp.route('/categories', methods=['GET'])
def get_categories():
    """Get all categories"""
    try:
        categories = Category.query.all()
        return jsonify([cat.to_dict() for cat in categories]), 200
        
    except Exception as e:
        return jsonify({'message': 'Failed to fetch categories', 'error': str(e)}), 500

@products_bp.route('/search', methods=['GET'])
def search_products():
    """Search products"""
    try:
        search_term = request.args.get('q', '')
        category_id = request.args.get('categoryId')
        
        query = Product.query.filter_by(is_active=True)
        
        if search_term:
            query = query.filter(
                or_(
                    Product.name.ilike(f'%{search_term}%'),
                    Product.description.ilike(f'%{search_term}%'),
                    Product.sku.ilike(f'%{search_term}%')
                )
            )
        
        if category_id:
            query = query.filter_by(category_id=category_id)
        
        products = query.all()
        return jsonify([prod.to_dict() for prod in products]), 200
        
    except Exception as e:
        return jsonify({'message': 'Failed to search products', 'error': str(e)}), 500 