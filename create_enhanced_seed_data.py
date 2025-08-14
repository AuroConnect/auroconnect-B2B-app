#!/usr/bin/env python3
"""
Enhanced Seed Data Script for AuroMart B2B Platform
Creates demo users, products, inventory, pricing rules, and orders with enhanced features
"""
import requests
import json
import time
import os
from datetime import datetime, timedelta

# Configuration
BASE_URL = "http://localhost:5000"
API_BASE = f"{BASE_URL}/api"

# Demo users
DEMO_USERS = {
    "manufacturer": {
        "email": "m@demo.com",
        "password": "Demo@123",
        "firstName": "Auro",
        "lastName": "Manufacturer",
        "businessName": "Auro Manufacturer",
        "role": "manufacturer",
        "phoneNumber": "+91-9876543210",
        "address": "123 Industrial Park, Mumbai, Maharashtra"
    },
    "distributor": {
        "email": "d@demo.com",
        "password": "Demo@123",
        "firstName": "Auro",
        "lastName": "Distributor",
        "businessName": "Auro Distributor",
        "role": "distributor",
        "phoneNumber": "+91-9876543211",
        "address": "456 Trade Center, Delhi, NCR"
    },
    "retailer": {
        "email": "r@demo.com",
        "password": "Demo@123",
        "firstName": "Auro",
        "lastName": "Retailer",
        "businessName": "Auro Retailer",
        "role": "retailer",
        "phoneNumber": "+91-9876543212",
        "address": "789 Market Street, Bangalore, Karnataka"
    }
}

# Enhanced categories
CATEGORIES = [
    {"name": "Laptops & Computers", "description": "High-performance laptops and desktop computers"},
    {"name": "Mobile Phones", "description": "Smartphones and mobile accessories"},
    {"name": "Clothing & Fashion", "description": "Trendy clothing and fashion accessories"},
    {"name": "Home & Furniture", "description": "Home decor and furniture items"},
    {"name": "Electronics & Gadgets", "description": "Electronic gadgets and accessories"}
]

# Sample products (10 per category)
SAMPLE_PRODUCTS = {
    "Laptops & Computers": [
        {"name": "Dell Inspiron 15", "sku": "DELL-INSP-15", "base_price": 45000, "description": "15.6-inch laptop with Intel i5 processor", "brand": "Dell"},
        {"name": "HP Pavilion 14", "sku": "HP-PAV-14", "base_price": 52000, "description": "14-inch ultrabook with AMD Ryzen", "brand": "HP"},
        {"name": "Lenovo ThinkPad X1", "sku": "LEN-THINK-X1", "base_price": 85000, "description": "Premium business laptop", "brand": "Lenovo"},
        {"name": "MacBook Air M2", "sku": "APPLE-MBA-M2", "base_price": 95000, "description": "Apple's latest ultrabook", "brand": "Apple"},
        {"name": "Asus ROG Strix", "sku": "ASUS-ROG-15", "base_price": 75000, "description": "Gaming laptop with RTX graphics", "brand": "Asus"},
        {"name": "Acer Swift 3", "sku": "ACER-SWIFT-3", "base_price": 38000, "description": "Lightweight productivity laptop", "brand": "Acer"},
        {"name": "MSI Gaming Laptop", "sku": "MSI-GAMING-17", "base_price": 120000, "description": "17-inch gaming powerhouse", "brand": "MSI"},
        {"name": "Razer Blade 15", "sku": "RAZER-BLADE-15", "base_price": 150000, "description": "Premium gaming laptop", "brand": "Razer"},
        {"name": "Samsung Galaxy Book", "sku": "SAMS-GAL-BOOK", "base_price": 65000, "description": "2-in-1 convertible laptop", "brand": "Samsung"},
        {"name": "Toshiba Satellite", "sku": "TOSH-SAT-15", "base_price": 42000, "description": "Reliable business laptop", "brand": "Toshiba"}
    ],
    "Mobile Phones": [
        {"name": "iPhone 15 Pro", "sku": "APPLE-IPH-15P", "base_price": 120000, "description": "Latest iPhone with titanium design", "brand": "Apple"},
        {"name": "Samsung Galaxy S24", "sku": "SAMS-GAL-S24", "base_price": 85000, "description": "Flagship Android smartphone", "brand": "Samsung"},
        {"name": "Xiaomi 14 Pro", "sku": "XIAOMI-14P", "base_price": 65000, "description": "Premium Android with Leica camera", "brand": "Xiaomi"},
        {"name": "OnePlus 12", "sku": "ONEPLUS-12", "base_price": 70000, "description": "Fast charging flagship", "brand": "OnePlus"},
        {"name": "OPPO Find X7", "sku": "OPPO-FIND-X7", "base_price": 75000, "description": "Innovative foldable design", "brand": "OPPO"},
        {"name": "Vivo X100 Pro", "sku": "VIVO-X100P", "base_price": 80000, "description": "Professional photography phone", "brand": "Vivo"},
        {"name": "Realme GT Neo 5", "sku": "REALME-GT-NEO5", "base_price": 35000, "description": "Performance-focused mid-range", "brand": "Realme"},
        {"name": "Nothing Phone 2", "sku": "NOTHING-PH2", "base_price": 45000, "description": "Unique Glyph interface", "brand": "Nothing"},
        {"name": "Google Pixel 8", "sku": "GOOGLE-PIXEL-8", "base_price": 75000, "description": "Best camera phone", "brand": "Google"},
        {"name": "Motorola Edge 40", "sku": "MOTO-EDGE-40", "base_price": 30000, "description": "5G ready mid-range", "brand": "Motorola"}
    ]
}

