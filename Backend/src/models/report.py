from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import enum

db = SQLAlchemy()

class ReportTypeEnum(enum.Enum):
    SALES = "sales"
    INVENTORY = "inventory"
    MONTHLY = "monthly"

class Report(db.Model):
    __tablename__ = 'reports'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    report_type = db.Column(db.Enum(ReportTypeEnum), nullable=False, index=True)
    file_path = db.Column(db.String(500), nullable=False)
    generated_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    period_start = db.Column(db.DateTime, nullable=False)
    period_end = db.Column(db.DateTime, nullable=False)
    
    # Relationships
    # user relationship is defined in user.py
    
    def get_type_display(self):
        """Get the display name for the report type"""
        type_names = {
            ReportTypeEnum.SALES: "Sales Report",
            ReportTypeEnum.INVENTORY: "Inventory Report",
            ReportTypeEnum.MONTHLY: "Monthly Report"
        }
        return type_names.get(self.report_type, "Unknown")
    
    def to_dict(self):
        """Convert the report object to a dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'report_type': self.report_type.value,
            'report_type_display': self.get_type_display(),
            'file_path': self.file_path,
            'generated_at': self.generated_at.isoformat() if self.generated_at else None,
            'period_start': self.period_start.isoformat() if self.period_start else None,
            'period_end': self.period_end.isoformat() if self.period_end else None
        }
    
    def __repr__(self):
        return f'<Report {self.id} Type:{self.report_type.value} Generated:{self.generated_at}>'