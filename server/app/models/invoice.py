from app import db
from datetime import datetime
import uuid

class Invoice(db.Model):
    """Invoice model for manufacturer-distributor-retailer workflow"""
    __tablename__ = 'invoices'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Invoice type: 'manufacturer_distributor' or 'distributor_retailer'
    invoice_type = db.Column(db.String(50), nullable=False)
    
    # For manufacturer-distributor invoices
    manufacturer_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=True)
    distributor_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=True)
    
    # For distributor-retailer invoices
    retailer_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=True)
    
    # Invoice details
    invoice_number = db.Column(db.String(50), unique=True, nullable=False)
    order_id = db.Column(db.String(36), db.ForeignKey('orders.id'), nullable=False)
    
    # Amount details
    subtotal = db.Column(db.Numeric(10, 2), nullable=False)
    tax_amount = db.Column(db.Numeric(10, 2), default=0)
    shipping_amount = db.Column(db.Numeric(10, 2), default=0)
    total_amount = db.Column(db.Numeric(10, 2), nullable=False)
    
    # Invoice status
    status = db.Column(db.String(20), default='pending')  # pending, paid, overdue, cancelled
    
    # Payment details
    payment_method = db.Column(db.String(50), nullable=True)
    payment_date = db.Column(db.DateTime, nullable=True)
    due_date = db.Column(db.DateTime, nullable=True)
    
    # Invoice details
    notes = db.Column(db.Text, nullable=True)
    terms_conditions = db.Column(db.Text, nullable=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    manufacturer = db.relationship('User', foreign_keys=[manufacturer_id], backref='manufacturer_invoices')
    distributor = db.relationship('User', foreign_keys=[distributor_id], backref='distributor_invoices')
    retailer = db.relationship('User', foreign_keys=[retailer_id], backref='retailer_invoices')
    order = db.relationship('Order', backref='invoices')
    items = db.relationship('InvoiceItem', backref='invoice', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'invoice_type': self.invoice_type,
            'manufacturer_id': self.manufacturer_id,
            'distributor_id': self.distributor_id,
            'retailer_id': self.retailer_id,
            'invoice_number': self.invoice_number,
            'order_id': self.order_id,
            'subtotal': float(self.subtotal) if self.subtotal else 0,
            'tax_amount': float(self.tax_amount) if self.tax_amount else 0,
            'shipping_amount': float(self.shipping_amount) if self.shipping_amount else 0,
            'total_amount': float(self.total_amount) if self.total_amount else 0,
            'status': self.status,
            'payment_method': self.payment_method,
            'payment_date': self.payment_date.isoformat() if self.payment_date else None,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'notes': self.notes,
            'terms_conditions': self.terms_conditions,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'items': [item.to_dict() for item in self.items],
            'manufacturer': self.manufacturer.to_dict() if self.manufacturer else None,
            'distributor': self.distributor.to_dict() if self.distributor else None,
            'retailer': self.retailer.to_dict() if self.retailer else None,
            'order': self.order.to_dict() if self.order else None,
        }
    
    @staticmethod
    def generate_invoice_number():
        """Generate unique invoice number"""
        import random
        import string
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        random_chars = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
        return f"INV-{timestamp}-{random_chars}"
    
    @staticmethod
    def get_manufacturer_invoices(manufacturer_id):
        """Get all invoices for a manufacturer"""
        return Invoice.query.filter_by(
            manufacturer_id=manufacturer_id,
            invoice_type='manufacturer_distributor'
        ).order_by(Invoice.created_at.desc()).all()
    
    @staticmethod
    def get_distributor_invoices(distributor_id):
        """Get all invoices for a distributor (both from manufacturer and to retailers)"""
        return Invoice.query.filter(
            db.or_(
                db.and_(Invoice.distributor_id == distributor_id, Invoice.invoice_type == 'manufacturer_distributor'),
                db.and_(Invoice.distributor_id == distributor_id, Invoice.invoice_type == 'distributor_retailer')
            )
        ).order_by(Invoice.created_at.desc()).all()
    
    @staticmethod
    def get_retailer_invoices(retailer_id):
        """Get all invoices for a retailer"""
        return Invoice.query.filter_by(
            retailer_id=retailer_id,
            invoice_type='distributor_retailer'
        ).order_by(Invoice.created_at.desc()).all()

class InvoiceItem(db.Model):
    """Invoice item model"""
    __tablename__ = 'invoice_items'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    invoice_id = db.Column(db.String(36), db.ForeignKey('invoices.id'), nullable=False)
    product_id = db.Column(db.String(36), db.ForeignKey('products.id'), nullable=False)
    
    # Item details
    quantity = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Numeric(10, 2), nullable=False)
    total_price = db.Column(db.Numeric(10, 2), nullable=False)
    
    # Product snapshot (in case product is deleted)
    product_name = db.Column(db.String(200), nullable=False)
    product_sku = db.Column(db.String(100), nullable=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    product = db.relationship('Product', backref='invoice_items')
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'invoice_id': self.invoice_id,
            'product_id': self.product_id,
            'quantity': self.quantity,
            'unit_price': float(self.unit_price) if self.unit_price else 0,
            'total_price': float(self.total_price) if self.total_price else 0,
            'product_name': self.product_name,
            'product_sku': self.product_sku,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'product': self.product.to_dict() if self.product else None,
        } 