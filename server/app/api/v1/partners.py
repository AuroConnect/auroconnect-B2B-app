from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models import User
from app.utils.decorators import role_required
from sqlalchemy import or_

partners_bp = Blueprint('partners', __name__)

@partners_bp.route('/distributors', methods=['GET'])
@jwt_required()
def get_distributors():
    """Get all distributors"""
    try:
        current_user_id = get_jwt_identity()
        search = request.args.get('search', '')
        
        query = User.query.filter_by(role='distributor', is_active=True)
        
        if search:
            query = query.filter(
                or_(
                    User.business_name.ilike(f'%{search}%'),
                    User.email.ilike(f'%{search}%'),
                    User.first_name.ilike(f'%{search}%'),
                    User.last_name.ilike(f'%{search}%')
                )
            )
        
        distributors = query.all()
        return jsonify([dist.to_public_dict() for dist in distributors]), 200
        
    except Exception as e:
        return jsonify({'message': 'Failed to fetch distributors', 'error': str(e)}), 500

@partners_bp.route('/manufacturers', methods=['GET'])
@jwt_required()
@role_required('distributor')
def get_manufacturers():
    """Get all manufacturers (distributors only)"""
    try:
        search = request.args.get('search', '')
        
        query = User.query.filter_by(role='manufacturer', is_active=True)
        
        if search:
            query = query.filter(
                or_(
                    User.business_name.ilike(f'%{search}%'),
                    User.email.ilike(f'%{search}%'),
                    User.first_name.ilike(f'%{search}%'),
                    User.last_name.ilike(f'%{search}%')
                )
            )
        
        manufacturers = query.all()
        return jsonify([man.to_public_dict() for man in manufacturers]), 200
        
    except Exception as e:
        return jsonify({'message': 'Failed to fetch manufacturers', 'error': str(e)}), 500

@partners_bp.route('/available', methods=['GET'])
@jwt_required()
def get_available_partners():
    """Get available partners for current user"""
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        if not current_user:
            return jsonify({'message': 'User not found'}), 404
        
        # Determine allowed roles based on user role
        allowed_roles = []
        if current_user.role == 'retailer':
            allowed_roles = ['distributor']
        elif current_user.role == 'distributor':
            allowed_roles = ['retailer', 'manufacturer']
        elif current_user.role == 'manufacturer':
            allowed_roles = ['distributor']
        
        # Get existing partnerships
        from app.models import Partnership
        existing_partnerships = Partnership.query.filter_by(requester_id=current_user_id).all()
        existing_partner_ids = [str(p.partner_id) for p in existing_partnerships]
        
        # Get available partners
        query = User.query.filter(
            User.role.in_(allowed_roles),
            User.is_active == True,
            User.id != current_user_id
        )
        
        if existing_partner_ids:
            query = query.filter(~User.id.in_(existing_partner_ids))
        
        available_partners = query.all()
        
        return jsonify([partner.to_public_dict() for partner in available_partners]), 200
        
    except Exception as e:
        return jsonify({'message': 'Failed to fetch available partners', 'error': str(e)}), 500

@partners_bp.route('/search', methods=['GET'])
@jwt_required()
def search_partners():
    """Search partners globally"""
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        product = request.args.get('product')
        
        if not current_user:
            return jsonify({'message': 'User not found'}), 404
        
        if product:
            # Search partners by product (simplified implementation)
            allowed_roles = []
            if current_user.role == 'retailer':
                allowed_roles = ['distributor']
            elif current_user.role == 'distributor':
                allowed_roles = ['manufacturer']
            
            partners = User.query.filter(
                User.role.in_(allowed_roles),
                User.is_active == True,
                User.id != current_user_id
            ).all()
            
            return jsonify([partner.to_public_dict() for partner in partners]), 200
        else:
            # Get all global partners
            allowed_roles = []
            if current_user.role == 'retailer':
                allowed_roles = ['distributor']
            elif current_user.role == 'distributor':
                allowed_roles = ['retailer', 'manufacturer']
            elif current_user.role == 'manufacturer':
                allowed_roles = ['distributor']
            
            partners = User.query.filter(
                User.role.in_(allowed_roles),
                User.is_active == True
            ).all()
            
            return jsonify([partner.to_public_dict() for partner in partners]), 200
        
    except Exception as e:
        return jsonify({'message': 'Failed to search partners', 'error': str(e)}), 500 