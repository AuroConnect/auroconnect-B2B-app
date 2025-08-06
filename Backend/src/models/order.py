from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import enum

db = SQLAlchemy()

class OrderStatusEnum(enum.Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    PACKED = "packed"
    DISPATCHED = "dispatched"
    DELIVERED = "delivered"

class FulfillmentTypeEnum(enum.Enum):
    DELIVERY = "delivery"
    PICKUP = "pickup"

class Order(db.Model):
    __tablename__ = 'orders'
    
    id = db.Column(db.Integer, primary_key=True)
    retailer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    distributor_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    status = db.Column(db.Enum(OrderStatusEnum), nullable=False, default=OrderStatusEnum.PENDING, index=True)
    fulfillment_type = db.Column(db.Enum(FulfillmentTypeEnum), index=True)
    tracking_number = db.Column(db.String(100), index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    # retailer relationship is defined in user.py
    # distributor relationship is defined in user.py
    order_items = db.relationship('OrderItem', backref='order', lazy=True, cascade='all, delete-orphan')
    invoice = db.relationship('Invoice', backref='order', uselist=False, cascade='all, delete-orphan')
    notifications = db.relationship('Notification', backref='order', lazy=True, cascade='all, delete-orphan')
    
    def get_status_display(self):
        """Get the display name for the order status"""
        status_names = {
            OrderStatusEnum.PENDING: "Pending",
            OrderStatusEnum.ACCEPTED: "Accepted",
            OrderStatusEnum.REJECTED: "Rejected",
            OrderStatusEnum.PACKED: "Packed",
            OrderStatusEnum.DISPATCHED: "Dispatched",
            OrderStatusEnum.DELIVERED: "Delivered"
        }
        return status_names.get(self.status, "Unknown")
    
    def get_fulfillment_display(self):
        """Get the display name for the fulfillment type"""
        fulfillment_names = {
            FulfillmentTypeEnum.DELIVERY: "Delivery",
            FulfillmentTypeEnum.PICKUP: "Pickup"
        }
        return fulfillment_names.get(self.fulfillment_type, "Not Set")
    
    def get_total_amount(self):
        """Calculate the total amount for the order"""
        return sum(item.total_price for item in self.order_items)
    
    def can_update_status(self, new_status):
        """Check if the status can be updated to the new status"""
        valid_transitions = {
            OrderStatusEnum.PENDING: [OrderStatusEnum.ACCEPTED, OrderStatusEnum.REJECTED],
            OrderStatusEnum.ACCEPTED: [OrderStatusEnum.PACKED],
            OrderStatusEnum.PACKED: [OrderStatusEnum.DISPATCHED],
            OrderStatusEnum.DISPATCHED: [OrderStatusEnum.DELIVERED],
            OrderStatusEnum.REJECTED: [],
            OrderStatusEnum.DELIVERED: []
        }
        
        return new_status in valid_transitions.get(self.status, [])
    
    def update_status(self, new_status):
        """Update the order status if valid"""
        if self.can_update_status(new_status):
            self.status = new_status
            self.updated_at = datetime.utcnow()
            return True
        return False
    
    def to_dict(self):
        """Convert the order object to a dictionary"""
        return {
            'id': self.id,
            'retailer_id': self.retailer_id,
            'retailer_name': self.retailer.company_name if self.retailer else None,
            'distributor_id': self.distributor_id,
            'distributor_name': self.distributor_orders.company_name if self.distributor_orders else None,
            'status': self.status.value,
            'status_display': self.get_status_display(),
            'fulfillment_type': self.fulfillment_type.value if self.fulfillment_type else None,
            'fulfillment_display': self.get_fulfillment_display(),
            'tracking_number': self.tracking_number,
            'total_amount': float(self.get_total_amount()),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<Order {self.id} Status:{self.status.value}>'

class OrderItem(db.Model):
    __tablename__ = 'order_items'
    
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False, index=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False, index=True)
    quantity = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Numeric(10, 2), nullable=False)
    total_price = db.Column(db.Numeric(10, 2), nullable=False)
    
    # Relationships
    # order relationship is defined in order.py
    # product relationship is defined in product.py
    
    def to_dict(self):
        """Convert the order item object to a dictionary"""
        return {
            'id': self.id,
            'order_id': self.order_id,
            'product_id': self.product_id,
            'product_name': self.product.name if self.product else None,
            'quantity': self.quantity,
            'unit_price': float(self.unit_price),
            'total_price': float(self.total_price)
        }
    
    def __repr__(self):
        return f'<OrderItem Order:{self.order_id} Product:{self.product_id} Qty:{self.quantity}>'