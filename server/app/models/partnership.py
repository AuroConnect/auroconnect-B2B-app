from app import db
from datetime import datetime
import uuid

class Partnership(db.Model):
    """Partnership model for managing business relationships"""
    __tablename__ = 'partnerships'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    requester_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    partner_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    partnership_type = db.Column(db.String(50), nullable=False, default='MANUFACTURER_DISTRIBUTOR')
    status = db.Column(db.String(20), nullable=False, default='pending')  # pending, active, declined
    message = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    requester = db.relationship('User', foreign_keys=[requester_id], backref='sent_partnerships')
    partner = db.relationship('User', foreign_keys=[partner_id], backref='received_partnerships')
    
    def to_dict(self):
        return {
            'id': self.id,
            'requester_id': self.requester_id,
            'partner_id': self.partner_id,
            'partnership_type': self.partnership_type,
            'status': self.status,
            'message': self.message,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'requester': self.requester.to_public_dict() if self.requester else None,
            'partner': self.partner.to_public_dict() if self.partner else None
        }

class PartnershipInvite(db.Model):
    """Partnership invitation model for email-based invitations"""
    __tablename__ = 'partnership_invites'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    token = db.Column(db.String(64), unique=True, nullable=False, index=True)
    inviter_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    invitee_email = db.Column(db.String(255), nullable=False)
    invitee_role = db.Column(db.String(20), nullable=False)  # manufacturer, distributor
    partnership_type = db.Column(db.String(50), nullable=False, default='MANUFACTURER_DISTRIBUTOR')
    message = db.Column(db.Text)
    status = db.Column(db.String(20), nullable=False, default='pending')  # pending, accepted, declined, expired
    expires_at = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    inviter = db.relationship('User', foreign_keys=[inviter_id], backref='sent_invites')
    
    def to_dict(self):
        return {
            'id': self.id,
            'token': self.token,
            'inviter_id': self.inviter_id,
            'invitee_email': self.invitee_email,
            'invitee_role': self.invitee_role,
            'partnership_type': self.partnership_type,
            'message': self.message,
            'status': self.status,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'inviter': self.inviter.to_public_dict() if self.inviter else None,
            'is_expired': self.is_expired()
        }
    
    def is_expired(self):
        """Check if the invitation has expired"""
        return datetime.utcnow() > self.expires_at if self.expires_at else True 