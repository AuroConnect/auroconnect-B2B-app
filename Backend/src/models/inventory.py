from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Inventory(db.Model):
    __tablename__ = 'inventories'
    
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False, index=True)
    distributor_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    quantity = db.Column(db.Integer, nullable=False, default=0)
    reserved_quantity = db.Column(db.Integer, nullable=False, default=0)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    # product relationship is defined in product.py
    # distributor relationship is defined in user.py
    
    # Ensure unique constraint for product-distributor combination
    __table_args__ = (db.UniqueConstraint('product_id', 'distributor_id', name='uq_product_distributor'),)
    
    @property
    def available_quantity(self):
        """Calculate available quantity (total - reserved)"""
        return max(0, self.quantity - self.reserved_quantity)
    
    def reserve_quantity(self, qty):
        """Reserve quantity for an order"""
        if qty <= self.available_quantity:
            self.reserved_quantity += qty
            return True
        return False
    
    def release_reserved_quantity(self, qty):
        """Release reserved quantity"""
        self.reserved_quantity = max(0, self.reserved_quantity - qty)
    
    def deduct_reserved_quantity(self, qty):
        """Deduct reserved quantity when order is fulfilled"""
        if qty <= self.reserved_quantity:
            self.reserved_quantity -= qty
            self.quantity -= qty
            return True
        return False
    
    def add_stock(self, qty):
        """Add stock to inventory"""
        self.quantity += qty
        return True
    
    def to_dict(self):
        """Convert the inventory object to a dictionary"""
        return {
            'id': self.id,
            'product_id': self.product_id,
            'product_name': self.product.name if self.product else None,
            'distributor_id': self.distributor_id,
            'distributor_name': self.distributor.company_name if self.distributor else None,
            'quantity': self.quantity,
            'reserved_quantity': self.reserved_quantity,
            'available_quantity': self.available_quantity,
            'last_updated': self.last_updated.isoformat() if self.last_updated else None
        }
    
    def __repr__(self):
        return f'<Inventory Product:{self.product_id} Distributor:{self.distributor_id} Qty:{self.quantity}>'