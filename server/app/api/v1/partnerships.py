from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models import Partnership, User
from app.utils.decorators import validate_json

partnerships_bp = Blueprint('partnerships', __name__)

@partnerships_bp.route('/', methods=['GET'])
@jwt_required()
def get_partnerships():
    """Get user partnerships"""
    try:
        current_user_id = get_jwt_identity()
        
        partnerships = Partnership.query.filter_by(requester_id=current_user_id).all()
        return jsonify([partnership.to_dict() for partnership in partnerships]), 200
        
    except Exception as e:
        return jsonify({'message': 'Failed to fetch partnerships', 'error': str(e)}), 500

@partnerships_bp.route('/request', methods=['POST'])
@jwt_required()
@validate_json
def send_partnership_request():
    """Send partnership request"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        partner_id = data.get('partnerId')
        partnership_type = data.get('partnershipType')
        
        if not partner_id or not partnership_type:
            return jsonify({'message': 'Partner ID and partnership type are required'}), 400
        
        # Check if request already exists
        existing_request = Partnership.query.filter_by(
            requester_id=current_user_id,
            partner_id=partner_id
        ).first()
        
        if existing_request:
            return jsonify({'message': 'Partnership request already exists'}), 400
        
        # Verify partner exists
        partner = User.query.get(partner_id)
        if not partner:
            return jsonify({'message': 'Partner not found'}), 404
        
        new_partnership = Partnership(
            requester_id=current_user_id,
            partner_id=partner_id,
            partnership_type=partnership_type,
            status='pending'
        )
        
        db.session.add(new_partnership)
        db.session.commit()
        
        return jsonify(new_partnership.to_dict()), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Failed to send partnership request', 'error': str(e)}), 500

@partnerships_bp.route('/<partnership_id>/respond', methods=['PATCH'])
@jwt_required()
@validate_json
def respond_to_partnership(partnership_id):
    """Respond to partnership request"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        status = data.get('status')
        
        if status not in ['approved', 'rejected']:
            return jsonify({'message': 'Invalid status'}), 400
        
        partnership = Partnership.query.get(partnership_id)
        
        if not partnership:
            return jsonify({'message': 'Partnership request not found'}), 404
        
        # Only the partner can respond to the request
        if str(partnership.partner_id) != current_user_id:
            return jsonify({'message': 'Unauthorized'}), 403
        
        partnership.status = status
        db.session.commit()
        
        return jsonify(partnership.to_dict()), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Failed to respond to partnership request', 'error': str(e)}), 500

@partnerships_bp.route('/received', methods=['GET'])
@jwt_required()
def get_received_partnerships():
    """Get received partnership requests"""
    try:
        current_user_id = get_jwt_identity()
        
        partnerships = Partnership.query.filter_by(partner_id=current_user_id).all()
        return jsonify([partnership.to_dict() for partnership in partnerships]), 200
        
    except Exception as e:
        return jsonify({'message': 'Failed to fetch received partnerships', 'error': str(e)}), 500 