from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import enum

db = SQLAlchemy()

class UserRoleEnum(enum.Enum):
    MANUFACTURER = "manufacturer"
    DISTRIBUTOR = "distributor"
    RETAILER = "retailer"

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    company_name = db.Column(db.String(255), nullable=False)
    address = db.Column(db.Text, nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    role = db.Column(db.Enum(UserRoleEnum), nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    user_roles = db.relationship('UserRole', backref='user', lazy=True, cascade='all, delete-orphan')
    inventories_managed = db.relationship('Inventory', foreign_keys='Inventory.distributor_id', backref='distributor', lazy=True)
    orders_placed = db.relationship('Order', foreign_keys='Order.retailer_id', backref='retailer', lazy=True)
    orders_fulfilled = db.relationship('Order', foreign_keys='Order.distributor_id', backref='distributor_orders', lazy=True)
    notifications = db.relationship('Notification', backref='user', lazy=True)
    reports = db.relationship('Report', backref='user', lazy=True)
    
    def set_password(self, password):
        """Hash and set the user's password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if the provided password matches the hashed password"""
        return check_password_hash(self.password_hash, password)
    
    def is_manufacturer(self):
        """Check if the user is a manufacturer"""
        return self.role == UserRoleEnum.MANUFACTURER
    
    def is_distributor(self):
        """Check if the user is a distributor"""
        return self.role == UserRoleEnum.DISTRIBUTOR
    
    def is_retailer(self):
        """Check if the user is a retailer"""
        return self.role == UserRoleEnum.RETAILER
    
    def get_role_display(self):
        """Get the display name for the user's role"""
        role_names = {
            UserRoleEnum.MANUFACTURER: "Manufacturer",
            UserRoleEnum.DISTRIBUTOR: "Distributor",
            UserRoleEnum.RETAILER: "Retailer"
        }
        return role_names.get(self.role, "Unknown")
    
    def to_dict(self):
        """Convert the user object to a dictionary"""
        return {
            'id': self.id,
            'email': self.email,
            'name': self.name,
            'company_name': self.company_name,
            'address': self.address,
            'phone': self.phone,
            'role': self.role.value,
            'role_display': self.get_role_display(),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<User {self.email} ({self.company_name})>'

class UserRole(db.Model):
    __tablename__ = 'user_roles'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    role = db.Column(db.Enum(UserRoleEnum), nullable=False)
    assigned_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f'<UserRole {self.user_id} - {self.role.value}>'