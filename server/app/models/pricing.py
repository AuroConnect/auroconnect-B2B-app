from app import db
from datetime import datetime, date
import uuid

class PricingRule(db.Model):
    __tablename__ = 'pricing_rules'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(100), nullable=False)
    rule_type = db.Column(db.String(50), nullable=False)  # VOLUME, SEASONAL, PARTNER, CATEGORY
    discount_type = db.Column(db.String(20), nullable=False)  # PERCENTAGE, FIXED_AMOUNT
    discount_value = db.Column(db.Numeric(10, 2), nullable=False)
    
    # Applicability
    manufacturer_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=True)
    distributor_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=True)
    category_id = db.Column(db.String(36), db.ForeignKey('categories.id'), nullable=True)
    product_id = db.Column(db.String(36), db.ForeignKey('products.id'), nullable=True)
    
    # Volume tier settings
    min_quantity = db.Column(db.Integer, nullable=True)
    max_quantity = db.Column(db.Integer, nullable=True)
    
    # Seasonal settings
    start_date = db.Column(db.Date, nullable=True)
    end_date = db.Column(db.Date, nullable=True)
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    priority = db.Column(db.Integer, default=1)  # Higher number = higher priority
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    manufacturer = db.relationship('User', foreign_keys=[manufacturer_id])
    distributor = db.relationship('User', foreign_keys=[distributor_id])
    
    def is_applicable(self, product_id=None, category_id=None, quantity=1, buyer_id=None, seller_id=None):
        """Check if pricing rule is applicable"""
        if not self.is_active:
            return False
        
        # Check date range for seasonal rules
        if self.rule_type == 'SEASONAL' and (self.start_date or self.end_date):
            today = date.today()
            if self.start_date and today < self.start_date:
                return False
            if self.end_date and today > self.end_date:
                return False
        
        # Check volume tier
        if self.rule_type == 'VOLUME':
            if self.min_quantity and quantity < self.min_quantity:
                return False
            if self.max_quantity and quantity > self.max_quantity:
                return False
        
        # Check product/category applicability
        if self.product_id and product_id != self.product_id:
            return False
        if self.category_id and category_id != self.category_id:
            return False
        
        # Check partner applicability
        if self.manufacturer_id and seller_id != self.manufacturer_id:
            return False
        if self.distributor_id and buyer_id != self.distributor_id:
            return False
        
        return True
    
    def calculate_discount(self, base_price, quantity=1):
        """Calculate discount amount"""
        if self.discount_type == 'PERCENTAGE':
            return (base_price * self.discount_value / 100) * quantity
        elif self.discount_type == 'FIXED_AMOUNT':
            return self.discount_value * quantity
        return 0
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'rule_type': self.rule_type,
            'discount_type': self.discount_type,
            'discount_value': float(self.discount_value) if self.discount_value else 0,
            'manufacturer_id': self.manufacturer_id,
            'distributor_id': self.distributor_id,
            'category_id': self.category_id,
            'product_id': self.product_id,
            'min_quantity': self.min_quantity,
            'max_quantity': self.max_quantity,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'is_active': self.is_active,
            'priority': self.priority,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class PromoCode(db.Model):
    __tablename__ = 'promo_codes'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    code = db.Column(db.String(50), nullable=False, unique=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    
    # Discount settings
    discount_type = db.Column(db.String(20), nullable=False)  # PERCENTAGE, FIXED_AMOUNT
    discount_value = db.Column(db.Numeric(10, 2), nullable=False)
    min_order_amount = db.Column(db.Numeric(10, 2), nullable=True)
    max_discount_amount = db.Column(db.Numeric(10, 2), nullable=True)
    
    # Usage limits
    max_uses = db.Column(db.Integer, nullable=True)
    current_uses = db.Column(db.Integer, default=0)
    max_uses_per_user = db.Column(db.Integer, default=1)
    
    # Validity
    start_date = db.Column(db.Date, nullable=True)
    end_date = db.Column(db.Date, nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    
    # Applicability
    applicable_roles = db.Column(db.String(100))  # Comma-separated: manufacturer,distributor,retailer
    applicable_categories = db.Column(db.String(500))  # Comma-separated category IDs
    applicable_products = db.Column(db.String(500))  # Comma-separated product IDs
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    @property
    def is_expired(self):
        """Check if promo code is expired"""
        if not self.is_active:
            return True
        
        today = date.today()
        if self.start_date and today < self.start_date:
            return True
        if self.end_date and today > self.end_date:
            return True
        
        if self.max_uses and self.current_uses >= self.max_uses:
            return True
        
        return False
    
    @property
    def applicable_roles_list(self):
        """Get applicable roles as list"""
        return [role.strip() for role in self.applicable_roles.split(',')] if self.applicable_roles else []
    
    @property
    def applicable_categories_list(self):
        """Get applicable categories as list"""
        return [cat.strip() for cat in self.applicable_categories.split(',')] if self.applicable_categories else []
    
    @property
    def applicable_products_list(self):
        """Get applicable products as list"""
        return [prod.strip() for prod in self.applicable_products.split(',')] if self.applicable_products else []
    
    def is_applicable(self, user_role, order_amount, category_ids=None, product_ids=None):
        """Check if promo code is applicable"""
        if self.is_expired:
            return False, "Promo code is expired or inactive"
        
        # Check role applicability
        if self.applicable_roles and user_role not in self.applicable_roles_list:
            return False, "Promo code not applicable for your role"
        
        # Check minimum order amount
        if self.min_order_amount and order_amount < float(self.min_order_amount):
            return False, f"Minimum order amount of {self.min_order_amount} required"
        
        # Check category applicability
        if self.applicable_categories and category_ids:
            if not any(cat_id in self.applicable_categories_list for cat_id in category_ids):
                return False, "Promo code not applicable for selected categories"
        
        # Check product applicability
        if self.applicable_products and product_ids:
            if not any(prod_id in self.applicable_products_list for prod_id in product_ids):
                return False, "Promo code not applicable for selected products"
        
        return True, "Valid promo code"
    
    def calculate_discount(self, order_amount):
        """Calculate discount amount"""
        if self.discount_type == 'PERCENTAGE':
            discount = (order_amount * self.discount_value / 100)
        elif self.discount_type == 'FIXED_AMOUNT':
            discount = self.discount_value
        else:
            discount = 0
        
        # Apply maximum discount limit
        if self.max_discount_amount and discount > float(self.max_discount_amount):
            discount = float(self.max_discount_amount)
        
        return min(discount, order_amount)  # Cannot discount more than order amount
    
    def use_code(self):
        """Increment usage count"""
        self.current_uses += 1
    
    def to_dict(self):
        return {
            'id': self.id,
            'code': self.code,
            'name': self.name,
            'description': self.description,
            'discount_type': self.discount_type,
            'discount_value': float(self.discount_value) if self.discount_value else 0,
            'min_order_amount': float(self.min_order_amount) if self.min_order_amount else None,
            'max_discount_amount': float(self.max_discount_amount) if self.max_discount_amount else None,
            'max_uses': self.max_uses,
            'current_uses': self.current_uses,
            'max_uses_per_user': self.max_uses_per_user,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'is_active': self.is_active,
            'is_expired': self.is_expired,
            'applicable_roles': self.applicable_roles,
            'applicable_roles_list': self.applicable_roles_list,
            'applicable_categories': self.applicable_categories,
            'applicable_categories_list': self.applicable_categories_list,
            'applicable_products': self.applicable_products,
            'applicable_products_list': self.applicable_products_list,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class PromoCodeUsage(db.Model):
    __tablename__ = 'promo_code_usage'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    promo_code_id = db.Column(db.String(36), db.ForeignKey('promo_codes.id'), nullable=False)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    order_id = db.Column(db.String(36), db.ForeignKey('orders.id'), nullable=False)
    discount_amount = db.Column(db.Numeric(10, 2), nullable=False)
    used_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    promo_code = db.relationship('PromoCode', backref='usage_records')
    user = db.relationship('User', backref='promo_code_usage')
    order = db.relationship('Order', backref='promo_code_usage')
    
    def to_dict(self):
        return {
            'id': self.id,
            'promo_code_id': self.promo_code_id,
            'user_id': self.user_id,
            'order_id': self.order_id,
            'discount_amount': float(self.discount_amount) if self.discount_amount else 0,
            'used_at': self.used_at.isoformat() if self.used_at else None,
            'promo_code': self.promo_code.to_dict() if self.promo_code else None
        }
