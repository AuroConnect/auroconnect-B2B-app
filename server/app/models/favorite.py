from app import db
from datetime import datetime
import uuid

class Favorite(db.Model):
    __tablename__ = 'favorites'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    favorite_user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    favorite_type = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', foreign_keys=[user_id], backref='favorites')
    favorite_user = db.relationship('User', foreign_keys=[favorite_user_id], backref='favorited_by')
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': str(self.id),
            'userId': str(self.user_id),
            'favoriteUserId': str(self.favorite_user_id),
            'favoriteType': self.favorite_type,
            'createdAt': self.created_at.isoformat() if self.created_at else None,
            'favoriteUser': self.favorite_user.to_public_dict() if self.favorite_user else None
        }
    
    def __repr__(self):
        return f'<Favorite {self.user_id} -> {self.favorite_user_id}>' 