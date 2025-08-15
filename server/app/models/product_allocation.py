from app import db
from datetime import datetime
import uuid

class ProductAllocation(db.Model):
    __tablename__ = 'product_allocations'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    manufacturer_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    distributor_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    product_id = db.Column(db.String(36), db.ForeignKey('products.id'), nullable=False)
    selling_price = db.Column(db.Numeric(10, 2), nullable=True)
    allocated_quantity = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    manufacturer = db.relationship('User', foreign_keys=[manufacturer_id], backref='product_allocations')
    distributor = db.relationship('User', foreign_keys=[distributor_id], backref='allocated_products')
    product = db.relationship('Product', backref='allocations')
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': str(self.id),
            'manufacturerId': str(self.manufacturer_id),
            'distributorId': str(self.distributor_id),
            'productId': str(self.product_id),
            'sellingPrice': float(self.selling_price) if self.selling_price else None,
            'allocatedQuantity': self.allocated_quantity,
            'isActive': self.is_active,
            'createdAt': self.created_at.isoformat() if self.created_at else None,
            'updatedAt': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<ProductAllocation {self.manufacturer_id} -> {self.distributor_id} for {self.product_id}>'
