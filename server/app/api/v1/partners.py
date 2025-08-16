from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models import User, ProductAllocation, Partnership
from app.utils.decorators import role_required
from sqlalchemy import or_

partners_bp = Blueprint('partners', __name__)

@partners_bp.route('/', methods=['GET'])
@jwt_required()
def get_partners():
    """Get connected partners for current user"""
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        if not current_user:
            return jsonify({'message': 'User not found'}), 404
        
        # Get active partnerships
        partnerships = Partnership.query.filter(
            ((Partnership.requester_id == current_user_id) | 
             (Partnership.partner_id == current_user_id)) &
            (Partnership.status == 'active')
        ).all()
        
        connected_partners = []
        for partnership in partnerships:
            if partnership.requester_id == current_user_id:
                partner_user = User.query.get(partnership.partner_id)
            else:
                partner_user = User.query.get(partnership.requester_id)
            
            if partner_user:
                partner_data = partner_user.to_public_dict()
                partner_data['partnershipId'] = partnership.id
                partner_data['partnershipType'] = partnership.partnership_type
                connected_partners.append(partner_data)
        
        return jsonify(connected_partners), 200
        
    except Exception as e:
        return jsonify({'message': 'Failed to fetch partners', 'error': str(e)}), 500

@partners_bp.route('/available', methods=['GET'])
@jwt_required()
def get_available_partners():
    """Get available partners for partnership requests"""
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        if not current_user:
            return jsonify({'message': 'User not found'}), 404
        
        # Determine allowed roles based on user role
        allowed_roles = []
        if current_user.role == 'manufacturer':
            allowed_roles = ['distributor']
        elif current_user.role == 'distributor':
            allowed_roles = ['manufacturer']
        elif current_user.role == 'retailer':
            allowed_roles = ['distributor']
        
        # Get existing partnerships (both active and pending)
        existing_partnerships = Partnership.query.filter(
            ((Partnership.requester_id == current_user_id) | 
             (Partnership.partner_id == current_user_id))
        ).all()
        
        existing_partner_ids = []
        for partnership in existing_partnerships:
            if partnership.requester_id == current_user_id:
                existing_partner_ids.append(partnership.partner_id)
            else:
                existing_partner_ids.append(partnership.requester_id)
        
        # Get available partners (not already partnered)
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

@partners_bp.route('/requests', methods=['GET'])
@jwt_required()
def get_partnership_requests():
    """Get pending partnership requests for current user"""
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        if not current_user:
            return jsonify({'message': 'User not found'}), 404
        
        # Get pending requests where user is the partner (receiving requests)
        pending_requests = Partnership.query.filter_by(
            partner_id=current_user_id,
            status='pending'
        ).all()
        
        return jsonify([p.to_dict() for p in pending_requests]), 200
        
    except Exception as e:
        return jsonify({'message': 'Failed to fetch partnership requests', 'error': str(e)}), 500

@partners_bp.route('/distributors', methods=['GET'])
@jwt_required()
def get_distributors():
    """Get all distributors (for manufacturers to invite)"""
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        search = request.args.get('search', '')
        
        # Only manufacturers can see distributors for partnership
        if current_user.role != 'manufacturer':
            return jsonify([]), 200
        
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
def get_manufacturers():
    """Get all manufacturers (for distributors to request partnership)"""
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        search = request.args.get('search', '')
        
        # Only distributors can see manufacturers for partnership
        if current_user.role != 'distributor':
            return jsonify([]), 200
        
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

@partners_bp.route('/search', methods=['GET'])
@jwt_required()
def search_partners():
    """Search partners globally"""
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        search = request.args.get('search', '')
        
        if not current_user:
            return jsonify({'message': 'User not found'}), 404
        
        # Determine allowed roles based on user role
        allowed_roles = []
        if current_user.role == 'manufacturer':
            allowed_roles = ['distributor']
        elif current_user.role == 'distributor':
            allowed_roles = ['manufacturer']
        elif current_user.role == 'retailer':
            allowed_roles = ['distributor']
        
        # Search partners
        query = User.query.filter(
            User.role.in_(allowed_roles),
            User.is_active == True,
            User.id != current_user_id
        )
        
        if search:
            query = query.filter(
                or_(
                    User.business_name.ilike(f'%{search}%'),
                    User.email.ilike(f'%{search}%'),
                    User.first_name.ilike(f'%{search}%'),
                    User.last_name.ilike(f'%{search}%')
                )
            )
        
        partners = query.all()
        return jsonify([partner.to_public_dict() for partner in partners]), 200
        
    except Exception as e:
        return jsonify({'message': 'Failed to search partners', 'error': str(e)}), 500 