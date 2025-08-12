#!/usr/bin/env python3
"""
Comprehensive Seed Data Generator for AuroMart B2B Platform
Creates demo users, categories, products, orders, and invoices for testing
"""

import requests
import json
import time
from datetime import datetime, timedelta
import random

# Configuration
BASE_URL = "http://localhost:5000"
API_BASE = f"{BASE_URL}/api"

# Demo user credentials
DEMO_USERS = [
    {
        "email": "m@demo.com",
        "password": "Demo@123",
        "business_name": "Auro Manufacturer",
        "role": "manufacturer",
        "phone": "+91-9876543210",
        "address": "123 Industrial Park, Mumbai, Maharashtra"
    },
    {
        "email": "d@demo.com", 
        "password": "Demo@123",
        "business_name": "Auro Distributor",
        "role": "distributor",
        "phone": "+91-9876543211",
        "address": "456 Trade Center, Delhi, NCR"
    },
    {
        "email": "r@demo.com",
        "password": "Demo@123", 
        "business_name": "Auro Retailer",
        "role": "retailer",
        "phone": "+91-9876543212",
        "address": "789 Market Street, Bangalore, Karnataka"
    }
]

# Categories and Brands
CATEGORIES = [
    {
        "name": "Laptop",
        "description": "High-performance laptops for business and personal use",
        "brands": ["HP", "Dell", "Lenovo", "ASUS", "Acer", "Apple"]
    },
    {
        "name": "Clothing",
        "description": "Fashion apparel for all ages and occasions",
        "brands": ["Levis", "Allen Solly", "Van Heusen", "Raymond", "Peter England", "Arrow"]
    },
    {
        "name": "Mattress",
        "description": "Comfortable mattresses for better sleep",
        "brands": ["Kurl-On", "Sleepwell", "Relaxwell", "Springfit", "Duroflex", "Peps"]
    },
    {
        "name": "Mobile",
        "description": "Smartphones and mobile accessories",
        "brands": ["Samsung", "Apple", "Xiaomi", "OnePlus", "Vivo", "Oppo"]
    },
    {
        "name": "Electronics",
        "description": "Home and office electronics",
        "brands": ["LG", "Sony", "Panasonic", "Philips", "Bajaj", "Havells"]
    },
    {
        "name": "Furniture",
        "description": "Modern furniture for home and office",
        "brands": ["Godrej", "IKEA", "Durian", "Nilkamal", "Prestige", "Stanley"]
    },
    {
        "name": "Kitchen Appliances",
        "description": "Kitchen and cooking appliances",
        "brands": ["Prestige", "Bajaj", "Philips", "Morphy Richards", "Butterfly", "Usha"]
    },
    {
        "name": "Sports Equipment",
        "description": "Sports and fitness equipment",
        "brands": ["Nike", "Adidas", "Puma", "Reebok", "Decathlon", "Yonex"]
    }
]

