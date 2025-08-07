from app import db
from datetime import datetime
import uuid

class Order(db.Model):
    __tablename__ = 'orders'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    buyer_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    seller_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    product_id = db.Column(db.String(36), db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(50), nullable=False, default='pending')  # pending, accepted, packed, shipped, delivered, rejected
    delivery_method = db.Column(db.String(50), nullable=True)  # delivery_to_address, self_pickup
    delivery_address = db.Column(db.Text, nullable=True)
    invoice_path = db.Column(db.String(500), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    buyer = db.relationship('User', foreign_keys=[buyer_id], backref='orders_as_buyer')
    seller = db.relationship('User', foreign_keys=[seller_id], backref='orders_as_seller')
    product = db.relationship('Product', backref='orders')
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'buyerId': self.buyer_id,
            'sellerId': self.seller_id,
            'productId': self.product_id,
            'quantity': self.quantity,
            'status': self.status,
            'deliveryMethod': self.delivery_method,
            'deliveryAddress': self.delivery_address,
            'invoicePath': self.invoice_path,
            'notes': self.notes,
            'createdAt': self.created_at.isoformat() if self.created_at else None,
            'updatedAt': self.updated_at.isoformat() if self.updated_at else None,
            'buyer': self.buyer.to_public_dict() if self.buyer else None,
            'seller': self.seller.to_public_dict() if self.seller else None,
            'product': self.product.to_dict() if self.product else None
        }
    
    def get_total_price(self):
        """Calculate total price"""
        if self.product and self.product.price:
            return float(self.product.price) * self.quantity
        return 0.0
    
    def can_update_status(self, new_status, user_id):
        """Check if user can update order status"""
        if new_status == 'accepted' and self.status == 'pending':
            return self.seller_id == user_id
        elif new_status in ['packed', 'shipped'] and self.status in ['accepted', 'packed']:
            return self.seller_id == user_id
        elif new_status == 'delivered' and self.status == 'shipped':
            return self.buyer_id == user_id
        return False
    
    def __repr__(self):
        return f'<Order {self.id} - {self.status}>'

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