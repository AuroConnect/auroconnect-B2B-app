from app import db
from datetime import datetime
import uuid

class Cart(db.Model):
    """Cart model for B2B platform"""
    __tablename__ = 'carts'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='cart')
    items = db.relationship('CartItem', backref='cart', cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'userId': self.user_id,
            'createdAt': self.created_at.isoformat(),
            'updatedAt': self.updated_at.isoformat()
        }

class CartItem(db.Model):
    """Cart item model for B2B platform"""
    __tablename__ = 'cart_items'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    cart_id = db.Column(db.String(36), db.ForeignKey('carts.id'), nullable=False)
    product_id = db.Column(db.String(36), db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    product = db.relationship('Product', backref='cart_items')
    
    def to_dict(self):
        return {
            'id': self.id,
            'cartId': self.cart_id,
            'productId': self.product_id,
            'quantity': self.quantity,
            'createdAt': self.created_at.isoformat(),
            'updatedAt': self.updated_at.isoformat()
        }