# Sample product data
SAMPLE_PRODUCTS = {
    "Laptop": [
        {"name": "HP Pavilion 15", "sku": "LAP-HP-PAV-15", "base_price": 45000, "stock": 25},
        {"name": "Dell Inspiron 14", "sku": "LAP-DELL-INS-14", "base_price": 52000, "stock": 20},
        {"name": "Lenovo ThinkPad E15", "sku": "LAP-LEN-THINK-E15", "base_price": 48000, "stock": 30},
        {"name": "ASUS VivoBook 15", "sku": "LAP-ASUS-VIVO-15", "base_price": 38000, "stock": 15},
        {"name": "Acer Aspire 5", "sku": "LAP-ACER-ASP-5", "base_price": 42000, "stock": 18},
        {"name": "MacBook Air M1", "sku": "LAP-APPLE-MBA-M1", "base_price": 85000, "stock": 10}
    ],
    "Clothing": [
        {"name": "Levis 501 Jeans", "sku": "CLO-LEVIS-501", "base_price": 2500, "stock": 100},
        {"name": "Allen Solly Shirt", "sku": "CLO-AS-SHIRT", "base_price": 1800, "stock": 80},
        {"name": "Van Heusen Formal", "sku": "CLO-VH-FORMAL", "base_price": 2200, "stock": 60},
        {"name": "Raymond Suit", "sku": "CLO-RAY-SUIT", "base_price": 12000, "stock": 25},
        {"name": "Peter England Casual", "sku": "CLO-PE-CASUAL", "base_price": 1500, "stock": 90},
        {"name": "Arrow T-Shirt", "sku": "CLO-ARROW-TSHIRT", "base_price": 800, "stock": 120}
    ],
    "Mattress": [
        {"name": "Kurl-On Ortho", "sku": "MAT-KURL-ORTHO", "base_price": 15000, "stock": 40},
        {"name": "Sleepwell Comfort", "sku": "MAT-SLEEP-COM", "base_price": 12000, "stock": 35},
        {"name": "Relaxwell Memory", "sku": "MAT-RELAX-MEM", "base_price": 18000, "stock": 30},
        {"name": "Springfit Coir", "sku": "MAT-SPRING-COIR", "base_price": 8000, "stock": 50},
        {"name": "Duroflex Latex", "sku": "MAT-DURO-LATEX", "base_price": 22000, "stock": 20},
        {"name": "Peps Spring", "sku": "MAT-PEPS-SPRING", "base_price": 10000, "stock": 45}
    ],
    "Mobile": [
        {"name": "Samsung Galaxy S21", "sku": "MOB-SAM-S21", "base_price": 65000, "stock": 30},
        {"name": "iPhone 13", "sku": "MOB-APPLE-13", "base_price": 75000, "stock": 25},
        {"name": "Xiaomi Mi 11", "sku": "MOB-XIAOMI-MI11", "base_price": 45000, "stock": 40},
        {"name": "OnePlus 9", "sku": "MOB-OP-9", "base_price": 55000, "stock": 35},
        {"name": "Vivo V21", "sku": "MOB-VIVO-V21", "base_price": 35000, "stock": 50},
        {"name": "Oppo Reno 6", "sku": "MOB-OPPO-RENO6", "base_price": 32000, "stock": 45}
    ],
    "Electronics": [
        {"name": "LG Smart TV 55", "sku": "ELE-LG-TV55", "base_price": 45000, "stock": 20},
        {"name": "Sony Soundbar", "sku": "ELE-SONY-SOUND", "base_price": 25000, "stock": 15},
        {"name": "Panasonic AC", "sku": "ELE-PANA-AC", "base_price": 35000, "stock": 25},
        {"name": "Philips LED Bulb", "sku": "ELE-PHIL-LED", "base_price": 200, "stock": 500},
        {"name": "Bajaj Mixer", "sku": "ELE-BAJAJ-MIX", "base_price": 2500, "stock": 80},
        {"name": "Havells Fan", "sku": "ELE-HAVELLS-FAN", "base_price": 1800, "stock": 100}
    ],
    "Furniture": [
        {"name": "Godrej Office Chair", "sku": "FUR-GOD-CHAIR", "base_price": 8000, "stock": 30},
        {"name": "IKEA Study Table", "sku": "FUR-IKEA-TABLE", "base_price": 12000, "stock": 25},
        {"name": "Durian Sofa Set", "sku": "FUR-DUR-SOFA", "base_price": 45000, "stock": 15},
        {"name": "Nilkamal Plastic Chair", "sku": "FUR-NIL-PLASTIC", "base_price": 800, "stock": 200},
        {"name": "Prestige Dining Table", "sku": "FUR-PRE-DINING", "base_price": 25000, "stock": 20},
        {"name": "Stanley Wardrobe", "sku": "FUR-STA-WARD", "base_price": 18000, "stock": 25}
    ],
    "Kitchen Appliances": [
        {"name": "Prestige Pressure Cooker", "sku": "KIT-PRE-PRESSURE", "base_price": 1200, "stock": 150},
        {"name": "Bajaj Toaster", "sku": "KIT-BAJ-TOAST", "base_price": 800, "stock": 100},
        {"name": "Philips Food Processor", "sku": "KIT-PHI-FOOD", "base_price": 3500, "stock": 60},
        {"name": "Morphy Richards Coffee Maker", "sku": "KIT-MOR-COFFEE", "base_price": 2800, "stock": 40},
        {"name": "Butterfly Mixer Grinder", "sku": "KIT-BUT-MIXER", "base_price": 1800, "stock": 80},
        {"name": "Usha Iron", "sku": "KIT-USHA-IRON", "base_price": 1200, "stock": 120}
    ],
    "Sports Equipment": [
        {"name": "Nike Running Shoes", "sku": "SPO-NIKE-RUN", "base_price": 4500, "stock": 80},
        {"name": "Adidas Football", "sku": "SPO-ADI-FOOT", "base_price": 1200, "stock": 100},
        {"name": "Puma Tracksuit", "sku": "SPO-PUMA-TRACK", "base_price": 2800, "stock": 60},
        {"name": "Reebok Dumbbells", "sku": "SPO-REE-DUMB", "base_price": 800, "stock": 150},
        {"name": "Decathlon Badminton Set", "sku": "SPO-DEC-BAD", "base_price": 1500, "stock": 70},
        {"name": "Yonex Tennis Racket", "sku": "SPO-YON-TENNIS", "base_price": 3500, "stock": 40}
    ]
}

