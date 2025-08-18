#!/usr/bin/env python3
"""
Initialize SQLite database for AuroMart
"""

import os
import sys
from pathlib import Path

# Add the server directory to Python path
server_dir = Path(__file__).parent
sys.path.insert(0, str(server_dir))

from app import create_app, db
from app.models.user import User
from app.models.product import Product
from app.models.category import Category
from app.models.order import Order, OrderItem
from app.models.cart import Cart, CartItem
from app.models.favorite import Favorite
from app.models.inventory import Inventory
from app.models.partnership import Partnership, PartnershipInvite
from app.models.invoice import Invoice
from app.models.search_history import SearchHistory
from app.models.whatsapp import WhatsAppNotification
from app.models.pricing import PricingRule
from app.models.product_allocation import ProductAllocation
from datetime import datetime
import uuid

def init_db():
    """Initialize the database with tables and sample data"""
        app = create_app()
        
        with app.app_context():
            # Create all tables
        print("Creating database tables...")
            db.create_all()
        print("✅ Database tables created successfully!")
        
        # Check if data already exists
        if User.query.first():
            print("⚠️  Database already contains data. Skipping sample data creation.")
            return
        
        print("Creating sample data...")
        
        # Create sample categories
        categories = [
            Category(name="Electronics", description="Electronic devices and accessories"),
            Category(name="Clothing", description="Fashion and apparel"),
            Category(name="Home & Garden", description="Home improvement and garden supplies"),
            Category(name="Sports", description="Sports equipment and accessories"),
            Category(name="Books", description="Books and educational materials")
        ]
        
        for category in categories:
            db.session.add(category)
        db.session.commit()
        print("✅ Categories created")
            
            # Create sample users
        users = [
            User(
                email="hrushigavhane@gmail.com",
                business_name="TechCorp Industries",
                role="manufacturer",
                phone_number="+1234567890",
                is_verified=True
            ),
            User(
                email="chikyagavhane22@gmail.com",
                business_name="TechDist Solutions",
                role="distributor",
                phone_number="+0987654321",
                is_verified=True
            ),
            User(
                email="manufacturer2@example.com",
                business_name="Global Manufacturing Co.",
                role="manufacturer",
                phone_number="+1122334455",
                is_verified=True
            ),
            User(
                email="distributor2@example.com",
                business_name="Regional Distribution Ltd.",
                role="distributor",
                phone_number="+5544332211",
                is_verified=True
            )
        ]
        
        for user in users:
            user.set_password("password123")
            db.session.add(user)
        db.session.commit()
        print("✅ Users created")
        
        # Create sample products
        products = [
            Product(
                name="Smartphone X1",
                description="Latest smartphone with advanced features",
                price=599.99,
                category_id=categories[0].id,
                manufacturer_id=users[0].id,
                stock_quantity=100,
                sku="SMART-X1-001"
            ),
            Product(
                name="Laptop Pro",
                description="Professional laptop for business use",
                price=1299.99,
                category_id=categories[0].id,
                manufacturer_id=users[0].id,
                stock_quantity=50,
                sku="LAPTOP-PRO-001"
            ),
            Product(
                name="Cotton T-Shirt",
                description="Comfortable cotton t-shirt",
                price=19.99,
                category_id=categories[1].id,
                manufacturer_id=users[2].id,
                stock_quantity=200,
                sku="TSHIRT-COT-001"
            ),
            Product(
                name="Garden Tool Set",
                description="Complete set of garden tools",
                price=89.99,
                category_id=categories[2].id,
                manufacturer_id=users[2].id,
                stock_quantity=75,
                sku="GARDEN-SET-001"
            ),
            Product(
                name="Basketball",
                description="Professional basketball",
                price=29.99,
                category_id=categories[3].id,
                manufacturer_id=users[0].id,
                stock_quantity=150,
                sku="BASKET-001"
            )
        ]
        
        for product in products:
            db.session.add(product)
        db.session.commit()
        print("✅ Products created")
        
        # Create sample partnerships
        partnerships = [
            Partnership(
                requester_id=users[0].id,  # TechCorp Industries
                partner_id=users[1].id,    # TechDist Solutions
                partnership_type="MANUFACTURER_DISTRIBUTOR",
                status="active",
                message="Looking forward to a great partnership!"
            ),
            Partnership(
                requester_id=users[2].id,  # Global Manufacturing Co.
                partner_id=users[3].id,    # Regional Distribution Ltd.
                partnership_type="MANUFACTURER_DISTRIBUTOR",
                status="active",
                message="Excited to work together!"
            )
        ]
        
        for partnership in partnerships:
            db.session.add(partnership)
        db.session.commit()
        print("✅ Partnerships created")
        
        # Create sample inventory records
        inventories = [
            Inventory(
                product_id=products[0].id,
                distributor_id=users[1].id,
                quantity=25,
                price=649.99
            ),
            Inventory(
                product_id=products[1].id,
                distributor_id=users[1].id,
                quantity=15,
                price=1349.99
            ),
            Inventory(
                product_id=products[2].id,
                distributor_id=users[3].id,
                quantity=50,
                price=24.99
            ),
            Inventory(
                product_id=products[3].id,
                distributor_id=users[3].id,
                quantity=20,
                price=99.99
            )
        ]
        
        for inventory in inventories:
            db.session.add(inventory)
        db.session.commit()
        print("✅ Inventory records created")
        
        # Create sample orders
        orders = [
            Order(
                customer_id=users[1].id,
                status="completed",
                total_amount=649.99,
                shipping_address="123 Business St, Tech City, TC 12345"
            ),
            Order(
                customer_id=users[3].id,
                status="pending",
                total_amount=124.98,
                shipping_address="456 Commerce Ave, Business District, BD 67890"
            )
        ]
        
        for order in orders:
            db.session.add(order)
        db.session.commit()
        print("✅ Orders created")
        
        # Create sample order items
        order_items = [
            OrderItem(
                order_id=orders[0].id,
                product_id=products[0].id,
                quantity=1,
                price=649.99
            ),
            OrderItem(
                order_id=orders[1].id,
                product_id=products[2].id,
                quantity=5,
                price=24.99
            ),
            OrderItem(
                order_id=orders[1].id,
                product_id=products[4].id,
                quantity=1,
                price=29.99
            )
        ]
        
        for item in order_items:
            db.session.add(item)
        db.session.commit()
        print("✅ Order items created")
        
        # Create sample cart items (ensure carts exist and use cart_id)
        from app.models.cart import Cart
        # Create carts for sample users if not exist
        for u in [users[1], users[3]]:
            if not Cart.query.filter_by(user_id=u.id).first():
                db.session.add(Cart(user_id=u.id))
        db.session.flush()

        cart_items = []
        dist_cart = Cart.query.filter_by(user_id=users[1].id).first()
        other_cart = Cart.query.filter_by(user_id=users[3].id).first()
        if dist_cart:
            cart_items.append(CartItem(
                cart_id=dist_cart.id,
                product_id=products[1].id,
                quantity=2
            ))
        if other_cart:
            cart_items.append(CartItem(
                cart_id=other_cart.id,
                product_id=products[3].id,
                quantity=1
            ))
        
        for item in cart_items:
            db.session.add(item)
        db.session.commit()
        print("✅ Cart items created")
        
        # Create sample favorites
        favorites = [
            Favorite(
                user_id=users[1].id,
                product_id=products[0].id
            ),
            Favorite(
                user_id=users[3].id,
                product_id=products[2].id
            )
        ]
        
        for favorite in favorites:
            db.session.add(favorite)
        db.session.commit()
        print("✅ Favorites created")
        
        # Create sample pricing records
        pricing_records = [
            Pricing(
                product_id=products[0].id,
                distributor_id=users[1].id,
                wholesale_price=550.00,
                retail_price=649.99,
                markup_percentage=18.18
            ),
            Pricing(
                product_id=products[1].id,
                distributor_id=users[1].id,
                wholesale_price=1200.00,
                retail_price=1349.99,
                markup_percentage=12.50
            )
        ]
        
        for pricing in pricing_records:
            db.session.add(pricing)
            db.session.commit()
        print("✅ Pricing records created")
        
        # Create sample product allocations
        allocations = [
            ProductAllocation(
                product_id=products[0].id,
                distributor_id=users[1].id,
                allocated_quantity=25,
                reserved_quantity=5
            ),
            ProductAllocation(
                product_id=products[1].id,
                distributor_id=users[1].id,
                allocated_quantity=15,
                reserved_quantity=3
            )
        ]
        
        for allocation in allocations:
            db.session.add(allocation)
        db.session.commit()
        print("✅ Product allocations created")
        
        print("🎉 Database initialization completed successfully!")
        print("\n📊 Sample Data Summary:")
        print(f"   • Users: {User.query.count()}")
        print(f"   • Categories: {Category.query.count()}")
        print(f"   • Products: {Product.query.count()}")
        print(f"   • Partnerships: {Partnership.query.count()}")
        print(f"   • Inventory Records: {Inventory.query.count()}")
        print(f"   • Orders: {Order.query.count()}")
        print(f"   • Cart Items: {CartItem.query.count()}")
        print(f"   • Favorites: {Favorite.query.count()}")
        print(f"   • Pricing Records: {Pricing.query.count()}")
        print(f"   • Product Allocations: {ProductAllocation.query.count()}")
        
        print("\n🔑 Test Accounts:")
        print("   • Manufacturer: hrushigavhane@gmail.com / password123")
        print("   • Distributor: chikyagavhane22@gmail.com / password123")
        print("   • Manufacturer 2: manufacturer2@example.com / password123")
        print("   • Distributor 2: distributor2@example.com / password123")

if __name__ == "__main__":
    init_db()
