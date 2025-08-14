from app import db
from datetime import datetime
import uuid

class Order(db.Model):
    __tablename__ = 'orders'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    buyer_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    seller_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    status = db.Column(db.String(50), nullable=False, default='PENDING')
    delivery_option = db.Column(db.String(50), default='DELIVER_TO_BUYER')
    notes = db.Column(db.Text)
    internal_notes = db.Column(db.Text)
    total_amount = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    
    # New fields for enhanced features
    order_tags = db.Column(db.String(200))  # Comma-separated tags: URGENT,BULK,PROMO
    allow_split_shipment = db.Column(db.Boolean, default=False)
    allow_backorders = db.Column(db.Boolean, default=False)
    expected_delivery_date = db.Column(db.Date, nullable=True)
    priority = db.Column(db.String(20), default='NORMAL')  # LOW, NORMAL, HIGH, URGENT
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    buyer = db.relationship('User', foreign_keys=[buyer_id], backref='buying_orders')
    seller = db.relationship('User', foreign_keys=[seller_id], backref='selling_orders')
    items = db.relationship('OrderItem', backref='order', lazy=True, cascade='all, delete-orphan')
    shipments = db.relationship('Shipment', backref='order', lazy=True, cascade='all, delete-orphan')
    chat_messages = db.relationship('OrderChat', backref='order', lazy=True, cascade='all, delete-orphan')
    
    @property
    def tags_list(self):
        """Get order tags as list"""
        return [tag.strip() for tag in self.order_tags.split(',')] if self.order_tags else []
    
    @property
    def is_urgent(self):
        """Check if order is urgent"""
        return 'URGENT' in self.tags_list or self.priority == 'URGENT'
    
    @property
    def is_bulk(self):
        """Check if order is bulk"""
        return 'BULK' in self.tags_list
    
    @property
    def has_backorders(self):
        """Check if order has backordered items"""
        return any(item.is_backordered for item in self.items)
    
    @property
    def can_split_shipment(self):
        """Check if order can be split into multiple shipments"""
        return self.allow_split_shipment and len(self.items) > 1
    
    def add_tag(self, tag):
        """Add a tag to the order"""
        current_tags = self.tags_list
        if tag.upper() not in [t.upper() for t in current_tags]:
            current_tags.append(tag.upper())
            self.order_tags = ','.join(current_tags)
    
    def remove_tag(self, tag):
        """Remove a tag from the order"""
        current_tags = self.tags_list
        current_tags = [t for t in current_tags if t.upper() != tag.upper()]
        self.order_tags = ','.join(current_tags) if current_tags else None
    
    def to_dict(self):
        return {
            'id': self.id,
            'buyer_id': self.buyer_id,
            'seller_id': self.seller_id,
            'status': self.status,
            'delivery_option': self.delivery_option,
            'notes': self.notes,
            'internal_notes': self.internal_notes,
            'total_amount': float(self.total_amount) if self.total_amount else 0,
            'order_tags': self.order_tags,
            'tags_list': self.tags_list,
            'allow_split_shipment': self.allow_split_shipment,
            'allow_backorders': self.allow_backorders,
            'expected_delivery_date': self.expected_delivery_date.isoformat() if self.expected_delivery_date else None,
            'priority': self.priority,
            'is_urgent': self.is_urgent,
            'is_bulk': self.is_bulk,
            'has_backorders': self.has_backorders,
            'can_split_shipment': self.can_split_shipment,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'buyer': {
                'id': self.buyer.id,
                'business_name': self.buyer.business_name,
                'email': self.buyer.email
            } if self.buyer else None,
            'seller': {
                'id': self.seller.id,
                'business_name': self.seller.business_name,
                'email': self.seller.email
            } if self.seller else None,
            'items': [item.to_dict() for item in self.items],
            'shipments': [shipment.to_dict() for shipment in self.shipments]
        }

