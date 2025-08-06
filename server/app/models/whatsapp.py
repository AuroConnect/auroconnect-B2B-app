from app import db
from datetime import datetime
import uuid
from sqlalchemy.dialects.postgresql import UUID

class WhatsAppNotification(db.Model):
    __tablename__ = 'whatsapp_notifications'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'), nullable=False)
    message = db.Column(db.Text, nullable=False)
    type = db.Column(db.String(50), nullable=False)  # order_update, invoice_sent, etc.
    sent_at = db.Column(db.DateTime, nullable=True)
    is_delivered = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='whatsapp_notifications')
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': str(self.id),
            'userId': str(self.user_id),
            'message': self.message,
            'type': self.type,
            'sentAt': self.sent_at.isoformat() if self.sent_at else None,
            'isDelivered': self.is_delivered,
            'createdAt': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<WhatsAppNotification {self.type} to {self.user_id}>' 