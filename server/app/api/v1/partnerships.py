from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.user import User
from app.models.partnership import Partnership
from app.utils.decorators import roles_required
from app import db
from datetime import datetime
import uuid

partnerships_bp = Blueprint('partnerships_v1', __name__)

@partnerships_bp.route('/', methods=['GET'])
@jwt_required()
def get_partnerships():
    """Get partnerships for current user"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'message': 'User not found'}), 404
        
        partnerships = []
        
        if user.role == 'manufacturer':
            # Get partnerships where user is manufacturer
            partnerships = Partnership.query.filter_by(
                manufacturer_id=current_user_id,
                status='ACTIVE'
            ).all()
        elif user.role == 'distributor':
            # Get partnerships where user is distributor
            partnerships = Partnership.query.filter(
                (Partnership.distributor_id == current_user_id) &
                (Partnership.status == 'ACTIVE')
            ).all()
        elif user.role == 'retailer':
            # Get partnerships where user is retailer
            partnerships = Partnership.query.filter_by(
                retailer_id=current_user_id,
                status='ACTIVE'
            ).all()
        
        return jsonify([p.to_dict() for p in partnerships]), 200
        
    except Exception as e:
        return jsonify({'message': 'Failed to fetch partnerships', 'error': str(e)}), 500

@partnerships_bp.route('/', methods=['POST'])
@jwt_required()
@roles_required(['manufacturer', 'distributor'])
def create_partnership():
    """Create a new partnership"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'message': 'User not found'}), 404
        
        data = request.get_json()
        partner_id = data.get('partnerId')
        partnership_type = data.get('partnershipType')
        
        if not partner_id or not partnership_type:
            return jsonify({'message': 'Partner ID and partnership type are required'}), 400
        
        partner = User.query.get(partner_id)
        if not partner:
            return jsonify({'message': 'Partner not found'}), 404
        
        # Validate partnership type based on user role
        if user.role == 'manufacturer':
            if partnership_type != 'MANUFACTURER_DISTRIBUTOR':
                return jsonify({'message': 'Manufacturers can only create partnerships with distributors'}), 400
            if partner.role != 'distributor':
                return jsonify({'message': 'Can only partner with distributors'}), 400
        elif user.role == 'distributor':
            if partnership_type != 'DISTRIBUTOR_RETAILER':
                return jsonify({'message': 'Distributors can only create partnerships with retailers'}), 400
            if partner.role != 'retailer':
                return jsonify({'message': 'Can only partner with retailers'}), 400
        
        # Check if partnership already exists
        existing_partnership = None
        if user.role == 'manufacturer':
            existing_partnership = Partnership.query.filter_by(
                manufacturer_id=current_user_id,
                distributor_id=partner_id,
                partnership_type=partnership_type
            ).first()
        elif user.role == 'distributor':
            existing_partnership = Partnership.query.filter_by(
                distributor_id=current_user_id,
                retailer_id=partner_id,
                partnership_type=partnership_type
            ).first()
        
        if existing_partnership:
            return jsonify({'message': 'Partnership already exists'}), 409
        
        # Create new partnership
        new_partnership = Partnership(
            manufacturer_id=current_user_id if user.role == 'manufacturer' else None,
            distributor_id=current_user_id if user.role == 'distributor' else partner_id if user.role == 'manufacturer' else None,
            retailer_id=partner_id if user.role == 'distributor' else None,
            partnership_type=partnership_type,
            status='ACTIVE'
        )
        
        db.session.add(new_partnership)
        db.session.commit()
        
        return jsonify(new_partnership.to_dict()), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Failed to create partnership', 'error': str(e)}), 500

@partnerships_bp.route('/<partnership_id>', methods=['PUT'])
@jwt_required()
def update_partnership(partnership_id):
    """Update partnership status"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'message': 'User not found'}), 404
        
        partnership = Partnership.query.get(partnership_id)
        if not partnership:
            return jsonify({'message': 'Partnership not found'}), 404
        
        # Check if user is part of this partnership
        if (partnership.manufacturer_id != current_user_id and 
            partnership.distributor_id != current_user_id and 
            partnership.retailer_id != current_user_id):
            return jsonify({'message': 'Access denied'}), 403
        
        data = request.get_json()
        status = data.get('status')
        
        if status and status in ['ACTIVE', 'INACTIVE', 'PENDING']:
            partnership.status = status
            partnership.updated_at = datetime.utcnow()
            db.session.commit()
        
        return jsonify(partnership.to_dict()), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Failed to update partnership', 'error': str(e)}), 500

@partnerships_bp.route('/<partnership_id>', methods=['DELETE'])
@jwt_required()
def delete_partnership(partnership_id):
    """Delete partnership"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'message': 'User not found'}), 404
        
        partnership = Partnership.query.get(partnership_id)
        if not partnership:
            return jsonify({'message': 'Partnership not found'}), 404
        
        # Check if user is part of this partnership
        if (partnership.manufacturer_id != current_user_id and 
            partnership.distributor_id != current_user_id and 
            partnership.retailer_id != current_user_id):
            return jsonify({'message': 'Access denied'}), 403
        
        db.session.delete(partnership)
        db.session.commit()
        
        return jsonify({'message': 'Partnership deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Failed to delete partnership', 'error': str(e)}), 500 