class OrderItem(db.Model):
    __tablename__ = 'order_items'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    order_id = db.Column(db.String(36), db.ForeignKey('orders.id'), nullable=False)
    product_id = db.Column(db.String(36), db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    unit_price = db.Column(db.Numeric(10, 2), nullable=False)
    total_price = db.Column(db.Numeric(10, 2), nullable=False)
    
    # New fields for backorders and split shipments
    quantity_shipped = db.Column(db.Integer, nullable=False, default=0)
    quantity_backordered = db.Column(db.Integer, nullable=False, default=0)
    backorder_expected_date = db.Column(db.Date, nullable=True)
    is_backordered = db.Column(db.Boolean, default=False)
    
    # Relationships
    product = db.relationship('Product', backref='order_items')
    
    @property
    def quantity_pending(self):
        """Get pending quantity (ordered - shipped)"""
        return max(0, self.quantity - self.quantity_shipped)
    
    @property
    def is_fully_shipped(self):
        """Check if item is fully shipped"""
        return self.quantity_shipped >= self.quantity
    
    @property
    def is_partially_shipped(self):
        """Check if item is partially shipped"""
        return 0 < self.quantity_shipped < self.quantity
    
    def update_shipped_quantity(self, shipped_qty):
        """Update shipped quantity and handle backorders"""
        if shipped_qty > self.quantity:
            shipped_qty = self.quantity
        
        self.quantity_shipped = shipped_qty
        self.quantity_backordered = max(0, self.quantity - shipped_qty)
        self.is_backordered = self.quantity_backordered > 0
        
        if self.is_backordered and not self.backorder_expected_date:
            # Set default backorder date to 30 days from now
            from datetime import timedelta
            self.backorder_expected_date = datetime.utcnow().date() + timedelta(days=30)
    
    def to_dict(self):
        return {
            'id': self.id,
            'order_id': self.order_id,
            'product_id': self.product_id,
            'quantity': self.quantity,
            'unit_price': float(self.unit_price) if self.unit_price else 0,
            'total_price': float(self.total_price) if self.total_price else 0,
            'quantity_shipped': self.quantity_shipped,
            'quantity_backordered': self.quantity_backordered,
            'quantity_pending': self.quantity_pending,
            'backorder_expected_date': self.backorder_expected_date.isoformat() if self.backorder_expected_date else None,
            'is_backordered': self.is_backordered,
            'is_fully_shipped': self.is_fully_shipped,
            'is_partially_shipped': self.is_partially_shipped,
            'product': {
                'id': self.product.id,
                'name': self.product.name,
                'sku': self.product.sku,
                'image_url': self.product.image_url
            } if self.product else None
        }

class Shipment(db.Model):
    __tablename__ = 'shipments'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    order_id = db.Column(db.String(36), db.ForeignKey('orders.id'), nullable=False)
    shipment_number = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(50), nullable=False, default='PENDING')  # PENDING, SHIPPED, DELIVERED
    tracking_number = db.Column(db.String(100), nullable=True)
    carrier = db.Column(db.String(50), nullable=True)
    shipped_date = db.Column(db.DateTime, nullable=True)
    delivered_date = db.Column(db.DateTime, nullable=True)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    items = db.relationship('ShipmentItem', backref='shipment', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'order_id': self.order_id,
            'shipment_number': self.shipment_number,
            'status': self.status,
            'tracking_number': self.tracking_number,
            'carrier': self.carrier,
            'shipped_date': self.shipped_date.isoformat() if self.shipped_date else None,
            'delivered_date': self.delivered_date.isoformat() if self.delivered_date else None,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'items': [item.to_dict() for item in self.items]
        }

class ShipmentItem(db.Model):
    __tablename__ = 'shipment_items'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    shipment_id = db.Column(db.String(36), db.ForeignKey('shipments.id'), nullable=False)
    order_item_id = db.Column(db.String(36), db.ForeignKey('order_items.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    
    # Relationships
    order_item = db.relationship('OrderItem', backref='shipment_items')
    
    def to_dict(self):
        return {
            'id': self.id,
            'shipment_id': self.shipment_id,
            'order_item_id': self.order_item_id,
            'quantity': self.quantity,
            'order_item': self.order_item.to_dict() if self.order_item else None
        }

class OrderChat(db.Model):
    __tablename__ = 'order_chat'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    order_id = db.Column(db.String(36), db.ForeignKey('orders.id'), nullable=False)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    message = db.Column(db.Text, nullable=False)
    message_type = db.Column(db.String(20), default='TEXT')  # TEXT, SYSTEM, ALERT
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='order_chat_messages')
    
    def to_dict(self):
        return {
            'id': self.id,
            'order_id': self.order_id,
            'user_id': self.user_id,
            'message': self.message,
            'message_type': self.message_type,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'user': {
                'id': self.user.id,
                'business_name': self.user.business_name,
                'email': self.user.email
            } if self.user else None
        } 