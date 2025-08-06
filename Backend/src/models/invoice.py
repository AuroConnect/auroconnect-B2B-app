from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Invoice(db.Model):
    __tablename__ = 'invoices'
    
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), unique=True, nullable=False, index=True)
    invoice_number = db.Column(db.String(50), unique=True, nullable=False, index=True)
    subtotal = db.Column(db.Numeric(10, 2), nullable=False)
    tax_rate = db.Column(db.Numeric(5, 2), nullable=False, default=0.00)
    tax_amount = db.Column(db.Numeric(10, 2), nullable=False, default=0.00)
    total = db.Column(db.Numeric(10, 2), nullable=False)
    issued_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    due_date = db.Column(db.DateTime, nullable=False)
    
    # Relationships
    # order relationship is defined in order.py
    
    def generate_invoice_number(self):
        """Generate a unique invoice number"""
        if not self.id:
            # This is a new invoice, we'll generate the number after it's saved
            return None
        # Format: INV-YYYY-MM-DD-XXXX (where XXXX is the invoice ID)
        return f"INV-{self.issued_at.strftime('%Y%m%d')}-{self.id:04d}"
    
    def calculate_tax(self):
        """Calculate tax amount based on subtotal and tax rate"""
        self.tax_amount = self.subtotal * (self.tax_rate / 100)
        self.total = self.subtotal + self.tax_amount
    
    def to_dict(self):
        """Convert the invoice object to a dictionary"""
        return {
            'id': self.id,
            'order_id': self.order_id,
            'invoice_number': self.invoice_number,
            'subtotal': float(self.subtotal),
            'tax_rate': float(self.tax_rate),
            'tax_amount': float(self.tax_amount),
            'total': float(self.total),
            'issued_at': self.issued_at.isoformat() if self.issued_at else None,
            'due_date': self.due_date.isoformat() if self.due_date else None
        }
    
    def __repr__(self):
        return f'<Invoice {self.invoice_number} Total:{self.total}>'