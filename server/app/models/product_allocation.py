from app import db
from datetime import datetime
import uuid

class ProductAllocation(db.Model):
    __tablename__ = 'product_allocations'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Allocation details
    manufacturer_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    distributor_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    product_id = db.Column(db.String(36), db.ForeignKey('products.id'), nullable=False)
    
    # Allocation settings
    allocated_quantity = db.Column(db.Integer, nullable=False, default=0)
    selling_price = db.Column(db.Numeric(10, 2), nullable=False)  # Price distributor can sell at
    is_active = db.Column(db.Boolean, default=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    manufacturer = db.relationship('User', foreign_keys=[manufacturer_id], backref='manufacturer_allocations')
    distributor = db.relationship('User', foreign_keys=[distributor_id], backref='distributor_allocations')
    product = db.relationship('Product', backref='allocations')
    
    def to_dict(self):
        return {
            'id': self.id,
            'manufacturer_id': self.manufacturer_id,
            'distributor_id': self.distributor_id,
            'product_id': self.product_id,
            'allocated_quantity': self.allocated_quantity,
            'selling_price': float(self.selling_price) if self.selling_price else 0.0,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'manufacturer': self.manufacturer.to_dict() if self.manufacturer else None,
            'distributor': self.distributor.to_dict() if self.distributor else None,
            'product': self.product.to_dict() if self.product else None
        }
    
    def __repr__(self):
        return f'<ProductAllocation {self.manufacturer_id} -> {self.distributor_id}: {self.product_id}>'
