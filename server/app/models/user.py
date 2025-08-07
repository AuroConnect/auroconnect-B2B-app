from app import db
from datetime import datetime
import uuid
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), nullable=False, default='retailer')  # manufacturer, distributor, retailer
    business_name = db.Column(db.Text, nullable=True)
    address = db.Column(db.Text, nullable=True)
    phone_number = db.Column(db.String(50), nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __init__(self, **kwargs):
        password = kwargs.pop('password', None)
        super(User, self).__init__(**kwargs)
        if password:
            self.set_password(password)
    
    def set_password(self, password):
        """Set password hash"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check password hash"""
        if not self.password_hash:
            return False
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'role': self.role,
            'businessName': self.business_name,
            'address': self.address,
            'phoneNumber': self.phone_number,
            'isActive': self.is_active,
            'createdAt': self.created_at.isoformat() if self.created_at else None,
            'updatedAt': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def to_public_dict(self):
        """Convert to public dictionary (without sensitive info)"""
        return {
            'id': self.id,
            'name': self.name,
            'role': self.role,
            'businessName': self.business_name,
            'address': self.address,
            'phoneNumber': self.phone_number
        }
    
    def get_dashboard_url(self):
        """Get dashboard URL based on role"""
        if self.role == 'manufacturer':
            return '/manufacturer/dashboard'
        elif self.role == 'distributor':
            return '/distributor/dashboard'
        elif self.role == 'retailer':
            return '/retailer/dashboard'
        return '/dashboard'
    
    def __repr__(self):
        return f'<User {self.email}>' 