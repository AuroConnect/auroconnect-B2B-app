from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import enum

db = SQLAlchemy()

class NotificationTypeEnum(enum.Enum):
    ORDER = "order"
    INVOICE = "invoice"
    ALERT = "alert"
    INFO = "info"

class NotificationStatusEnum(enum.Enum):
    UNREAD = "unread"
    READ = "read"
    ARCHIVED = "archived"

class Notification(db.Model):
    __tablename__ = 'notifications'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), index=True)
    message = db.Column(db.Text, nullable=False)
    type = db.Column(db.Enum(NotificationTypeEnum), nullable=False, default=NotificationTypeEnum.INFO, index=True)
    status = db.Column(db.Enum(NotificationStatusEnum), nullable=False, default=NotificationStatusEnum.UNREAD, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    read_at = db.Column(db.DateTime, index=True)
    
    # Relationships
    # user relationship is defined in user.py
    # order relationship is defined in order.py
    
    def mark_as_read(self):
        """Mark notification as read"""
        self.status = NotificationStatusEnum.READ
        self.read_at = datetime.utcnow()
    
    def mark_as_unread(self):
        """Mark notification as unread"""
        self.status = NotificationStatusEnum.UNREAD
        self.read_at = None
    
    def archive(self):
        """Archive the notification"""
        self.status = NotificationStatusEnum.ARCHIVED
    
    def get_type_display(self):
        """Get the display name for the notification type"""
        type_names = {
            NotificationTypeEnum.ORDER: "Order",
            NotificationTypeEnum.INVOICE: "Invoice",
            NotificationTypeEnum.ALERT: "Alert",
            NotificationTypeEnum.INFO: "Info"
        }
        return type_names.get(self.type, "Unknown")
    
    def get_status_display(self):
        """Get the display name for the notification status"""
        status_names = {
            NotificationStatusEnum.UNREAD: "Unread",
            NotificationStatusEnum.READ: "Read",
            NotificationStatusEnum.ARCHIVED: "Archived"
        }
        return status_names.get(self.status, "Unknown")
    
    def to_dict(self):
        """Convert the notification object to a dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'order_id': self.order_id,
            'message': self.message,
            'type': self.type.value,
            'type_display': self.get_type_display(),
            'status': self.status.value,
            'status_display': self.get_status_display(),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'read_at': self.read_at.isoformat() if self.read_at else None
        }
    
    def __repr__(self):
        return f'<Notification {self.id} Type:{self.type.value} Status:{self.status.value}>'