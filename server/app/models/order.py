from app import db
from datetime import datetime
import uuid

class Order(db.Model):
    """Order model for manufacturer-distributor-retailer workflow"""
    __tablename__ = 'orders'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Order type: 'manufacturer_distributor' or 'distributor_retailer'
    order_type = db.Column(db.String(50), nullable=False)
    
    # For manufacturer-distributor orders
    manufacturer_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=True)
    distributor_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=True)
    
    # For distributor-retailer orders
    retailer_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=True)
    
    # Order details
    order_number = db.Column(db.String(50), unique=True, nullable=False)
    total_amount = db.Column(db.Numeric(10, 2), nullable=False)
    tax_amount = db.Column(db.Numeric(10, 2), default=0)
    shipping_amount = db.Column(db.Numeric(10, 2), default=0)
    
    # Order status tracking
    status = db.Column(db.String(20), default='pending')  # pending, accepted, processing, shipped, delivered, cancelled
    
    # Delivery details
    delivery_address = db.Column(db.Text, nullable=True)
    delivery_method = db.Column(db.String(50), nullable=True)  # 'delivery', 'pickup'
    expected_delivery_date = db.Column(db.DateTime, nullable=True)
    actual_delivery_date = db.Column(db.DateTime, nullable=True)
    
    # Notes and tracking
    notes = db.Column(db.Text, nullable=True)
    tracking_number = db.Column(db.String(100), nullable=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    manufacturer = db.relationship('User', foreign_keys=[manufacturer_id], backref='manufacturer_orders')
    distributor = db.relationship('User', foreign_keys=[distributor_id], backref='distributor_orders')
    retailer = db.relationship('User', foreign_keys=[retailer_id], backref='retailer_orders')
    items = db.relationship('OrderItem', backref='order', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'order_type': self.order_type,
            'manufacturer_id': self.manufacturer_id,
            'distributor_id': self.distributor_id,
            'retailer_id': self.retailer_id,
            'order_number': self.order_number,
            'total_amount': float(self.total_amount) if self.total_amount else 0,
            'tax_amount': float(self.tax_amount) if self.tax_amount else 0,
            'shipping_amount': float(self.shipping_amount) if self.shipping_amount else 0,
            'status': self.status,
            'delivery_address': self.delivery_address,
            'delivery_method': self.delivery_method,
            'expected_delivery_date': self.expected_delivery_date.isoformat() if self.expected_delivery_date else None,
            'actual_delivery_date': self.actual_delivery_date.isoformat() if self.actual_delivery_date else None,
            'notes': self.notes,
            'tracking_number': self.tracking_number,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'items': [item.to_dict() for item in self.items],
            'manufacturer': self.manufacturer.to_dict() if self.manufacturer else None,
            'distributor': self.distributor.to_dict() if self.distributor else None,
            'retailer': self.retailer.to_dict() if self.retailer else None,
        }
    
    @staticmethod
    def generate_order_number():
        """Generate unique order number"""
        import random
        import string
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        random_chars = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
        return f"ORD-{timestamp}-{random_chars}"
    
    @staticmethod
    def get_manufacturer_orders(manufacturer_id):
        """Get all orders for a manufacturer"""
        return Order.query.filter_by(
            manufacturer_id=manufacturer_id,
            order_type='manufacturer_distributor'
        ).order_by(Order.created_at.desc()).all()
    
    @staticmethod
    def get_distributor_orders(distributor_id):
        """Get all orders for a distributor (both from manufacturer and to retailers)"""
        return Order.query.filter(
            db.or_(
                db.and_(Order.distributor_id == distributor_id, Order.order_type == 'manufacturer_distributor'),
                db.and_(Order.distributor_id == distributor_id, Order.order_type == 'distributor_retailer')
            )
        ).order_by(Order.created_at.desc()).all()
    
    @staticmethod
    def get_retailer_orders(retailer_id):
        """Get all orders for a retailer"""
        return Order.query.filter_by(
            retailer_id=retailer_id,
            order_type='distributor_retailer'
        ).order_by(Order.created_at.desc()).all()

class OrderItem(db.Model):
    """Order item model"""
    __tablename__ = 'order_items'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    order_id = db.Column(db.String(36), db.ForeignKey('orders.id'), nullable=False)
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
    product = db.relationship('Product', backref='order_items')
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'order_id': self.order_id,
            'product_id': self.product_id,
            'quantity': self.quantity,
            'unit_price': float(self.unit_price) if self.unit_price else 0,
            'total_price': float(self.total_price) if self.total_price else 0,
            'product_name': self.product_name,
            'product_sku': self.product_sku,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'product': self.product.to_dict() if self.product else None,
        } 