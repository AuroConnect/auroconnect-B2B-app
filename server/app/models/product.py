from app import db
from datetime import datetime
import uuid
from sqlalchemy.dialects.postgresql import UUID

class Product(db.Model):
    __tablename__ = 'products'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    sku = db.Column(db.String(255), unique=True, nullable=False)
    category_id = db.Column(UUID(as_uuid=True), db.ForeignKey('categories.id'), nullable=True)
    manufacturer_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'), nullable=True)
    image_url = db.Column(db.Text, nullable=True)
    base_price = db.Column(db.Numeric(10, 2), nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    category = db.relationship('Category', backref='products')
    manufacturer = db.relationship('User', backref='manufactured_products')
    inventory_items = db.relationship('Inventory', backref='product', lazy='dynamic')
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': str(self.id),
            'name': self.name,
            'description': self.description,
            'sku': self.sku,
            'categoryId': str(self.category_id) if self.category_id else None,
            'manufacturerId': str(self.manufacturer_id) if self.manufacturer_id else None,
            'imageUrl': self.image_url,
            'basePrice': float(self.base_price) if self.base_price else None,
            'isActive': self.is_active,
            'createdAt': self.created_at.isoformat() if self.created_at else None,
            'updatedAt': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<Product {self.name}>' 