def make_request(method, endpoint, data=None, token=None):
    """Make HTTP request to API"""
    url = f"{API_BASE}{endpoint}"
    headers = {"Content-Type": "application/json"}
    
    if token:
        headers["Authorization"] = f"Bearer {token}"
    
    try:
        if method == "GET":
            response = requests.get(url, headers=headers)
        elif method == "POST":
            response = requests.post(url, headers=headers, json=data)
        elif method == "PUT":
            response = requests.put(url, headers=headers, json=data)
        
        if response.status_code in [200, 201]:
            return response.json()
        else:
            print(f"❌ {method} {endpoint}: {response.status_code} - {response.text}")
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
        "business_name": user_data["business_name"],
        "role": user_data["role"],
        "phone": user_data["phone"],
        "address": user_data["address"]
    }
    
    result = make_request("POST", "/auth/register", registration_data)
    if result:
        print(f"✅ {user_data['role']} registered successfully")
        return result.get("user", {}).get("id")
    else:
        print(f"❌ Failed to register {user_data['role']}")
        return None

def login_user(email, password):
    """Login user and get token"""
    print(f"🔐 Logging in: {email}")
    
    login_data = {"email": email, "password": password}
    result = make_request("POST", "/auth/login", login_data)
    
    if result and "access_token" in result:
        print(f"✅ Login successful for {email}")
        return result["access_token"]
    else:
        print(f"❌ Login failed for {email}")
        return None

def create_category(category_data, token):
    """Create a category"""
    print(f"📂 Creating category: {category_data['name']}")
    
    result = make_request("POST", "/products/categories", category_data, token)
    if result:
        print(f"✅ Category '{category_data['name']}' created")
        return result.get("id")
    else:
        print(f"❌ Failed to create category '{category_data['name']}'")
        return None

def create_product(product_data, token):
    """Create a product"""
    print(f"📦 Creating product: {product_data['name']}")
    
    result = make_request("POST", "/products", product_data, token)
    if result:
        print(f"✅ Product '{product_data['name']}' created")
        return result.get("id")
    else:
        print(f"❌ Failed to create product '{product_data['name']}'")
        return None

def create_order(order_data, token):
    """Create an order"""
    print(f"📋 Creating order for {order_data['buyer_id']}")
    
    result = make_request("POST", "/orders", order_data, token)
    if result:
        print(f"✅ Order created successfully")
        return result.get("orders", [{}])[0].get("id")
    else:
        print(f"❌ Failed to create order")
        return None

def update_order_status(order_id, status_data, token):
    """Update order status"""
    print(f"🔄 Updating order {order_id} status to {status_data['status']}")
    
    result = make_request("PUT", f"/orders/{order_id}/status", status_data, token)
    if result:
        print(f"✅ Order status updated successfully")
        return True
    else:
        print(f"❌ Failed to update order status")
        return False

def generate_invoice(order_id, token):
    """Generate invoice for order"""
    print(f"🧾 Generating invoice for order {order_id}")
    
    result = make_request("POST", f"/invoices/generate/{order_id}", {}, token)
    if result:
        print(f"✅ Invoice generated successfully")
        return True
    else:
        print(f"❌ Failed to generate invoice")
        return False

