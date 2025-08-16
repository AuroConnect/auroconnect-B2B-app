from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.user import User
from app.models.partnership import Partnership, PartnershipInvite
from app.utils.decorators import role_required
from app.utils.email_sender import email_sender
from app import db
from datetime import datetime, timedelta
import uuid
import secrets
import string

partnerships_bp = Blueprint('partnerships_v1', __name__)

def generate_invite_token():
    """Generate a secure invite token"""
    return ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(32))

@partnerships_bp.route('/', methods=['GET'])
@jwt_required()
def get_partnerships():
    """Get partnerships for current user"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'message': 'User not found'}), 404
        
        # Get partnerships where user is either requester or partner
        partnerships = Partnership.query.filter(
            ((Partnership.requester_id == current_user_id) | 
             (Partnership.partner_id == current_user_id)) &
            (Partnership.status == 'active')
        ).all()
        
        return jsonify([p.to_dict() for p in partnerships]), 200
        
    except Exception as e:
        return jsonify({'message': 'Failed to fetch partnerships', 'error': str(e)}), 500

@partnerships_bp.route('/requests', methods=['GET'])
@jwt_required()
def get_partnership_requests():
    """Get pending partnership requests for current user"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'message': 'User not found'}), 404
        
        # Get pending requests where user is the partner (receiving requests)
        pending_requests = Partnership.query.filter_by(
            partner_id=current_user_id,
            status='pending'
        ).all()
        
        return jsonify([p.to_dict() for p in pending_requests]), 200
        
    except Exception as e:
        return jsonify({'message': 'Failed to fetch partnership requests', 'error': str(e)}), 500

