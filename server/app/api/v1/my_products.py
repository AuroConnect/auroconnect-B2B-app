from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.user import User
from app.models.product import Product
from app.models.inventory import Inventory
from app.models.product_allocation import ProductAllocation
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
        distributor_id = request.args.get('distributorId')
        
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
            
            # Get assigned distributors for this product
            allocations = ProductAllocation.query.filter_by(
                product_id=product.id,
                is_active=True
            ).all()
            
            assigned_distributors = []
            for allocation in allocations:
                distributor = User.query.get(allocation.distributor_id)
                if distributor:
                    assigned_distributors.append({
                        'id': str(distributor.id),
                        'name': distributor.business_name or f"{distributor.first_name} {distributor.last_name}",
                        'email': distributor.email
                    })
            
            # Filter by distributor if specified
            if distributor_id and distributor_id != 'all':
                if not any(d['id'] == distributor_id for d in assigned_distributors):
                    continue  # Skip this product if it's not assigned to the specified distributor
            
            product_dict['availableStock'] = inventory.quantity if inventory else 0
            product_dict['sellingPrice'] = float(product.base_price) if product.base_price else 0
            product_dict['isAllocated'] = False  # These are own products, not allocated
            product_dict['manufacturerName'] = user.business_name
            product_dict['category'] = product.category.to_dict() if product.category else None
            product_dict['assignedDistributors'] = assigned_distributors
            
            products_with_details.append(product_dict)
        
        return jsonify(products_with_details), 200
        
    except Exception as e:
        return jsonify({'message': 'Failed to fetch products', 'error': str(e)}), 500
