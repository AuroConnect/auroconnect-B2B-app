from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import enum

db = SQLAlchemy()

class ProductCategoryEnum(enum.Enum):
    MATTRESS = "mattress"
    CLOTHING = "clothing"
    LAPTOP = "laptop"
    ELECTRONICS = "electronics"
    GENERAL = "general"

class Product(db.Model):
    __tablename__ = 'products'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.Enum(ProductCategoryEnum), nullable=False, index=True)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    manufacturer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    sku = db.Column(db.String(100), unique=True, index=True)
    image_url = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    manufacturer = db.relationship('User', foreign_keys=[manufacturer_id], backref='products')
    inventories = db.relationship('Inventory', backref='product', lazy=True, cascade='all, delete-orphan')
    order_items = db.relationship('OrderItem', backref='product', lazy=True, cascade='all, delete-orphan')
    
    def get_category_display(self):
        """Get the display name for the product category"""
        category_names = {
            ProductCategoryEnum.MATTRESS: "Mattress",
            ProductCategoryEnum.CLOTHING: "Clothing",
            ProductCategoryEnum.LAPTOP: "Laptop",
            ProductCategoryEnum.ELECTRONICS: "Electronics",
            ProductCategoryEnum.GENERAL: "General"
        }
        return category_names.get(self.category, "Unknown")
    
    def to_dict(self):
        """Convert the product object to a dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'category': self.category.value,
            'category_display': self.get_category_display(),
            'price': float(self.price),
            'manufacturer_id': self.manufacturer_id,
            'manufacturer_name': self.manufacturer.company_name if self.manufacturer else None,
            'sku': self.sku,
            'image_url': self.image_url,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<Product {self.name} ({self.sku})>'