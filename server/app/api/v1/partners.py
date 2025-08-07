from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models import User, Partnership
from app.utils.decorators import role_required, roles_required
from sqlalchemy import or_

partners_bp = Blueprint('partners', __name__)

@partners_bp.route('/', methods=['GET'])
@jwt_required()
def get_partners():
    """Get partners based on user role and partnerships"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'message': 'User not found'}), 404
        
        # Role-based partner visibility
        if user.role == 'manufacturer':
            # Manufacturers see their distributors
            partnerships = Partnership.get_manufacturer_distributors(current_user_id)
            partners = [partnership.distributor for partnership in partnerships if partnership.distributor]
            
        elif user.role == 'distributor':
            # Distributors see their manufacturer and retailers
            manufacturer_partnership = Partnership.get_distributor_manufacturer(current_user_id)
            retailer_partnerships = Partnership.get_distributor_retailers(current_user_id)
            
            partners = []
            if manufacturer_partnership and manufacturer_partnership.manufacturer:
                partners.append({
                    'id': manufacturer_partnership.manufacturer.id,
                    'business_name': manufacturer_partnership.manufacturer.business_name,
                    'email': manufacturer_partnership.manufacturer.email,
                    'phone_number': manufacturer_partnership.manufacturer.phone_number,
                    'address': manufacturer_partnership.manufacturer.address,
                    'role': 'manufacturer',
                    'partnership_type': 'manufacturer_distributor',
                    'status': manufacturer_partnership.status
                })
            
            for partnership in retailer_partnerships:
                if partnership.retailer:
                    partners.append({
                        'id': partnership.retailer.id,
                        'business_name': partnership.retailer.business_name,
                        'email': partnership.retailer.email,
                        'phone_number': partnership.retailer.phone_number,
                        'address': partnership.retailer.address,
                        'role': 'retailer',
                        'partnership_type': 'distributor_retailer',
                        'status': partnership.status
                    })
            
        elif user.role == 'retailer':
            # Retailers see their distributor
            distributor_partnership = Partnership.get_retailer_distributor(current_user_id)
            partners = []
            
            if distributor_partnership and distributor_partnership.distributor:
                partners.append({
                    'id': distributor_partnership.distributor.id,
                    'business_name': distributor_partnership.distributor.business_name,
                    'email': distributor_partnership.distributor.email,
                    'phone_number': distributor_partnership.distributor.phone_number,
                    'address': distributor_partnership.distributor.address,
                    'role': 'distributor',
                    'partnership_type': 'distributor_retailer',
                    'status': distributor_partnership.status
                })
            
        else:
            return jsonify({'message': 'Invalid user role'}), 400
        
        return jsonify(partners), 200
        
    except Exception as e:
        return jsonify({'message': 'Failed to fetch partners', 'error': str(e)}), 500

@partners_bp.route('/<partner_id>', methods=['GET'])
@jwt_required()
def get_partner_details(partner_id):
    """Get detailed partner information with role-based access control"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'message': 'User not found'}), 404
        
        partner = User.query.get(partner_id)
        if not partner:
            return jsonify({'message': 'Partner not found'}), 404
        
        # Check if user has access to this partner
        if user.role == 'manufacturer':
            # Manufacturers can only see their distributors
            partnership = Partnership.query.filter_by(
                manufacturer_id=current_user_id,
                distributor_id=partner_id,
                partnership_type='manufacturer_distributor',
                status='active'
            ).first()
            
            if not partnership:
                return jsonify({'message': 'Access denied'}), 403
                
        elif user.role == 'distributor':
            # Distributors can see their manufacturer and retailers
            manufacturer_partnership = Partnership.query.filter_by(
                distributor_id=current_user_id,
                manufacturer_id=partner_id,
                partnership_type='manufacturer_distributor',
                status='active'
            ).first()
            
            retailer_partnership = Partnership.query.filter_by(
                distributor_id=current_user_id,
                retailer_id=partner_id,
                partnership_type='distributor_retailer',
                status='active'
            ).first()
            
            if not manufacturer_partnership and not retailer_partnership:
                return jsonify({'message': 'Access denied'}), 403
                
        elif user.role == 'retailer':
            # Retailers can only see their distributor
            partnership = Partnership.query.filter_by(
                retailer_id=current_user_id,
                distributor_id=partner_id,
                partnership_type='distributor_retailer',
                status='active'
            ).first()
            
            if not partnership:
                return jsonify({'message': 'Access denied'}), 403
        
        return jsonify(partner.to_dict()), 200
        
    except Exception as e:
        return jsonify({'message': 'Failed to fetch partner details', 'error': str(e)}), 500