def main():
    """Main function to create comprehensive seed data"""
    print("🚀 Starting Comprehensive Seed Data Generation")
    print("=" * 60)
    
    # Step 1: Register demo users
    print("\n📝 STEP 1: Registering Demo Users")
    print("-" * 40)
    
    user_ids = {}
    user_tokens = {}
    
    for user_data in DEMO_USERS:
        user_id = register_user(user_data)
        if user_id:
            user_ids[user_data["role"]] = user_id
            # Login to get token
            token = login_user(user_data["email"], user_data["password"])
            if token:
                user_tokens[user_data["role"]] = token
    
    if not user_ids:
        print("❌ No users created. Exiting.")
        return
    
    # Step 2: Create categories
    print("\n📂 STEP 2: Creating Categories")
    print("-" * 40)
    
    manufacturer_token = user_tokens.get("manufacturer")
    if not manufacturer_token:
        print("❌ No manufacturer token. Skipping categories.")
        return
    
    category_ids = {}
    for category_data in CATEGORIES:
        category_id = create_category({
            "name": category_data["name"],
            "description": category_data["description"]
        }, manufacturer_token)
        if category_id:
            category_ids[category_data["name"]] = category_id
    
    # Step 3: Create products
    print("\n📦 STEP 3: Creating Products")
    print("-" * 40)
    
    product_ids = []
    for category_name, products in SAMPLE_PRODUCTS.items():
        if category_name not in category_ids:
            continue
            
        for product_data in products:
            product_info = {
                "name": product_data["name"],
                "description": f"High-quality {product_data['name']} for your needs",
                "sku": product_data["sku"],
                "category_id": category_ids[category_name],
                "base_price": product_data["base_price"],
                "stock_quantity": product_data["stock"],
                "brand": random.choice(CATEGORIES[0]["brands"]),  # Random brand
                "unit": "pcs",
                "image_url": f"https://example.com/images/{product_data['sku'].lower()}.jpg"
            }
            
            product_id = create_product(product_info, manufacturer_token)
            if product_id:
                product_ids.append(product_id)
    
    print(f"✅ Created {len(product_ids)} products")
    
    # Step 4: Create demo orders
    print("\n📋 STEP 4: Creating Demo Orders")
    print("-" * 40)
    
    # Get some products for orders
    if len(product_ids) < 3:
        print("❌ Not enough products for orders. Skipping.")
        return
    
    # Create orders from distributor to manufacturer
    distributor_token = user_tokens.get("distributor")
    if distributor_token and product_ids:
        for i in range(3):  # Create 3 orders
            order_data = {
                "cart_items": [
                    {
                        "product_id": product_ids[i % len(product_ids)],
                        "quantity": random.randint(1, 5)
                    }
                ],
                "delivery_option": "DELIVER_TO_BUYER",
                "notes": f"Demo order {i+1} from distributor"
            }
            
            order_id = create_order(order_data, distributor_token)
            if order_id:
                # Update order status to simulate workflow
                time.sleep(1)
                
                # Accept order
                update_order_status(order_id, {
                    "status": "ACCEPTED",
                    "internal_notes": "Order accepted by manufacturer"
                }, manufacturer_token)
                
                time.sleep(1)
                
                # Pack order
                update_order_status(order_id, {
                    "status": "PACKED",
                    "internal_notes": "Order packed and ready for shipping"
                }, manufacturer_token)
                
                time.sleep(1)
                
                # Ship order
                update_order_status(order_id, {
                    "status": "SHIPPED",
                    "delivery_option": "THIRD_PARTY",
                    "internal_notes": "Order shipped via courier"
                }, manufacturer_token)
                
                time.sleep(1)
                
                # Generate invoice
                generate_invoice(order_id, manufacturer_token)
    
    # Create orders from retailer to distributor
    retailer_token = user_tokens.get("retailer")
    if retailer_token and product_ids:
        for i in range(2):  # Create 2 orders
            order_data = {
                "cart_items": [
                    {
                        "product_id": product_ids[(i+1) % len(product_ids)],
                        "quantity": random.randint(1, 3)
                    }
                ],
                "delivery_option": "SELF_PICKUP",
                "notes": f"Demo order {i+1} from retailer"
            }
            
            order_id = create_order(order_data, retailer_token)
            if order_id:
                # Update order status
                time.sleep(1)
                
                update_order_status(order_id, {
                    "status": "ACCEPTED",
                    "internal_notes": "Order accepted by distributor"
                }, distributor_token)
                
                time.sleep(1)
                
                update_order_status(order_id, {
                    "status": "PACKED",
                    "internal_notes": "Order packed"
                }, distributor_token)
                
                time.sleep(1)
                
                update_order_status(order_id, {
                    "status": "OUT_FOR_DELIVERY",
                    "internal_notes": "Order out for delivery"
                }, distributor_token)
    
    print("\n✅ Comprehensive Seed Data Generation Complete!")
    print("=" * 60)
    print("\n📊 SUMMARY:")
    print(f"   • Users created: {len(user_ids)}")
    print(f"   • Categories created: {len(category_ids)}")
    print(f"   • Products created: {len(product_ids)}")
    print(f"   • Demo orders created: 5")
    print(f"   • Invoices generated: 3")
    
    print("\n🔑 DEMO LOGINS:")
    for user_data in DEMO_USERS:
        print(f"   • {user_data['role'].title()}: {user_data['email']} / {user_data['password']}")
    
    print("\n🌐 Access the application at: http://localhost:3000")
    print("📖 Check the README.md for detailed usage instructions")

if __name__ == "__main__":
    main()
