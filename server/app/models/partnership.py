from app import db
from datetime import datetime
import uuid

class PartnerLink(db.Model):
    """PartnerLink model to handle manufacturer-distributor and distributor-retailer relationships"""
    __tablename__ = 'partner_links'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # For manufacturer-distributor links
    manufacturer_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=True)
    distributor_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=True)
    
    # For distributor-retailer links
    retailer_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=True)
    
    # Link type: 'manufacturer_distributor' or 'distributor_retailer'
    link_type = db.Column(db.String(50), nullable=False)
    
    # Link status
    status = db.Column(db.String(20), default='active')  # active, inactive
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    manufacturer = db.relationship('User', foreign_keys=[manufacturer_id], backref='manufacturer_links')
    distributor = db.relationship('User', foreign_keys=[distributor_id], backref='distributor_links')
    retailer = db.relationship('User', foreign_keys=[retailer_id], backref='retailer_links')
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'manufacturerId': self.manufacturer_id,
            'distributorId': self.distributor_id,
            'retailerId': self.retailer_id,
            'linkType': self.link_type,
            'status': self.status,
            'createdAt': self.created_at.isoformat() if self.created_at else None,
            'updatedAt': self.updated_at.isoformat() if self.updated_at else None,
            'manufacturer': self.manufacturer.to_public_dict() if self.manufacturer else None,
            'distributor': self.distributor.to_public_dict() if self.distributor else None,
            'retailer': self.retailer.to_public_dict() if self.retailer else None,
        }
    
    @staticmethod
    def get_manufacturer_distributors(manufacturer_id):
        """Get all distributors for a manufacturer"""
        return PartnerLink.query.filter_by(
            manufacturer_id=manufacturer_id,
            link_type='manufacturer_distributor',
            status='active'
        ).all()
    
    @staticmethod
    def get_distributor_manufacturer(distributor_id):
        """Get manufacturer for a distributor"""
        return PartnerLink.query.filter_by(
            distributor_id=distributor_id,
            link_type='manufacturer_distributor',
            status='active'
        ).first()
    
    @staticmethod
    def get_distributor_retailers(distributor_id):
        """Get all retailers for a distributor"""
        return PartnerLink.query.filter_by(
            distributor_id=distributor_id,
            link_type='distributor_retailer',
            status='active'
        ).all()
    
    @staticmethod
    def get_retailer_distributor(retailer_id):
        """Get distributor for a retailer"""
        return PartnerLink.query.filter_by(
            retailer_id=retailer_id,
            link_type='distributor_retailer',
            status='active'
        ).first()
    
    def __repr__(self):
        return f'<PartnerLink {self.link_type}>' 