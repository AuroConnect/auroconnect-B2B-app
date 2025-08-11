from app import db
from datetime import datetime
import uuid

class Partnership(db.Model):
    __tablename__ = 'partnerships'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    requester_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    partner_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    status = db.Column(db.String(50), default='pending')
    partnership_type = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    requester = db.relationship('User', foreign_keys=[requester_id], backref='sent_partnerships')
    partner = db.relationship('User', foreign_keys=[partner_id], backref='received_partnerships')
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': str(self.id),
            'requesterId': str(self.requester_id),
            'partnerId': str(self.partner_id),
            'status': self.status,
            'partnershipType': self.partnership_type,
            'createdAt': self.created_at.isoformat() if self.created_at else None,
            'updatedAt': self.updated_at.isoformat() if self.updated_at else None,
            'partner': self.partner.to_public_dict() if self.partner else None
        }
    
    def __repr__(self):
        return f'<Partnership {self.requester_id} -> {self.partner_id}>' 