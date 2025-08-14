from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.user import User
from app.models.product import Product
from app.models.partnership import Partnership
from app.models.product_allocation import ProductAllocation
from app.utils.decorators import roles_required
from app import db
from datetime import datetime
import uuid

product_allocations_bp = Blueprint('product_allocations_v1', __name__)

@product_allocations_bp.route('/', methods=['GET'])
@jwt_required()
def get_product_allocations():
    """Get product allocations for current user"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'message': 'User not found'}), 404
        
        allocations = []
        
        if user.role == 'manufacturer':
            # Get allocations where user is manufacturer
            allocations = ProductAllocation.query.filter_by(
                manufacturer_id=current_user_id,
                is_active=True
            ).all()
        elif user.role == 'distributor':
            # Get allocations where user is distributor
            allocations = ProductAllocation.query.filter_by(
                distributor_id=current_user_id,
                is_active=True
            ).all()
        
        return jsonify([a.to_dict() for a in allocations]), 200
        
    except Exception as e:
        return jsonify({'message': 'Failed to fetch product allocations', 'error': str(e)}), 500

@product_allocations_bp.route('/', methods=['POST'])
@jwt_required()
@roles_required(['manufacturer'])
def create_product_allocation():
    """Create a new product allocation (manufacturers only)"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'message': 'User not found'}), 404
        
        data = request.get_json()
        distributor_id = data.get('distributorId')
        product_id = data.get('productId')
        allocated_quantity = data.get('allocatedQuantity', 0)
        selling_price = data.get('sellingPrice')
        
        if not distributor_id or not product_id or not selling_price:
            return jsonify({'message': 'Distributor ID, product ID, and selling price are required'}), 400
        
        # Verify distributor exists and is a distributor
        distributor = User.query.get(distributor_id)
        if not distributor or distributor.role != 'distributor':
            return jsonify({'message': 'Invalid distributor'}), 400
        
        # Verify product exists and belongs to manufacturer
        product = Product.query.get(product_id)
        if not product or product.manufacturer_id != current_user_id:
            return jsonify({'message': 'Product not found or access denied'}), 404
        
        # Verify partnership exists
        partnership = Partnership.query.filter_by(
            requester_id=current_user_id,
            partner_id=distributor_id,
            partnership_type='MANUFACTURER_DISTRIBUTOR',
            status='active'
        ).first()
        
        if not partnership:
            return jsonify({'message': 'No active partnership with this distributor'}), 400
        
        # Check if allocation already exists
        existing_allocation = ProductAllocation.query.filter_by(
            manufacturer_id=current_user_id,
            distributor_id=distributor_id,
            product_id=product_id
        ).first()
        
        if existing_allocation:
            return jsonify({'message': 'Product allocation already exists'}), 409
        
        # Create new allocation
        new_allocation = ProductAllocation(
            manufacturer_id=current_user_id,
            distributor_id=distributor_id,
            product_id=product_id,
            allocated_quantity=allocated_quantity,
            selling_price=selling_price,
            is_active=True
        )
        
        db.session.add(new_allocation)
        db.session.commit()
        
        return jsonify(new_allocation.to_dict()), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Failed to create product allocation', 'error': str(e)}), 500

@product_allocations_bp.route('/<allocation_id>', methods=['PUT'])
@jwt_required()
def update_product_allocation(allocation_id):
    """Update product allocation"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'message': 'User not found'}), 404
        
        allocation = ProductAllocation.query.get(allocation_id)
        if not allocation:
            return jsonify({'message': 'Product allocation not found'}), 404
        
        # Check if user is the manufacturer of this allocation
        if allocation.manufacturer_id != current_user_id:
            return jsonify({'message': 'Access denied'}), 403
        
        data = request.get_json()
        
        if 'allocatedQuantity' in data:
            allocation.allocated_quantity = data['allocatedQuantity']
        if 'sellingPrice' in data:
            allocation.selling_price = data['sellingPrice']
        if 'isActive' in data:
            allocation.is_active = data['isActive']
        
        allocation.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify(allocation.to_dict()), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Failed to update product allocation', 'error': str(e)}), 500

@product_allocations_bp.route('/<allocation_id>', methods=['DELETE'])
@jwt_required()
def delete_product_allocation(allocation_id):
    """Delete product allocation"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'message': 'User not found'}), 404
        
        allocation = ProductAllocation.query.get(allocation_id)
        if not allocation:
            return jsonify({'message': 'Product allocation not found'}), 404
        
        # Check if user is the manufacturer of this allocation
        if allocation.manufacturer_id != current_user_id:
            return jsonify({'message': 'Access denied'}), 403
        
        db.session.delete(allocation)
        db.session.commit()
        
        return jsonify({'message': 'Product allocation deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Failed to delete product allocation', 'error': str(e)}), 500
