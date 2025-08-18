#!/usr/bin/env python3
"""
Initialize comprehensive business categories for AuroMart B2B platform
"""

import os
import sys
from pathlib import Path

# Add the server directory to Python path
server_dir = Path(__file__).parent
sys.path.insert(0, str(server_dir))

from app import create_app, db
from app.models.category import Category

def init_categories():
    """Initialize comprehensive business categories"""
    app = create_app()
    
    with app.app_context():
        # Check if categories already exist
        if Category.query.first():
            print("⚠️  Categories already exist. Skipping initialization.")
            return
        
        print("🌱 Initializing comprehensive business categories...")
        
        # Comprehensive business categories
        categories = [
            # Electronics & Technology
            Category(name="Electronics", description="Electronic devices and accessories"),
            Category(name="Computers & Laptops", description="Desktop computers, laptops, and accessories"),
            Category(name="Mobile Phones", description="Smartphones, feature phones, and accessories"),
            Category(name="Audio & Video", description="Speakers, headphones, cameras, and video equipment"),
            Category(name="Gaming", description="Gaming consoles, accessories, and gaming equipment"),
            
            # Fashion & Apparel
            Category(name="Clothing", description="Fashion and apparel for all ages"),
            Category(name="Footwear", description="Shoes, boots, sandals, and footwear accessories"),
            Category(name="Accessories", description="Jewelry, watches, bags, and fashion accessories"),
            Category(name="Sports Wear", description="Athletic clothing and sports equipment"),
            
            # Home & Living
            Category(name="Home & Garden", description="Home improvement and garden supplies"),
            Category(name="Furniture", description="Home and office furniture"),
            Category(name="Kitchen & Dining", description="Kitchen appliances and dining accessories"),
            Category(name="Bedding & Bath", description="Bedding, towels, and bathroom accessories"),
            Category(name="Home Decor", description="Decorative items and home accessories"),
            
            # Health & Beauty
            Category(name="Health & Wellness", description="Health supplements and wellness products"),
            Category(name="Beauty & Personal Care", description="Cosmetics, skincare, and personal care"),
            Category(name="Medical Supplies", description="Medical equipment and healthcare supplies"),
            
            # Automotive
            Category(name="Automotive", description="Car parts, accessories, and automotive supplies"),
            Category(name="Motorcycles", description="Motorcycle parts and accessories"),
            
            # Industrial & Construction
            Category(name="Industrial Equipment", description="Heavy machinery and industrial tools"),
            Category(name="Construction Materials", description="Building materials and construction supplies"),
            Category(name="Tools & Hardware", description="Hand tools, power tools, and hardware"),
            
            # Food & Beverage
            Category(name="Food & Beverages", description="Food products and beverages"),
            Category(name="Restaurant Supplies", description="Commercial kitchen equipment and supplies"),
            
            # Office & Business
            Category(name="Office Supplies", description="Office equipment and stationery"),
            Category(name="Business Equipment", description="Commercial and business equipment"),
            
            # Agriculture
            Category(name="Agriculture", description="Farming equipment and agricultural supplies"),
            Category(name="Livestock", description="Animal feed and livestock supplies"),
            
            # Textiles & Fabrics
            Category(name="Textiles & Fabrics", description="Raw materials for clothing and upholstery"),
            Category(name="Yarn & Thread", description="Yarn, thread, and sewing supplies"),
            
            # Chemicals & Materials
            Category(name="Chemicals", description="Industrial chemicals and raw materials"),
            Category(name="Plastics & Polymers", description="Plastic materials and polymer products"),
            Category(name="Metals & Alloys", description="Metal products and alloy materials"),
            
            # Energy & Utilities
            Category(name="Energy Equipment", description="Solar panels, generators, and energy equipment"),
            Category(name="Electrical Supplies", description="Electrical components and wiring"),
            
            # Transportation & Logistics
            Category(name="Logistics Equipment", description="Warehouse and logistics equipment"),
            Category(name="Packaging Materials", description="Packaging supplies and materials"),
            
            # Books & Education
            Category(name="Books & Publications", description="Educational books and publications"),
            Category(name="Educational Supplies", description="School and educational equipment"),
            
            # Sports & Recreation
            Category(name="Sports Equipment", description="Sports gear and recreational equipment"),
            Category(name="Outdoor & Camping", description="Outdoor gear and camping equipment"),
            
            # Pet Supplies
            Category(name="Pet Supplies", description="Pet food, toys, and accessories"),
            
            # Baby & Kids
            Category(name="Baby & Kids", description="Baby products and children's items"),
            
            # Miscellaneous
            Category(name="Miscellaneous", description="Other products and supplies"),
        ]
        
        # Add categories to database
        for category in categories:
            db.session.add(category)
        
        db.session.commit()
        print(f"✅ Successfully created {len(categories)} business categories!")
        
        # Display categories
        print("\n📋 Created Categories:")
        for i, category in enumerate(categories, 1):
            print(f"   {i:2d}. {category.name}")
        
        print(f"\n🎉 Total categories: {len(categories)}")

if __name__ == "__main__":
    init_categories()
