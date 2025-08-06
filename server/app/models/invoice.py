from app import db
from datetime import datetime
import uuid
from sqlalchemy.dialects.postgresql import UUID

class Invoice(db.Model):
    __tablename__ = 'invoices'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    invoice_number = db.Column(db.String(255), unique=True, nullable=False)
    order_id = db.Column(UUID(as_uuid=True), db.ForeignKey('orders.id'), nullable=False)
    pdf_url = db.Column(db.Text, nullable=True)
    sent_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    order = db.relationship('Order', backref='invoices')
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': str(self.id),
            'invoiceNumber': self.invoice_number,
            'orderId': str(self.order_id),
            'pdfUrl': self.pdf_url,
            'sentAt': self.sent_at.isoformat() if self.sent_at else None,
            'createdAt': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<Invoice {self.invoice_number}>' 