from app import db
from datetime import datetime
import uuid

class Invoice(db.Model):
    __tablename__ = 'invoices'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    invoice_number = db.Column(db.String(255), unique=True, nullable=False)
    order_id = db.Column(db.String(36), db.ForeignKey('orders.id'), nullable=False)
    seller_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    buyer_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    total_amount = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    tax_amount = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    shipping_amount = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    grand_total = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    order = db.relationship('Order', backref='invoices')
    seller = db.relationship('User', foreign_keys=[seller_id], backref='seller_invoices')
    buyer = db.relationship('User', foreign_keys=[buyer_id], backref='buyer_invoices')
    
    def to_dict(self):
        return {
            'id': self.id,
            'invoice_number': self.invoice_number,
            'order_id': self.order_id,
            'seller_id': self.seller_id,
            'buyer_id': self.buyer_id,
            'total_amount': float(self.total_amount) if self.total_amount else 0,
            'tax_amount': float(self.tax_amount) if self.tax_amount else 0,
            'shipping_amount': float(self.shipping_amount) if self.shipping_amount else 0,
            'grand_total': float(self.grand_total) if self.grand_total else 0,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'order': {
                'id': self.order.id,
                'status': self.order.status,
                'delivery_option': self.order.delivery_option
            } if self.order else None,
            'seller': {
                'id': self.seller.id,
                'business_name': self.seller.business_name,
                'email': self.seller.email
            } if self.seller else None,
            'buyer': {
                'id': self.buyer.id,
                'business_name': self.buyer.business_name,
                'email': self.buyer.email
            } if self.buyer else None
        }
    
    def __repr__(self):
        return f'<Invoice {self.invoice_number}>' 