@partnerships_bp.route('/invites', methods=['GET'])
@jwt_required()
def get_partnership_invites():
    """Get partnership invitations for current user"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'message': 'User not found'}), 404
        
        # Get pending invitations sent by current user
        sent_invites = PartnershipInvite.query.filter_by(
            inviter_id=current_user_id,
            status='pending'
        ).all()
        
        # Get pending invitations received by current user (by email)
        received_invites = PartnershipInvite.query.filter_by(
            invitee_email=user.email,
            status='pending'
        ).all()
        
        return jsonify({
            'sent_invites': [invite.to_dict() for invite in sent_invites],
            'received_invites': [invite.to_dict() for invite in received_invites]
        }), 200
        
    except Exception as e:
        return jsonify({'message': 'Failed to fetch partnership invites', 'error': str(e)}), 500

@partnerships_bp.route('/send-invite', methods=['POST'])
@jwt_required()
def send_partnership_invite():
    """Send partnership invitation by email (both manufacturer and distributor can send)"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'message': 'User not found'}), 404
        
        data = request.get_json()
        invitee_email = data.get('inviteeEmail')
        invitee_role = data.get('inviteeRole')  # manufacturer or distributor
        message = data.get('message', '')
        
        if not invitee_email:
            return jsonify({'message': 'Invitee email is required'}), 400
        
        if not invitee_role or invitee_role not in ['manufacturer', 'distributor']:
            return jsonify({'message': 'Valid invitee role (manufacturer or distributor) is required'}), 400
        
        # Check if user is trying to invite themselves
        if invitee_email.lower() == user.email.lower():
            return jsonify({'message': 'You cannot invite yourself'}), 400
        
        # Check if there's already a pending invitation
        existing_invite = PartnershipInvite.query.filter_by(
            inviter_id=current_user_id,
            invitee_email=invitee_email.lower(),
            status='pending'
        ).first()
        
        if existing_invite:
            return jsonify({'message': 'An invitation has already been sent to this email'}), 409
        
        # Check if there's already an active partnership with this email
        existing_user = User.query.filter_by(email=invitee_email.lower()).first()
        if existing_user:
            existing_partnership = Partnership.query.filter(
                ((Partnership.requester_id == current_user_id) & (Partnership.partner_id == existing_user.id)) |
                ((Partnership.requester_id == existing_user.id) & (Partnership.partner_id == current_user_id))
            ).first()
            
            if existing_partnership and existing_partnership.status == 'active':
                return jsonify({'message': 'Partnership already exists with this user'}), 409
        
        # Create invitation
        invite_token = generate_invite_token()
        expires_at = datetime.utcnow() + timedelta(days=7)  # 7 days expiry
        
        new_invite = PartnershipInvite(
            token=invite_token,
            inviter_id=current_user_id,
            invitee_email=invitee_email.lower(),
            invitee_role=invitee_role,
            message=message,
            expires_at=expires_at
        )
        
        db.session.add(new_invite)
        db.session.commit()
        
        # Send email invitation
        try:
            email_sent = email_sender.send_partnership_invite(
                from_user=user.to_dict(),
                to_email=invitee_email,
                invite_token=invite_token,
                message=message
            )
            if email_sent:
                print(f"✅ Invitation email sent to {invitee_email}")
            else:
                print(f"⚠️  Invitation email sending failed for {invitee_email}")
        except Exception as e:
            print(f"⚠️  Invitation email sending error: {str(e)}")
        
        return jsonify({
            'message': f'Partnership invitation sent to {invitee_email}',
            'invite': new_invite.to_dict(),
            'email_sent': True
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Failed to send partnership invitation', 'error': str(e)}), 500

@partnerships_bp.route('/invite/<token>/accept', methods=['POST'])
def accept_partnership_invite(token):
    """Accept a partnership invitation by token (no auth required)"""
    try:
        # Find the invitation
        invite = PartnershipInvite.query.filter_by(token=token, status='pending').first()
        if not invite:
            return jsonify({'message': 'Invalid or expired invitation'}), 404
        
        # Check if invitation has expired
        if invite.is_expired():
            invite.status = 'expired'
            db.session.commit()
            return jsonify({'message': 'Invitation has expired'}), 400
        
        # Get inviter details
        inviter = User.query.get(invite.inviter_id)
        if not inviter:
            return jsonify({'message': 'Inviter not found'}), 404
        
        # Check if invitee already exists
        invitee = User.query.filter_by(email=invite.invitee_email).first()
        
        if not invitee:
            # Create new user account for invitee
            data = request.get_json()
            if not data:
                return jsonify({'message': 'User registration data required'}), 400
            
            # Create new user
            invitee = User(
                email=invite.invitee_email,
                business_name=data.get('businessName', 'New Business'),
                role=invite.invitee_role,
                phone_number=data.get('phoneNumber'),
                is_verified=True  # Auto-verify since they came through invitation
            )
            invitee.set_password(data.get('password', 'temp123'))  # They can change this later
            
            db.session.add(invitee)
            db.session.flush()  # Get the ID
        
        # Create partnership
        new_partnership = Partnership(
            requester_id=invite.inviter_id,
            partner_id=invitee.id,
            partnership_type=invite.partnership_type,
            status='active',
            message=invite.message
        )
        
        # Update invitation status
        invite.status = 'accepted'
        invite.updated_at = datetime.utcnow()
        
        db.session.add(new_partnership)
        db.session.commit()
        
        # Send acceptance email to inviter
        try:
            email_sent = email_sender.send_partnership_accepted(
                to_user=inviter.to_dict(),
                from_user=invitee.to_dict()
            )
            if email_sent:
                print(f"✅ Acceptance email sent to {inviter.email}")
        except Exception as e:
            print(f"⚠️  Acceptance email sending error: {str(e)}")
        
        return jsonify({
            'message': 'Partnership invitation accepted successfully',
            'partnership': new_partnership.to_dict(),
            'user_created': invitee.id if not User.query.filter_by(email=invite.invitee_email).first() else False
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Failed to accept partnership invitation', 'error': str(e)}), 500

@partnerships_bp.route('/invite/<token>/decline', methods=['POST'])
def decline_partnership_invite(token):
    """Decline a partnership invitation by token (no auth required)"""
    try:
        # Find the invitation
        invite = PartnershipInvite.query.filter_by(token=token, status='pending').first()
        if not invite:
            return jsonify({'message': 'Invalid or expired invitation'}), 404
        
        # Check if invitation has expired
        if invite.is_expired():
            invite.status = 'expired'
            db.session.commit()
            return jsonify({'message': 'Invitation has expired'}), 400
        
        # Get inviter details
        inviter = User.query.get(invite.inviter_id)
        if not inviter:
            return jsonify({'message': 'Inviter not found'}), 404
        
        # Update invitation status
        invite.status = 'declined'
        invite.updated_at = datetime.utcnow()
        db.session.commit()
        
        # Send decline email to inviter
        try:
            decline_reason = request.get_json().get('reason', '') if request.get_json() else ''
            email_sent = email_sender.send_partnership_declined(
                to_user=inviter.to_dict(),
                from_user={'email': invite.invitee_email, 'businessName': 'Invited Partner'},
                reason=decline_reason
            )
            if email_sent:
                print(f"✅ Decline email sent to {inviter.email}")
        except Exception as e:
            print(f"⚠️  Decline email sending error: {str(e)}")
        
        return jsonify({
            'message': 'Partnership invitation declined successfully',
            'invite': invite.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Failed to decline partnership invitation', 'error': str(e)}), 500

@partnerships_bp.route('/invite/<token>', methods=['GET'])
def get_invite_details(token):
    """Get invitation details by token (no auth required)"""
    try:
        invite = PartnershipInvite.query.filter_by(token=token, status='pending').first()
        if not invite:
            return jsonify({'message': 'Invalid or expired invitation'}), 404
        
        # Check if invitation has expired
        if invite.is_expired():
            invite.status = 'expired'
            db.session.commit()
            return jsonify({'message': 'Invitation has expired'}), 400
        
        return jsonify(invite.to_dict()), 200
        
    except Exception as e:
        return jsonify({'message': 'Failed to get invitation details', 'error': str(e)}), 500

# Legacy endpoints for backward compatibility
@partnerships_bp.route('/send-request', methods=['POST'])
@jwt_required()
@role_required('manufacturer')
def send_partnership_request():
    """Legacy endpoint - redirects to new invite system"""
    return jsonify({'message': 'Please use /send-invite endpoint instead'}), 400

@partnerships_bp.route('/request-partnership', methods=['POST'])
@jwt_required()
@role_required('distributor')
def request_partnership():
    """Legacy endpoint - redirects to new invite system"""
    return jsonify({'message': 'Please use /send-invite endpoint instead'}), 400

@partnerships_bp.route('/<partnership_id>/accept', methods=['POST'])
@jwt_required()
def accept_partnership(partnership_id):
    """Accept a partnership request"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'message': 'User not found'}), 404
        
        partnership = Partnership.query.get(partnership_id)
        if not partnership:
            return jsonify({'message': 'Partnership request not found'}), 404
        
        # Check if user is the partner (receiving the request)
        if partnership.partner_id != current_user_id:
            return jsonify({'message': 'Access denied'}), 403
        
        if partnership.status != 'pending':
            return jsonify({'message': 'Partnership request is not pending'}), 400
        
        # Accept the partnership
        partnership.status = 'active'
        partnership.updated_at = datetime.utcnow()
        db.session.commit()
        
        # Send email notification to requester
        try:
            requester = User.query.get(partnership.requester_id)
            if requester:
                email_sent = email_sender.send_partnership_accepted(
                    to_user=requester.to_dict(),
                    from_user=user.to_dict()
                )
                if email_sent:
                    print(f"✅ Acceptance email sent to {requester.email}")
                else:
                    print(f"⚠️  Acceptance email sending failed for {requester.email}")
        except Exception as e:
            print(f"⚠️  Acceptance email sending error: {str(e)}")
        
        return jsonify({
            'message': 'Partnership accepted successfully',
            'partnership': partnership.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Failed to accept partnership', 'error': str(e)}), 500

@partnerships_bp.route('/<partnership_id>/decline', methods=['POST'])
@jwt_required()
def decline_partnership(partnership_id):
    """Decline a partnership request"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'message': 'User not found'}), 404
        
        partnership = Partnership.query.get(partnership_id)
        if not partnership:
            return jsonify({'message': 'Partnership request not found'}), 404
        
        # Check if user is the partner (receiving the request)
        if partnership.partner_id != current_user_id:
            return jsonify({'message': 'Access denied'}), 403
        
        if partnership.status != 'pending':
            return jsonify({'message': 'Partnership request is not pending'}), 400
        
        # Decline the partnership
        partnership.status = 'declined'
        partnership.updated_at = datetime.utcnow()
        db.session.commit()
        
        # Send email notification to requester
        try:
            requester = User.query.get(partnership.requester_id)
            if requester:
                email_sent = email_sender.send_partnership_declined(
                    to_user=requester.to_dict(),
                    from_user=user.to_dict(),
                    reason="Partnership request was declined"
                )
                if email_sent:
                    print(f"✅ Decline email sent to {requester.email}")
                else:
                    print(f"⚠️  Decline email sending failed for {requester.email}")
        except Exception as e:
            print(f"⚠️  Decline email sending error: {str(e)}")
        
        return jsonify({
            'message': 'Partnership declined successfully',
            'partnership': partnership.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Failed to decline partnership', 'error': str(e)}), 500

@partnerships_bp.route('/<partnership_id>', methods=['DELETE'])
@jwt_required()
def delete_partnership(partnership_id):
    """Delete/terminate a partnership"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'message': 'User not found'}), 404
        
        partnership = Partnership.query.get(partnership_id)
        if not partnership:
            return jsonify({'message': 'Partnership not found'}), 404
        
        # Check if user is part of this partnership
        if partnership.requester_id != current_user_id and partnership.partner_id != current_user_id:
            return jsonify({'message': 'Access denied'}), 403
        
        db.session.delete(partnership)
        db.session.commit()
        
        return jsonify({'message': 'Partnership terminated successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Failed to terminate partnership', 'error': str(e)}), 500

@partnerships_bp.route('/available', methods=['GET'])
@jwt_required()
def get_available_partners():
    """Get available partners for partnership requests"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'message': 'User not found'}), 404
        
        # Get all users except current user and those already partnered
        all_users = User.query.filter(User.id != current_user_id).all()
        
        # Get current user's partnerships (both as requester and partner)
        user_partnerships = Partnership.query.filter(
            ((Partnership.requester_id == current_user_id) | 
             (Partnership.partner_id == current_user_id))
        ).all()
        
        # Get IDs of users already partnered with current user
        partnered_user_ids = set()
        for partnership in user_partnerships:
            if partnership.requester_id == current_user_id:
                partnered_user_ids.add(partnership.partner_id)
            else:
                partnered_user_ids.add(partnership.requester_id)
        
        # Filter out already partnered users
        available_partners = []
        for potential_partner in all_users:
            if potential_partner.id not in partnered_user_ids:
                partner_data = potential_partner.to_public_dict()
                available_partners.append(partner_data)
        
        return jsonify(available_partners), 200
        
    except Exception as e:
        return jsonify({'message': 'Failed to fetch available partners', 'error': str(e)}), 500

@partnerships_bp.route('/connected-partners', methods=['GET'])
@jwt_required()
def get_connected_partners():
    """Get connected partners for current user"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
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
        return jsonify({'message': 'Failed to fetch connected partners', 'error': str(e)}), 500 