@partners_bp.route('/', methods=['POST'])
@jwt_required()
def create_partnership():
    """Create new partnership (for connecting users)"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        data = request.get_json()
        
        if not user:
            return jsonify({'message': 'User not found'}), 404
        
        partner_id = data.get('partner_id')
        partnership_type = data.get('partnership_type')
        
        if not partner_id or not partnership_type:
            return jsonify({'message': 'Partner ID and partnership type are required'}), 400
        
        partner = User.query.get(partner_id)
        if not partner:
            return jsonify({'message': 'Partner not found'}), 404
        
        # Validate partnership type based on user role
        if user.role == 'manufacturer':
            if partnership_type != 'manufacturer_distributor':
                return jsonify({'message': 'Manufacturers can only create manufacturer-distributor partnerships'}), 400
            if partner.role != 'distributor':
                return jsonify({'message': 'Can only partner with distributors'}), 400
                
        elif user.role == 'distributor':
            if partnership_type not in ['manufacturer_distributor', 'distributor_retailer']:
                return jsonify({'message': 'Invalid partnership type'}), 400
            if partnership_type == 'manufacturer_distributor' and partner.role != 'manufacturer':
                return jsonify({'message': 'Can only partner with manufacturers'}), 400
            if partnership_type == 'distributor_retailer' and partner.role != 'retailer':
                return jsonify({'message': 'Can only partner with retailers'}), 400
                
        elif user.role == 'retailer':
            if partnership_type != 'distributor_retailer':
                return jsonify({'message': 'Retailers can only create distributor-retailer partnerships'}), 400
            if partner.role != 'distributor':
                return jsonify({'message': 'Can only partner with distributors'}), 400
        
        # Check if partnership already exists
        existing_partnership = Partnership.query.filter_by(
            partnership_type=partnership_type,
            status='active'
        ).filter(
            db.or_(
                db.and_(Partnership.manufacturer_id == current_user_id, Partnership.distributor_id == partner_id),
                db.and_(Partnership.distributor_id == current_user_id, Partnership.manufacturer_id == partner_id),
                db.and_(Partnership.distributor_id == current_user_id, Partnership.retailer_id == partner_id),
                db.and_(Partnership.retailer_id == current_user_id, Partnership.distributor_id == partner_id)
            )
        ).first()
        
        if existing_partnership:
            return jsonify({'message': 'Partnership already exists'}), 409
        
        # Create partnership
        if partnership_type == 'manufacturer_distributor':
            if user.role == 'manufacturer':
                partnership = Partnership(
                    partnership_type=partnership_type,
                    manufacturer_id=current_user_id,
                    distributor_id=partner_id,
                    status='active'
                )
            else:
                partnership = Partnership(
                    partnership_type=partnership_type,
                    manufacturer_id=partner_id,
                    distributor_id=current_user_id,
                    status='active'
                )
        else:  # distributor_retailer
            if user.role == 'distributor':
                partnership = Partnership(
                    partnership_type=partnership_type,
                    distributor_id=current_user_id,
                    retailer_id=partner_id,
                    status='active'
                )
            else:
                partnership = Partnership(
                    partnership_type=partnership_type,
                    distributor_id=partner_id,
                    retailer_id=current_user_id,
                    status='active'
                )
        
        db.session.add(partnership)
        db.session.commit()
        
        return jsonify(partnership.to_dict()), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Failed to create partnership', 'error': str(e)}), 500

@partners_bp.route('/<partnership_id>', methods=['PUT'])
@jwt_required()
def update_partnership(partnership_id):
    """Update partnership status"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        data = request.get_json()
        
        if not user:
            return jsonify({'message': 'User not found'}), 404
        
        partnership = Partnership.query.get(partnership_id)
        if not partnership:
            return jsonify({'message': 'Partnership not found'}), 404
        
        # Check if user has access to this partnership
        if user.role == 'manufacturer':
            if partnership.manufacturer_id != current_user_id:
                return jsonify({'message': 'Access denied'}), 403
        elif user.role == 'distributor':
            if partnership.distributor_id != current_user_id:
                return jsonify({'message': 'Access denied'}), 403
        elif user.role == 'retailer':
            if partnership.retailer_id != current_user_id:
                return jsonify({'message': 'Access denied'}), 403
        
        # Update partnership status
        new_status = data.get('status')
        if new_status and new_status in ['active', 'inactive', 'pending']:
            partnership.status = new_status
            db.session.commit()
        
        return jsonify(partnership.to_dict()), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Failed to update partnership', 'error': str(e)}), 500

@partners_bp.route('/<partnership_id>', methods=['DELETE'])
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
        
        # Check if user has access to this partnership
        if user.role == 'manufacturer':
            if partnership.manufacturer_id != current_user_id:
                return jsonify({'message': 'Access denied'}), 403
        elif user.role == 'distributor':
            if partnership.distributor_id != current_user_id:
                return jsonify({'message': 'Access denied'}), 403
        elif user.role == 'retailer':
            if partnership.retailer_id != current_user_id:
                return jsonify({'message': 'Access denied'}), 403
        
        # Soft delete by setting status to inactive
        partnership.status = 'inactive'
        db.session.commit()
        
        return jsonify({'message': 'Partnership deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Failed to delete partnership', 'error': str(e)}), 500 