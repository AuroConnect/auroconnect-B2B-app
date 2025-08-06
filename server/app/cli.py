import click
from flask.cli import with_appcontext
from app import db
from app.models import User, Category, Product, Order, OrderItem, Partnership, Favorite, WhatsAppNotification
from datetime import datetime, timedelta
import uuid
import random

def register_commands(app):
    """Register CLI commands"""
    
    @app.cli.command()
    @with_appcontext
    def init_db():
        """Initialize the database"""
        db.create_all()
        click.echo('Database initialized!')
    
    @app.cli.command()
    @with_appcontext
    def seed():
        """Seed the database with comprehensive sample data"""
        
        # Clear existing data
        click.echo('Clearing existing data...')
        WhatsAppNotification.query.delete()
        OrderItem.query.delete()
        Order.query.delete()
        # Clear inventory first due to foreign key constraints
        from app.models import Inventory
        Inventory.query.delete()
        Product.query.delete()
        Category.query.delete()
        Partnership.query.delete()
        Favorite.query.delete()
        User.query.delete()
        db.session.commit()
        
        # Create sample categories
        click.echo('Creating categories...')
        categories = [
            Category(id=str(uuid.uuid4()), name="Electronics", description="Electronic devices and accessories"),
            Category(id=str(uuid.uuid4()), name="Furniture", description="Office and home furniture"),
            Category(id=str(uuid.uuid4()), name="Clothing", description="Apparel and fashion items"),
            Category(id=str(uuid.uuid4()), name="Food & Beverages", description="Food products and beverages"),
            Category(id=str(uuid.uuid4()), name="Automotive", description="Automotive parts and accessories"),
            Category(id=str(uuid.uuid4()), name="Healthcare", description="Medical and healthcare products"),
            Category(id=str(uuid.uuid4()), name="Sports & Fitness", description="Sports equipment and fitness gear"),
            Category(id=str(uuid.uuid4()), name="Books & Stationery", description="Books and office supplies")
        ]
        
        for category in categories:
            db.session.add(category)
        db.session.commit()
        
        # Create sample users for each role
        click.echo('Creating users...')
        
        # Retailers
        retailers = [
            User(
                id=str(uuid.uuid4()),
                email="retailer1@test.com",
                first_name="Rajesh",
                last_name="Kumar",
                role="retailer",
                business_name="TechMart Electronics",
                phone_number="+91-9876543210",
                whatsapp_number="+91-9876543210",
                address="123 Main Street, Mumbai, Maharashtra",
                is_active=True,
                password="password123"
            ),
            User(
                id=str(uuid.uuid4()),
                email="retailer2@test.com",
                first_name="Priya",
                last_name="Sharma",
                role="retailer",
                business_name="Fashion Forward",
                phone_number="+91-9876543211",
                whatsapp_number="+91-9876543211",
                address="456 Park Avenue, Delhi, Delhi",
                is_active=True,
                password="password123"
            ),
            User(
                id=str(uuid.uuid4()),
                email="retailer3@test.com",
                first_name="Amit",
                last_name="Patel",
                role="retailer",
                business_name="Office Supplies Plus",
                phone_number="+91-9876543212",
                whatsapp_number="+91-9876543212",
                address="789 Business District, Bangalore, Karnataka",
                is_active=True,
                password="password123"
            )
        ]
        
        # Distributors
        distributors = [
            User(
                id=str(uuid.uuid4()),
                email="distributor1@test.com",
                first_name="Vikram",
                last_name="Singh",
                role="distributor",
                business_name="Global Distribution Co",
                phone_number="+91-9876543220",
                whatsapp_number="+91-9876543220",
                address="321 Industrial Area, Mumbai, Maharashtra",
                is_active=True,
                password="password123"
            ),
            User(
                id=str(uuid.uuid4()),
                email="distributor2@test.com",
                first_name="Meera",
                last_name="Joshi",
                role="distributor",
                business_name="Premium Distributors",
                phone_number="+91-9876543221",
                whatsapp_number="+91-9876543221",
                address="654 Trade Center, Delhi, Delhi",
                is_active=True,
                password="password123"
            ),
            User(
                id=str(uuid.uuid4()),
                email="distributor3@test.com",
                first_name="Suresh",
                last_name="Reddy",
                role="distributor",
                business_name="South India Distributors",
                phone_number="+91-9876543222",
                whatsapp_number="+91-9876543222",
                address="987 Logistics Park, Chennai, Tamil Nadu",
                is_active=True,
                password="password123"
            )
        ]
        
        # Manufacturers
        manufacturers = [
            User(
                id=str(uuid.uuid4()),
                email="hrushikesh@auromart.com",
                first_name="Hrushikesh",
                last_name="Waghmare",
                role="manufacturer",
                business_name="AuroMart Manufacturing",
                phone_number="+91-9876543230",
                whatsapp_number="+91-9876543230",
                address="147 Manufacturing Hub, Pune, Maharashtra",
                is_active=True,
                password="password123"
            ),
            User(
                id=str(uuid.uuid4()),
                email="manufacturer1@test.com",
                first_name="Arun",
                last_name="Gupta",
                role="manufacturer",
                business_name="TechPro Manufacturing",
                phone_number="+91-9876543231",
                whatsapp_number="+91-9876543231",
                address="258 Manufacturing Hub, Pune, Maharashtra",
                is_active=True,
                password="password123"
            ),
            User(
                id=str(uuid.uuid4()),
                email="manufacturer2@test.com",
                first_name="Lakshmi",
                last_name="Iyer",
                role="manufacturer",
                business_name="Fashion Factory Ltd",
                phone_number="+91-9876543232",
                whatsapp_number="+91-9876543232",
                address="369 Textile Zone, Surat, Gujarat",
                is_active=True,
                password="password123"
            ),
            User(
                id=str(uuid.uuid4()),
                email="manufacturer3@test.com",
                first_name="Ramesh",
                last_name="Kumar",
                role="manufacturer",
                business_name="Furniture Craft Industries",
                phone_number="+91-9876543233",
                whatsapp_number="+91-9876543233",
                address="456 Wood Industrial Area, Jodhpur, Rajasthan",
                is_active=True,
                password="password123"
            )
        ]
        
        all_users = retailers + distributors + manufacturers
        
        for user in all_users:
            db.session.add(user)
        db.session.commit()
        
        # Create sample products
        click.echo('Creating products...')
        products = []
        
        # AuroMart products (manufactured by Hrushikesh)
        auromart_products = [
            Product(
                id=str(uuid.uuid4()),
                name="AuroMart Premium Laptop Pro",
                description="High-performance laptop with latest Intel processor and 16GB RAM",
                sku="AM-LAPTOP-001",
                category_id=categories[0].id,  # Electronics
                manufacturer_id=manufacturers[3].id,  # Hrushikesh's company
                image_url="https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=400",
                base_price=75000.00,
                is_active=True
            ),
            Product(
                id=str(uuid.uuid4()),
                name="AuroMart Business Laptop",
                description="Reliable business laptop with security features and long battery life",
                sku="AM-LAPTOP-002",
                category_id=categories[0].id,  # Electronics
                manufacturer_id=manufacturers[3].id,  # Hrushikesh's company
                image_url="https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=400",
                base_price=65000.00,
                is_active=True
            ),
        ]

        # ASUS Products (manufactured by manufacturer1)
        asus_products = [
            Product(
                id=str(uuid.uuid4()),
                name="ASUS VivoBook S15",
                description="Student/Everyday Use laptop with Intel i5, 8GB RAM, 512GB SSD",
                sku="ASUS-VIVO-001",
                category_id=categories[0].id,  # Electronics
                manufacturer_id=manufacturers[0].id,
                image_url="https://images.unsplash.com/photo-1541807084-5c52b6b3adef?w=400",
                base_price=45000.00,
                is_active=True
            ),
            Product(
                id=str(uuid.uuid4()),
                name="ASUS ROG Strix G15",
                description="High-End Gaming laptop with RTX 4060, 16GB RAM, 1TB SSD",
                sku="ASUS-ROG-001",
                category_id=categories[0].id,  # Electronics
                manufacturer_id=manufacturers[0].id,
                image_url="https://images.unsplash.com/photo-1593642632823-8f785ba67e45?w=400",
                base_price=95000.00,
                is_active=True
            ),
            Product(
                id=str(uuid.uuid4()),
                name="ASUS TUF Gaming A15",
                description="Mid-Range Gaming laptop with GTX 1650, 8GB RAM, 512GB SSD",
                sku="ASUS-TUF-001",
                category_id=categories[0].id,  # Electronics
                manufacturer_id=manufacturers[0].id,
                image_url="https://images.unsplash.com/photo-1544735716-392fe248dcec?w=400",
                base_price=65000.00,
                is_active=True
            ),
        ]

        # HP Products (manufactured by manufacturer2)
        hp_products = [
            Product(
                id=str(uuid.uuid4()),
                name="HP ProBook 450 G8",
                description="Business/Office Use laptop with Intel i7, 16GB RAM, 512GB SSD",
                sku="HP-PRO-001",
                category_id=categories[0].id,  # Electronics
                manufacturer_id=manufacturers[1].id,
                image_url="https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=400",
                base_price=75000.00,
                is_active=True
            ),
            Product(
                id=str(uuid.uuid4()),
                name="HP Victus 16",
                description="Gaming (Mid-range) laptop with RTX 3050, 8GB RAM, 512GB SSD",
                sku="HP-VICTUS-001",
                category_id=categories[0].id,  # Electronics
                manufacturer_id=manufacturers[1].id,
                image_url="https://images.unsplash.com/photo-1593642632823-8f785ba67e45?w=400",
                base_price=70000.00,
                is_active=True
            ),
            Product(
                id=str(uuid.uuid4()),
                name="HP Omen 15",
                description="High-End Gaming laptop with RTX 4070, 16GB RAM, 1TB SSD",
                sku="HP-OMEN-001",
                category_id=categories[0].id,  # Electronics
                manufacturer_id=manufacturers[1].id,
                image_url="https://images.unsplash.com/photo-1544735716-392fe248dcec?w=400",
                base_price=120000.00,
                is_active=True
            ),
        ]

        # Dell Products (manufactured by manufacturer3)
        dell_products = [
            Product(
                id=str(uuid.uuid4()),
                name="Dell Inspiron 15 3000",
                description="Student/Budget laptop with Intel i3, 4GB RAM, 256GB SSD",
                sku="DELL-INS-001",
                category_id=categories[0].id,  # Electronics
                manufacturer_id=manufacturers[2].id,
                image_url="https://images.unsplash.com/photo-1541807084-5c52b6b3adef?w=400",
                base_price=35000.00,
                is_active=True
            ),
            Product(
                id=str(uuid.uuid4()),
                name="Dell G Series G15",
                description="Mid-Range Gaming laptop with GTX 1650, 8GB RAM, 512GB SSD",
                sku="DELL-G-001",
                category_id=categories[0].id,  # Electronics
                manufacturer_id=manufacturers[2].id,
                image_url="https://images.unsplash.com/photo-1593642632823-8f785ba67e45?w=400",
                base_price=60000.00,
                is_active=True
            ),
            Product(
                id=str(uuid.uuid4()),
                name="Dell Alienware m15",
                description="High-End Gaming laptop with RTX 4080, 32GB RAM, 2TB SSD",
                sku="DELL-ALIEN-001",
                category_id=categories[0].id,  # Electronics
                manufacturer_id=manufacturers[2].id,
                image_url="https://images.unsplash.com/photo-1544735716-392fe248dcec?w=400",
                base_price=180000.00,
                is_active=True
            ),
        ]

        # Lenovo Products (manufactured by manufacturer4)
        lenovo_products = [
            Product(
                id=str(uuid.uuid4()),
                name="Lenovo IdeaPad 3",
                description="Budget/Students laptop with Intel i3, 4GB RAM, 256GB SSD",
                sku="LENOVO-IDEA-001",
                category_id=categories[0].id,  # Electronics
                manufacturer_id=manufacturers[3].id,
                image_url="https://images.unsplash.com/photo-1541807084-5c52b6b3adef?w=400",
                base_price=32000.00,
                is_active=True
            ),
            Product(
                id=str(uuid.uuid4()),
                name="Lenovo Legion 5",
                description="Gaming laptop with RTX 3060, 16GB RAM, 512GB SSD",
                sku="LENOVO-LEGION-001",
                category_id=categories[0].id,  # Electronics
                manufacturer_id=manufacturers[3].id,
                image_url="https://images.unsplash.com/photo-1593642632823-8f785ba67e45?w=400",
                base_price=85000.00,
                is_active=True
            ),
            Product(
                id=str(uuid.uuid4()),
                name="Lenovo ThinkPad X1 Carbon",
                description="Business/Corporate laptop with Intel i7, 16GB RAM, 1TB SSD",
                sku="LENOVO-THINK-001",
                category_id=categories[0].id,  # Electronics
                manufacturer_id=manufacturers[3].id,
                image_url="https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=400",
                base_price=95000.00,
                is_active=True
            ),
        ]

        # Acer Products (manufactured by manufacturer3)
        acer_products = [
            Product(
                id=str(uuid.uuid4()),
                name="Acer Aspire 5",
                description="Budget/Entry-level laptop with Intel i3, 4GB RAM, 256GB SSD",
                sku="ACER-ASPIRE-001",
                category_id=categories[0].id,  # Electronics
                manufacturer_id=manufacturers[2].id,
                image_url="https://images.unsplash.com/photo-1541807084-5c52b6b3adef?w=400",
                base_price=28000.00,
                is_active=True
            ),
            Product(
                id=str(uuid.uuid4()),
                name="Acer Nitro 5",
                description="Gaming (Affordable) laptop with GTX 1650, 8GB RAM, 512GB SSD",
                sku="ACER-NITRO-001",
                category_id=categories[0].id,  # Electronics
                manufacturer_id=manufacturers[2].id,
                image_url="https://images.unsplash.com/photo-1593642632823-8f785ba67e45?w=400",
                base_price=55000.00,
                is_active=True
            ),
            Product(
                id=str(uuid.uuid4()),
                name="Acer Predator Helios 300",
                description="Premium Gaming laptop with RTX 3070, 16GB RAM, 1TB SSD",
                sku="ACER-PRED-001",
                category_id=categories[0].id,  # Electronics
                manufacturer_id=manufacturers[2].id,
                image_url="https://images.unsplash.com/photo-1544735716-392fe248dcec?w=400",
                base_price=110000.00,
                is_active=True
            ),
        ]

        # Electronics products (manufactured by manufacturer1)
        electronics_products = [
            Product(
                id=str(uuid.uuid4()),
                name="Smart LED TV 55\"",
                description="4K Ultra HD Smart LED Television with Android OS",
                sku="TV-55-4K-001",
                category_id=categories[0].id,  # Electronics
                manufacturer_id=manufacturers[0].id,
                image_url="https://images.unsplash.com/photo-1593359677879-a4bb92f829d1?w=400",
                base_price=45000.00,
                is_active=True
            ),
            Product(
                id=str(uuid.uuid4()),
                name="Wireless Bluetooth Headphones",
                description="Premium noise-cancelling wireless headphones",
                sku="HP-BT-001",
                category_id=categories[0].id,  # Electronics
                manufacturer_id=manufacturers[0].id,
                image_url="https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=400",
                base_price=2500.00,
                is_active=True
            ),
        ]

        # Clothing products (manufactured by manufacturer2)
        clothing_products = [
            Product(
                id=str(uuid.uuid4()),
                name="Premium Cotton T-Shirt",
                description="High-quality cotton t-shirt with modern design",
                sku="TSHIRT-COTTON-001",
                category_id=categories[1].id,  # Clothing
                manufacturer_id=manufacturers[1].id,
                image_url="https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=400",
                base_price=800.00,
                is_active=True
            ),
            Product(
                id=str(uuid.uuid4()),
                name="Denim Jeans",
                description="Comfortable denim jeans with stretch fabric",
                sku="JEANS-DENIM-001",
                category_id=categories[1].id,  # Clothing
                manufacturer_id=manufacturers[1].id,
                image_url="https://images.unsplash.com/photo-1542272604-787c3835535d?w=400",
                base_price=1200.00,
                is_active=True
            ),
        ]

        # Furniture products (manufactured by manufacturer3)
        furniture_products = [
            Product(
                id=str(uuid.uuid4()),
                name="Ergonomic Office Chair",
                description="Comfortable office chair with lumbar support",
                sku="CHAIR-OFFICE-001",
                category_id=categories[2].id,  # Furniture
                manufacturer_id=manufacturers[2].id,
                image_url="https://images.unsplash.com/photo-1586023492125-27b2c045efd7?w=400",
                base_price=8500.00,
                is_active=True
            ),
            Product(
                id=str(uuid.uuid4()),
                name="Modern Coffee Table",
                description="Elegant coffee table with glass top",
                sku="TABLE-COFFEE-001",
                category_id=categories[2].id,  # Furniture
                manufacturer_id=manufacturers[2].id,
                image_url="https://images.unsplash.com/photo-1533090481720-856c6e3c1fdc?w=400",
                base_price=12000.00,
                is_active=True
            ),
        ]

        products = auromart_products + asus_products + hp_products + dell_products + lenovo_products + acer_products + electronics_products + clothing_products + furniture_products
        
        for product in products:
            db.session.add(product)
        db.session.commit()
        
        # Create sample orders
        click.echo('Creating orders...')
        orders = []
        
        # Orders from retailers to distributors
        order_data = [
            # AuroMart product orders (Hrushikesh's products)
            {
                'retailer': retailers[0],
                'distributor': distributors[0],
                'products': [auromart_products[0], auromart_products[1]],  # AuroMart Laptops
                'quantities': [5, 3],
                'status': 'delivered',
                'date': datetime.utcnow() - timedelta(days=5)
            },
            {
                'retailer': retailers[1],
                'distributor': distributors[1],
                'products': [asus_products[0], asus_products[1]],  # ASUS Laptops
                'quantities': [8, 4],
                'status': 'shipped',
                'date': datetime.utcnow() - timedelta(days=3)
            },
            {
                'retailer': retailers[2],
                'distributor': distributors[2],
                'products': [hp_products[0], hp_products[1]],  # HP Laptops
                'quantities': [6, 2],
                'status': 'pending',
                'date': datetime.utcnow() - timedelta(days=1)
            },
            {
                'retailer': retailers[0],
                'distributor': distributors[1],
                'products': [dell_products[0], dell_products[1]],  # Dell Laptops
                'quantities': [10, 5],
                'status': 'accepted',
                'date': datetime.utcnow() - timedelta(days=2)
            },
            {
                'retailer': retailers[1],
                'distributor': distributors[1],
                'products': [lenovo_products[0], lenovo_products[1]],  # Lenovo Laptops
                'quantities': [7, 3],
                'status': 'rejected',
                'date': datetime.utcnow() - timedelta(days=4)
            },
            {
                'retailer': retailers[2],
                'distributor': distributors[2],
                'products': [acer_products[0], acer_products[1]],  # Acer Laptops
                'quantities': [4, 6],
                'status': 'processing',
                'date': datetime.utcnow() - timedelta(hours=12)
            }
        ]
        
        for i, data in enumerate(order_data):
            order = Order(
                id=str(uuid.uuid4()),
                order_number=f"ORD-{datetime.now().strftime('%Y%m%d')}-{i+1:03d}",
                retailer_id=data['retailer'].id,
                distributor_id=data['distributor'].id,
                status=data['status'],
                total_amount=sum(p.base_price * q for p, q in zip(data['products'], data['quantities'])),
                notes=f"Order from {data['retailer'].business_name}",
                created_at=data['date'],
                updated_at=data['date']
            )
            db.session.add(order)
            db.session.flush()  # Get the order ID
            
            # Create order items
            for product, quantity in zip(data['products'], data['quantities']):
                order_item = OrderItem(
                    id=str(uuid.uuid4()),
                    order_id=order.id,
                    product_id=product.id,
                    quantity=quantity,
                    unit_price=product.base_price,
                    total_price=product.base_price * quantity
                )
                db.session.add(order_item)
            
            orders.append(order)
        
        db.session.commit()
        
        # Create sample partnerships
        click.echo('Creating partnerships...')
        partnerships = [
            # AuroMart partnerships (Hrushikesh's company)
            Partnership(
                id=str(uuid.uuid4()),
                requester_id=distributors[0].id,
                partner_id=manufacturers[0].id,  # Hrushikesh's AuroMart Manufacturing
                status='accepted',
                partnership_type='distributor_manufacturer',
                created_at=datetime.utcnow() - timedelta(days=30)
            ),
            Partnership(
                id=str(uuid.uuid4()),
                requester_id=distributors[1].id,
                partner_id=manufacturers[0].id,  # Hrushikesh's AuroMart Manufacturing
                status='accepted',
                partnership_type='distributor_manufacturer',
                created_at=datetime.utcnow() - timedelta(days=25)
            ),
            Partnership(
                id=str(uuid.uuid4()),
                requester_id=distributors[2].id,
                partner_id=manufacturers[0].id,  # Hrushikesh's AuroMart Manufacturing
                status='accepted',
                partnership_type='distributor_manufacturer',
                created_at=datetime.utcnow() - timedelta(days=20)
            ),
            # Other partnerships
            Partnership(
                id=str(uuid.uuid4()),
                requester_id=retailers[0].id,
                partner_id=distributors[0].id,
                status='accepted',
                partnership_type='retailer_distributor',
                created_at=datetime.utcnow() - timedelta(days=30)
            ),
            Partnership(
                id=str(uuid.uuid4()),
                requester_id=retailers[1].id,
                partner_id=distributors[1].id,
                status='accepted',
                partnership_type='retailer_distributor',
                created_at=datetime.utcnow() - timedelta(days=25)
            ),
            Partnership(
                id=str(uuid.uuid4()),
                requester_id=distributors[0].id,
                partner_id=manufacturers[1].id,
                status='accepted',
                partnership_type='distributor_manufacturer',
                created_at=datetime.utcnow() - timedelta(days=15)
            ),
            Partnership(
                id=str(uuid.uuid4()),
                requester_id=distributors[1].id,
                partner_id=manufacturers[2].id,
                status='accepted',
                partnership_type='distributor_manufacturer',
                created_at=datetime.utcnow() - timedelta(days=10)
            )
        ]
        
        for partnership in partnerships:
            db.session.add(partnership)
        db.session.commit()
        
        # Create sample favorites
        click.echo('Creating favorites...')
        favorites = [
            Favorite(
                id=str(uuid.uuid4()),
                user_id=retailers[0].id,
                favorite_user_id=distributors[0].id,
                favorite_type='distributor',
                created_at=datetime.utcnow() - timedelta(days=10)
            ),
            Favorite(
                id=str(uuid.uuid4()),
                user_id=retailers[1].id,
                favorite_user_id=distributors[1].id,
                favorite_type='distributor',
                created_at=datetime.utcnow() - timedelta(days=8)
            ),
            Favorite(
                id=str(uuid.uuid4()),
                user_id=distributors[0].id,
                favorite_user_id=manufacturers[0].id,
                favorite_type='manufacturer',
                created_at=datetime.utcnow() - timedelta(days=12)
            )
        ]
        
        for favorite in favorites:
            db.session.add(favorite)
        db.session.commit()
        
        # Create sample WhatsApp notifications
        click.echo('Creating WhatsApp notifications...')
        notifications = [
            WhatsAppNotification(
                id=str(uuid.uuid4()),
                user_id=retailers[0].id,
                message="🛒 New order from TechMart Electronics\nOrder: ORD-20240806-001\nAmount: ₹95,000\nItems: 2 products\n\nPlease acknowledge:\n1️⃣ Accept\n2️⃣ Reject",
                type='order_alert',
                sent_at=datetime.utcnow() - timedelta(hours=2),
                is_delivered=True
            ),
            WhatsAppNotification(
                id=str(uuid.uuid4()),
                user_id=retailers[0].id,
                message="✅ Order Status Update\nOrder: ORD-20240806-001\nStatus: Confirmed\n\nYour order has been confirmed and is being processed!",
                type='status_update',
                sent_at=datetime.utcnow() - timedelta(hours=1),
                is_delivered=True
            ),
            WhatsAppNotification(
                id=str(uuid.uuid4()),
                user_id=distributors[0].id,
                message="📦 Order Status Update\nOrder: ORD-20240806-001\nStatus: Packed\n\nYour order is packed and ready for dispatch!",
                type='status_update',
                sent_at=datetime.utcnow() - timedelta(minutes=30),
                is_delivered=True
            )
        ]
        
        for notification in notifications:
            db.session.add(notification)
        db.session.commit()
        
        click.echo('Database seeded with comprehensive sample data!')
        click.echo(f'Created:')
        click.echo(f'- {len(categories)} categories')
        click.echo(f'- {len(all_users)} users ({len(retailers)} retailers, {len(distributors)} distributors, {len(manufacturers)} manufacturers)')
        click.echo(f'- {len(products)} products')
        click.echo(f'- {len(orders)} orders')
        click.echo(f'- {len(partnerships)} partnerships')
        click.echo(f'- {len(favorites)} favorites')
        click.echo(f'- {len(notifications)} WhatsApp notifications')
    
    @app.cli.command()
    @with_appcontext
    def create_admin():
        """Create an admin user"""
        email = click.prompt('Admin email')
        password = click.prompt('Admin password', hide_input=True)
        first_name = click.prompt('First name')
        last_name = click.prompt('Last name')
        
        user = User(
            id=uuid.uuid4(),
            email=email,
            first_name=first_name,
            last_name=last_name,
            role='admin',
            is_active=True
        )
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        click.echo(f'Admin user {email} created successfully!')
    
    @app.cli.command()
    @with_appcontext
    def list_users():
        """List all users"""
        users = User.query.all()
        for user in users:
            click.echo(f'{user.email} - {user.role} - {user.full_name}')
    
    @app.cli.command()
    @with_appcontext
    def reset_db():
        """Reset the database"""
        if click.confirm('Are you sure you want to drop all tables?'):
            db.drop_all()
            db.create_all()
            click.echo('Database reset!') 