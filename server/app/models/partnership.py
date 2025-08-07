from app import db
from datetime import datetime
import uuid

class Partnership(db.Model):
    """Partnership model to handle manufacturer-distributor-retailer relationships"""
    __tablename__ = 'partnerships'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Partnership type: 'manufacturer_distributor' or 'distributor_retailer'
    partnership_type = db.Column(db.String(50), nullable=False)
    
    # For manufacturer-distributor partnerships
    manufacturer_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=True)
    distributor_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=True)
    
    # For distributor-retailer partnerships
    retailer_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=True)
    
    # Partnership status
    status = db.Column(db.String(20), default='active')  # active, inactive, pending
    
    # Partnership details
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    manufacturer = db.relationship('User', foreign_keys=[manufacturer_id], backref='manufacturer_partnerships')
    distributor = db.relationship('User', foreign_keys=[distributor_id], backref='distributor_partnerships')
    retailer = db.relationship('User', foreign_keys=[retailer_id], backref='retailer_partnerships')
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'partnership_type': self.partnership_type,
            'manufacturer_id': self.manufacturer_id,
            'distributor_id': self.distributor_id,
            'retailer_id': self.retailer_id,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'manufacturer': self.manufacturer.to_dict() if self.manufacturer else None,
            'distributor': self.distributor.to_dict() if self.distributor else None,
            'retailer': self.retailer.to_dict() if self.retailer else None,
        }
    
    @staticmethod
    def get_manufacturer_distributors(manufacturer_id):
        """Get all distributors for a manufacturer"""
        return Partnership.query.filter_by(
            manufacturer_id=manufacturer_id,
            partnership_type='manufacturer_distributor',
            status='active'
        ).all()
    
    @staticmethod
    def get_distributor_manufacturer(distributor_id):
        """Get manufacturer for a distributor"""
        return Partnership.query.filter_by(
            distributor_id=distributor_id,
            partnership_type='manufacturer_distributor',
            status='active'
        ).first()
    
    @staticmethod
    def get_distributor_retailers(distributor_id):
        """Get all retailers for a distributor"""
        return Partnership.query.filter_by(
            distributor_id=distributor_id,
            partnership_type='distributor_retailer',
            status='active'
        ).all()
    
    @staticmethod
    def get_retailer_distributor(retailer_id):
        """Get distributor for a retailer"""
        return Partnership.query.filter_by(
            retailer_id=retailer_id,
            partnership_type='distributor_retailer',
            status='active'
        ).first() 