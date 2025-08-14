from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.user import User
from app.models.product import Product
from app.models.inventory import Inventory
from app import db

my_products_bp = Blueprint('my_products', __name__)

@my_products_bp.route('/', methods=['GET'])
@jwt_required()
def get_my_products():
    """Get products owned by the current user"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'message': 'User not found'}), 404
        
        # Only manufacturers and distributors can access this endpoint
        if user.role not in ['manufacturer', 'distributor']:
            return jsonify({'message': 'Access denied'}), 403
        
        # Get products owned by the current user
        query = Product.query.filter_by(
            manufacturer_id=current_user_id,
            is_active=True
        )
        
        # Apply filters
        category_id = request.args.get('categoryId')
        if category_id:
            query = query.filter_by(category_id=category_id)
        
        products = query.all()
        products_with_details = []
        
        for product in products:
            product_dict = product.to_dict()
            
            # Get inventory info
            inventory = Inventory.query.filter_by(
                distributor_id=current_user_id,
                product_id=product.id
            ).first()
            
            product_dict['availableStock'] = inventory.quantity if inventory else 0
            product_dict['sellingPrice'] = float(product.base_price) if product.base_price else 0
            product_dict['isAllocated'] = False  # These are own products, not allocated
            product_dict['manufacturerName'] = user.business_name
            product_dict['category'] = product.category.to_dict() if product.category else None
            
            products_with_details.append(product_dict)
        
        return jsonify(products_with_details), 200
        
    except Exception as e:
        return jsonify({'message': 'Failed to fetch products', 'error': str(e)}), 500
