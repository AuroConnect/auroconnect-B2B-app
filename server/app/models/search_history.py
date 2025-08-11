from app import db
from datetime import datetime
import uuid

class SearchHistory(db.Model):
    __tablename__ = 'search_history'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    search_term = db.Column(db.String(255), nullable=False)
    search_type = db.Column(db.String(50), nullable=False)
    result_count = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='search_history')
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': str(self.id),
            'userId': str(self.user_id),
            'searchTerm': self.search_term,
            'searchType': self.search_type,
            'resultCount': self.result_count,
            'createdAt': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<SearchHistory {self.search_term} - {self.result_count}>' 