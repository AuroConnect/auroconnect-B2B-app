from app import db
from datetime import datetime
import uuid

class Partnership(db.Model):
    __tablename__ = 'partnerships'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Partnership details
    requester_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    partner_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    
    # Partnership type
    partnership_type = db.Column(db.String(20), nullable=False)  # 'MANUFACTURER_DISTRIBUTOR' or 'DISTRIBUTOR_RETAILER'
    
    # Status
    status = db.Column(db.String(20), default='pending')  # 'pending', 'active', 'inactive'
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    requester = db.relationship('User', foreign_keys=[requester_id], backref='requested_partnerships')
    partner = db.relationship('User', foreign_keys=[partner_id], backref='received_partnerships')
    
    def to_dict(self):
        return {
            'id': self.id,
            'requester_id': self.requester_id,
            'partner_id': self.partner_id,
            'partnership_type': self.partnership_type,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'requester': self.requester.to_dict() if self.requester else None,
            'partner': self.partner.to_dict() if self.partner else None
        }
    
    def __repr__(self):
        return f'<Partnership {self.partnership_type}: {self.manufacturer_id}-{self.distributor_id}-{self.retailer_id}>' 