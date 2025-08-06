from .user import db as user_db, User, UserRole
from .product import db as product_db, Product
from .inventory import db as inventory_db, Inventory
from .order import db as order_db, Order, OrderItem
from .invoice import db as invoice_db, Invoice
from .notification import db as notification_db, Notification
from .report import db as report_db, Report

# Initialize all models with the same db instance
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Reassign db instances to the shared db instance
User.db = db
UserRole.db = db
Product.db = db
Inventory.db = db
Order.db = db
OrderItem.db = db
Invoice.db = db
Notification.db = db
Report.db = db

# Import all models to ensure they are registered with the db instance
from .user import User, UserRole
from .product import Product
from .inventory import Inventory
from .order import Order, OrderItem
from .invoice import Invoice
from .notification import Notification
from .report import Report

__all__ = [
    'db',
    'User',
    'UserRole',
    'Product',
    'Inventory',
    'Order',
    'OrderItem',
    'Invoice',
    'Notification',
    'Report'
]