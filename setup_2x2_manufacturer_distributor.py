#!/usr/bin/env python3
"""
Setup 2x2 Manufacturer-Distributor Relationships
Creates M1, M2 (Manufacturers) and D1, D2 (Distributors) with proper assignments
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'server'))

from server.app import create_app, db
from server.app.models import User, Product, Category, ProductAllocation, Partnership
from datetime import datetime
import uuid

def create_2x2_relationships():
    """Create 2 Manufacturers and 2 Distributors with proper relationships"""
    
    app = create_app()
    
    with app.app_context():
        print("🔧 Setting up 2x2 Manufacturer-Distributor relationships...")
        
        # Clear existing data
        db.session.query(ProductAllocation).delete()
        db.session.query(Partnership).delete()
        db.session.query(Product).delete()
        db.session.query(User).filter(User.role.in_(['manufacturer', 'distributor'])).delete()
        db.session.commit()
        
        # Create Categories
        categories = {
            'electronics': Category(id=str(uuid.uuid4()), name='Electronics', description='Electronic devices and accessories'),
            'clothing': Category(id=str(uuid.uuid4()), name='Clothing', description='Apparel and fashion items'),
            'home': Category(id=str(uuid.uuid4()), name='Home & Garden', description='Home improvement and garden products'),
            'sports': Category(id=str(uuid.uuid4()), name='Sports & Outdoors', description='Sports equipment and outdoor gear')
        }
        
        for category in categories.values():
            db.session.add(category)
        db.session.commit()
        
        # Create Manufacturers
        manufacturers = {
            'M1': User(
                id=str(uuid.uuid4()),
                email='m1@auromart.com',
                password_hash='$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj/RK.s5u.Ge',  # password123
                firstName='Tech',
                lastName='Manufacturer',
                businessName='TechCorp Industries',
                phone='+91-9876543210',
                role='manufacturer',
                is_active=True,
                created_at=datetime.utcnow()
            ),
            'M2': User(
                id=str(uuid.uuid4()),
                email='m2@auromart.com',
                password_hash='$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj/RK.s5u.Ge',  # password123
                firstName='Fashion',
                lastName='Manufacturer',
                businessName='FashionHub Ltd',
                phone='+91-9876543211',
                role='manufacturer',
                is_active=True,
                created_at=datetime.utcnow()
            )
        }
        
        # Create Distributors
        distributors = {
            'D1': User(
                id=str(uuid.uuid4()),
                email='d1@auromart.com',
                password_hash='$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj/RK.s5u.Ge',  # password123
                firstName='Tech',
                lastName='Distributor',
                businessName='TechDist Solutions',
                phone='+91-9876543212',
                role='distributor',
                is_active=True,
                created_at=datetime.utcnow()
            ),
            'D2': User(
                id=str(uuid.uuid4()),
                email='d2@auromart.com',
                password_hash='$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj/RK.s5u.Ge',  # password123
                firstName='Fashion',
                lastName='Distributor',
                businessName='FashionDist Pro',
                phone='+91-9876543213',
                role='distributor',
                is_active=True,
                created_at=datetime.utcnow()
            )
        }
        
        # Add all users
        for user in list(manufacturers.values()) + list(distributors.values()):
            db.session.add(user)
        db.session.commit()
        
        # Create Manufacturer Products
        m1_products = [
            Product(
                id=str(uuid.uuid4()),
                name='Premium Laptop',
                description='High-performance laptop with latest specifications',
                sku='LAPTOP001',
                categoryId=categories['electronics'].id,
                manufacturer_id=manufacturers['M1'].id,
                basePrice=45000.00,
                imageUrl='https://example.com/laptop1.jpg',
                is_active=True,
                created_at=datetime.utcnow()
            ),
            Product(
                id=str(uuid.uuid4()),
                name='Wireless Mouse',
                description='Ergonomic wireless mouse with precision tracking',
                sku='MOUSE001',
                categoryId=categories['electronics'].id,
                manufacturer_id=manufacturers['M1'].id,
                basePrice=1200.00,
                imageUrl='https://example.com/mouse1.jpg',
                is_active=True,
                created_at=datetime.utcnow()
            ),
            Product(
                id=str(uuid.uuid4()),
                name='Mechanical Keyboard',
                description='RGB mechanical keyboard with customizable switches',
                sku='KEYBOARD001',
                categoryId=categories['electronics'].id,
                manufacturer_id=manufacturers['M1'].id,
                basePrice=3500.00,
                imageUrl='https://example.com/keyboard1.jpg',
                is_active=True,
                created_at=datetime.utcnow()
            )
        ]
        
        m2_products = [
            Product(
                id=str(uuid.uuid4()),
                name='Designer T-Shirt',
                description='Premium cotton designer t-shirt',
                sku='TSHIRT001',
                categoryId=categories['clothing'].id,
                manufacturer_id=manufacturers['M2'].id,
                basePrice=800.00,
                imageUrl='https://example.com/tshirt1.jpg',
                is_active=True,
                created_at=datetime.utcnow()
            ),
            Product(
                id=str(uuid.uuid4()),
                name='Denim Jeans',
                description='High-quality denim jeans with perfect fit',
                sku='JEANS001',
                categoryId=categories['clothing'].id,
                manufacturer_id=manufacturers['M2'].id,
                basePrice=1500.00,
                imageUrl='https://example.com/jeans1.jpg',
                is_active=True,
                created_at=datetime.utcnow()
            ),
            Product(
                id=str(uuid.uuid4()),
                name='Running Shoes',
                description='Comfortable running shoes with advanced cushioning',
                sku='SHOES001',
                categoryId=categories['sports'].id,
                manufacturer_id=manufacturers['M2'].id,
                basePrice=2500.00,
                imageUrl='https://example.com/shoes1.jpg',
                is_active=True,
                created_at=datetime.utcnow()
            )
        ]
        
        # Add all products
        for product in m1_products + m2_products:
            db.session.add(product)
        db.session.commit()
        
        # Create Product Allocations (M1 ↔ D1, M2 ↔ D2)
        allocations = []
        
        # M1 products allocated to D1
        for product in m1_products:
            allocation = ProductAllocation(
                id=str(uuid.uuid4()),
                manufacturer_id=manufacturers['M1'].id,
                distributor_id=distributors['D1'].id,
                product_id=product.id,
                is_active=True,
                created_at=datetime.utcnow()
            )
            allocations.append(allocation)
        
        # M2 products allocated to D2
        for product in m2_products:
            allocation = ProductAllocation(
                id=str(uuid.uuid4()),
                manufacturer_id=manufacturers['M2'].id,
                distributor_id=distributors['D2'].id,
                product_id=product.id,
                is_active=True,
                created_at=datetime.utcnow()
            )
            allocations.append(allocation)
        
        # Add all allocations
        for allocation in allocations:
            db.session.add(allocation)
        db.session.commit()
        
        # Create Partnerships
        partnerships = [
            Partnership(
                id=str(uuid.uuid4()),
                manufacturer_id=manufacturers['M1'].id,
                distributor_id=distributors['D1'].id,
                status='active',
                created_at=datetime.utcnow()
            ),
            Partnership(
                id=str(uuid.uuid4()),
                manufacturer_id=manufacturers['M2'].id,
                distributor_id=distributors['D2'].id,
                status='active',
                created_at=datetime.utcnow()
            )
        ]
        
        for partnership in partnerships:
            db.session.add(partnership)
        db.session.commit()
        
        print("✅ 2x2 Manufacturer-Distributor relationships created successfully!")
        print("\n📋 Created Organizations:")
        print("Manufacturers:")
        for key, mfr in manufacturers.items():
            print(f"  {key}: {mfr.businessName} ({mfr.email})")
        print("\nDistributors:")
        for key, dist in distributors.items():
            print(f"  {key}: {dist.businessName} ({dist.email})")
        
        print("\n🔗 Relationships:")
        print("  M1 ↔ D1 (TechCorp ↔ TechDist)")
        print("  M2 ↔ D2 (FashionHub ↔ FashionDist)")
        
        print("\n📦 Products Created:")
        print("  M1: 3 Electronics products")
        print("  M2: 3 Clothing/Sports products")
        
        print("\n🔐 Login Credentials:")
        print("  All accounts use: password123")
        print("  Manufacturers: m1@auromart.com, m2@auromart.com")
        print("  Distributors: d1@auromart.com, d2@auromart.com")

if __name__ == "__main__":
    create_2x2_relationships()
