from app import db
from datetime import datetime
import uuid

class Inventory(db.Model):
    __tablename__ = 'inventory'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    distributor_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    product_id = db.Column(db.String(36), db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=0)
    selling_price = db.Column(db.Numeric(10, 2), nullable=True)
    is_available = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    distributor = db.relationship('User', backref='inventory_items')
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': str(self.id),
            'distributorId': str(self.distributor_id),
            'productId': str(self.product_id),
            'quantity': self.quantity,
            'sellingPrice': float(self.selling_price) if self.selling_price else None,
            'isAvailable': self.is_available,
            'createdAt': self.created_at.isoformat() if self.created_at else None,
            'updatedAt': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<Inventory {self.product_id} - {self.quantity}>' 