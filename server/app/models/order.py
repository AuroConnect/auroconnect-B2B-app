from app import db
from datetime import datetime
import uuid
from sqlalchemy.dialects.postgresql import UUID

class Order(db.Model):
    __tablename__ = 'orders'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    order_number = db.Column(db.String(255), unique=True, nullable=False)
    retailer_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'), nullable=False)
    distributor_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'), nullable=False)
    status = db.Column(db.String(50), default='pending')
    delivery_mode = db.Column(db.String(50), default='delivery')
    total_amount = db.Column(db.Numeric(10, 2), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    retailer = db.relationship('User', foreign_keys=[retailer_id], backref='retailer_orders')
    distributor = db.relationship('User', foreign_keys=[distributor_id], backref='distributor_orders')
    items = db.relationship('OrderItem', backref='order', lazy='dynamic', cascade='all, delete-orphan')
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': str(self.id),
            'orderNumber': self.order_number,
            'retailerId': str(self.retailer_id),
            'distributorId': str(self.distributor_id),
            'status': self.status,
            'deliveryMode': self.delivery_mode,
            'totalAmount': float(self.total_amount) if self.total_amount else None,
            'notes': self.notes,
            'createdAt': self.created_at.isoformat() if self.created_at else None,
            'updatedAt': self.updated_at.isoformat() if self.updated_at else None,
            'items': [item.to_dict() for item in self.items]
        }
    
    def __repr__(self):
        return f'<Order {self.order_number}>'

class OrderItem(db.Model):
    __tablename__ = 'order_items'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    order_id = db.Column(UUID(as_uuid=True), db.ForeignKey('orders.id'), nullable=False)
    product_id = db.Column(UUID(as_uuid=True), db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Numeric(10, 2), nullable=False)
    total_price = db.Column(db.Numeric(10, 2), nullable=False)
    
    # Relationships
    product = db.relationship('Product', backref='order_items')
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': str(self.id),
            'orderId': str(self.order_id),
            'productId': str(self.product_id),
            'quantity': self.quantity,
            'unitPrice': float(self.unit_price),
            'totalPrice': float(self.total_price),
            'product': self.product.to_dict() if self.product else None
        }
    
    def __repr__(self):
        return f'<OrderItem {self.product_id} - {self.quantity}>' 