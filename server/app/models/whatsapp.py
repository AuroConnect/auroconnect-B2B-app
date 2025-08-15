from app import db
from datetime import datetime
import uuid

class WhatsAppNotification(db.Model):
    __tablename__ = 'whatsapp_notifications'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    message = db.Column(db.Text, nullable=False)
    type = db.Column(db.String(50), nullable=False)  # 'order_status', 'new_order', 'system'
    is_read = db.Column(db.Boolean, default=False)
    sent_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref='whatsapp_notifications')

    def to_dict(self):
        return {
            'id': str(self.id),
            'userId': str(self.user_id),
            'message': self.message,
            'type': self.type,
            'isRead': self.is_read,
            'sentAt': self.sent_at.isoformat() if self.sent_at else None
        }

    def mark_as_read(self):
        self.is_read = True
        db.session.commit()

    def __repr__(self):
        return f'<WhatsAppNotification {self.id} for {self.user_id}>' 