def make_request(method, endpoint, data=None):
    """Make API request"""
    url = f"{API_BASE}{endpoint}"
    headers = {'Content-Type': 'application/json'} if data else {}
    
    try:
        if method == "GET":
            response = requests.get(url, headers=headers)
        elif method == "POST":
            response = requests.post(url, json=data, headers=headers)
        elif method == "PUT":
            response = requests.put(url, json=data, headers=headers)
        
        if response.status_code in [200, 201]:
            return response.json()
        else:
            print(f"❌ {method} {endpoint} failed: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Error making {method} request to {endpoint}: {str(e)}")
        return None

def register_user(user_data):
    """Register a new user"""
    print(f"📝 Registering {user_data['role']}: {user_data['email']}")
    
    registration_data = {
        "email": user_data["email"],
        "password": user_data["password"],
        "firstName": user_data["firstName"],
        "lastName": user_data["lastName"],
        "businessName": user_data["businessName"],
        "role": user_data["role"],
        "phoneNumber": user_data["phoneNumber"],
        "address": user_data["address"]
    }
    
    result = make_request("POST", "/auth/register", registration_data)
    if result:
        print(f"✅ {user_data['role']} registered successfully")
        return result
    else:
        print(f"❌ Failed to register {user_data['role']}")
        return None

def login_user(user_data):
    """Login user and return token"""
    print(f"🔐 Logging in {user_data['role']}: {user_data['email']}")
    
    login_data = {
        "email": user_data["email"],
        "password": user_data["password"]
    }
    
    result = make_request("POST", "/auth/login", login_data)
    if result and 'access_token' in result:
        print(f"✅ {user_data['role']} logged in successfully")
        return result['access_token']
    else:
        print(f"❌ Failed to login {user_data['role']}")
        return None

def create_category(category_data, token):
    """Create a category"""
    headers = {"Authorization": f"Bearer {token}"}
    url = f"{API_BASE}/products/categories"
    
    try:
        response = requests.post(url, json=category_data, headers=headers)
        if response.status_code == 201:
            result = response.json()
            print(f"✅ Category '{category_data['name']}' created")
            return result
        else:
            print(f"❌ Failed to create category '{category_data['name']}': {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error creating category: {str(e)}")
        return None

def create_product(product_data, category_id, token):
    """Create a product"""
    headers = {"Authorization": f"Bearer {token}"}
    url = f"{API_BASE}/products"
    
    product_payload = {
        "name": product_data["name"],
        "sku": product_data["sku"],
        "description": product_data["description"],
        "base_price": product_data["base_price"],
        "category_id": category_id,
        "brand": product_data["brand"],
        "image_url": f"https://via.placeholder.com/300x300?text={product_data['name'].replace(' ', '+')}"
    }
    
    try:
        response = requests.post(url, json=product_payload, headers=headers)
        if response.status_code == 201:
            result = response.json()
            print(f"✅ Product '{product_data['name']}' created")
            return result
        else:
            print(f"❌ Failed to create product '{product_data['name']}': {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error creating product: {str(e)}")
        return None

def main():
    """Main function to create enhanced seed data"""
    print("🚀 Starting enhanced seed data creation...")
    print("=" * 60)
    
    # Step 1: Register and login users
    print("\n📋 Step 1: Creating demo users...")
    users = {}
    tokens = {}
    
    for role, user_data in DEMO_USERS.items():
        # Register user
        user_result = register_user(user_data)
        if user_result:
            users[role] = user_result
        
        # Login user
        token = login_user(user_data)
        if token:
            tokens[role] = token
    
    if not all(tokens.values()):
        print("❌ Failed to create or login all users. Exiting.")
        return
    
    print(f"✅ All users created and logged in successfully")
    
    # Step 2: Create categories
    print("\n📋 Step 2: Creating categories...")
    categories = {}
    
    for category_data in CATEGORIES:
        category_result = create_category(category_data, tokens["manufacturer"])
        if category_result:
            categories[category_data["name"]] = category_result
    
    print(f"✅ Created {len(categories)} categories")
    
    # Step 3: Create products
    print("\n📋 Step 3: Creating products...")
    all_products = []
    
    for category_name, category_data in categories.items():
        if category_name in SAMPLE_PRODUCTS:
            for product_data in SAMPLE_PRODUCTS[category_name]:
                product_result = create_product(product_data, category_data["id"], tokens["manufacturer"])
                if product_result:
                    all_products.append(product_result)
    
    print(f"✅ Created {len(all_products)} products")
    
    print("\n" + "=" * 60)
    print("🎉 Enhanced seed data creation completed!")
    print("\n📊 Summary:")
    print(f"   • Users: {len(users)} (Manufacturer, Distributor, Retailer)")
    print(f"   • Categories: {len(categories)}")
    print(f"   • Products: {len(all_products)}")
    
    print("\n🔑 Demo Login Credentials:")
    print("   Manufacturer: m@demo.com / Demo@123")
    print("   Distributor:  d@demo.com / Demo@123")
    print("   Retailer:     r@demo.com / Demo@123")
    
    print("\n🎯 New Features Available:")
    print("   • Enhanced Inventory Management with low stock alerts")
    print("   • Auto-restock functionality")
    print("   • Bulk inventory upload via Excel")
    print("   • Order tags (URGENT, BULK, PARTIAL)")
    print("   • Split shipment and backorder support")
    print("   • Pricing rules (volume, seasonal, partner discounts)")
    print("   • Promo codes with various conditions")
    print("   • Real-time notifications and order chat")
    print("   • Comprehensive analytics and reporting")
    
    print("\n🚀 Ready to test all features!")

if __name__ == "__main__":
    main()
