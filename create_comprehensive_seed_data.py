#!/usr/bin/env python3
"""
Comprehensive Seed Data Script for AuroMart B2B Platform
Creates demo users, products, inventory, pricing rules, and orders with enhanced features
"""
import requests
import json
import time
import os
from datetime import datetime, timedelta
import openpyxl
from io import BytesIO

# Configuration
BASE_URL = "http://localhost:5000"
API_BASE = f"{BASE_URL}/api"

# Test credentials
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

# Enhanced Categories with more products
CATEGORIES = [
    {
        "name": "Laptops & Computers",
        "description": "High-performance laptops and desktop computers",
        "brands": ["Dell", "HP", "Lenovo", "Apple", "Asus", "Acer", "MSI", "Razer", "Samsung", "Toshiba"]
    },
    {
        "name": "Mobile Phones",
        "description": "Smartphones and mobile accessories",
        "brands": ["Apple", "Samsung", "Xiaomi", "OnePlus", "OPPO", "Vivo", "Realme", "Nothing", "Google", "Motorola"]
    },
    {
        "name": "Clothing & Fashion",
        "description": "Trendy clothing and fashion accessories",
        "brands": ["Nike", "Adidas", "Puma", "Levi's", "Zara", "H&M", "Uniqlo", "Gap", "Tommy Hilfiger", "Calvin Klein"]
    },
    {
        "name": "Home & Furniture",
        "description": "Home decor and furniture items",
        "brands": ["IKEA", "Urban Ladder", "Pepperfry", "Wakefit", "SleepyCat", "Duroflex", "Kurl-on", "Godrej", "Nilkamal", "Durian"]
    },
    {
        "name": "Electronics & Gadgets",
        "description": "Electronic gadgets and accessories",
        "brands": ["Sony", "LG", "Panasonic", "Philips", "JBL", "Boat", "Mi", "Realme", "OnePlus", "Samsung"]
    }
]

# Enhanced Sample Products (10 per category)
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
    ],
    "Clothing & Fashion": [
        {"name": "Nike Air Max 270", "sku": "NIKE-AIR-270", "base_price": 12000, "description": "Comfortable running shoes", "brand": "Nike"},
        {"name": "Adidas Ultraboost 22", "sku": "ADIDAS-ULTRA-22", "base_price": 15000, "description": "Premium running shoes", "brand": "Adidas"},
        {"name": "Puma RS-X", "sku": "PUMA-RSX", "base_price": 8000, "description": "Retro-inspired sneakers", "brand": "Puma"},
        {"name": "Levi's 501 Jeans", "sku": "LEVIS-501", "base_price": 3500, "description": "Classic straight fit jeans", "brand": "Levi's"},
        {"name": "Zara Summer Dress", "sku": "ZARA-SUMMER-DRESS", "base_price": 2500, "description": "Elegant summer collection", "brand": "Zara"},
        {"name": "H&M Casual Shirt", "sku": "HM-CASUAL-SHIRT", "base_price": 1200, "description": "Comfortable casual wear", "brand": "H&M"},
        {"name": "Uniqlo Heattech T-Shirt", "sku": "UNIQLO-HEAT-TEE", "base_price": 800, "description": "Thermal technology t-shirt", "brand": "Uniqlo"},
        {"name": "Gap Denim Jacket", "sku": "GAP-DENIM-JACKET", "base_price": 4500, "description": "Classic denim jacket", "brand": "Gap"},
        {"name": "Tommy Hilfiger Polo", "sku": "TOMMY-POLO", "base_price": 2800, "description": "Premium polo shirt", "brand": "Tommy Hilfiger"},
        {"name": "Calvin Klein Underwear", "sku": "CK-UNDERWEAR", "base_price": 1500, "description": "Comfortable innerwear", "brand": "Calvin Klein"}
    ],
    "Home & Furniture": [
        {"name": "IKEA MALM Bed", "sku": "IKEA-MALM-BED", "base_price": 25000, "description": "Queen size wooden bed frame", "brand": "IKEA"},
        {"name": "Urban Ladder Sofa", "sku": "URBAN-SOFA-3S", "base_price": 35000, "description": "3-seater fabric sofa", "brand": "Urban Ladder"},
        {"name": "Pepperfry Dining Table", "sku": "PEPPER-DINING-6", "base_price": 18000, "description": "6-seater dining table", "brand": "Pepperfry"},
        {"name": "Wakefit Mattress", "sku": "WAKE-MATT-QUEEN", "base_price": 12000, "description": "Queen size memory foam mattress", "brand": "Wakefit"},
        {"name": "SleepyCat Pillow", "sku": "SLEEPY-PILLOW", "base_price": 800, "description": "Memory foam pillow", "brand": "SleepyCat"},
        {"name": "Duroflex Mattress", "sku": "DURO-MATT-KING", "base_price": 15000, "description": "King size spring mattress", "brand": "Duroflex"},
        {"name": "Kurl-on Chair", "sku": "KURL-CHAIR-OFFICE", "base_price": 3500, "description": "Ergonomic office chair", "brand": "Kurl-on"},
        {"name": "Godrej Almirah", "sku": "GODREJ-ALMIRAH", "base_price": 22000, "description": "3-door wooden almirah", "brand": "Godrej"},
        {"name": "Nilkamal Plastic Chair", "sku": "NILKAMAL-CHAIR", "base_price": 800, "description": "Stackable plastic chair", "brand": "Nilkamal"},
        {"name": "Durian Sofa Set", "sku": "DURIAN-SOFA-5S", "base_price": 45000, "description": "5-seater leather sofa", "brand": "Durian"}
    ],
    "Electronics & Gadgets": [
        {"name": "Sony WH-1000XM5", "sku": "SONY-WH-1000XM5", "base_price": 28000, "description": "Premium noise-cancelling headphones", "brand": "Sony"},
        {"name": "LG OLED TV 65", "sku": "LG-OLED-65C3", "base_price": 180000, "description": "65-inch OLED smart TV", "brand": "LG"},
        {"name": "Panasonic Microwave", "sku": "PANA-MICRO-25L", "base_price": 8500, "description": "25L convection microwave", "brand": "Panasonic"},
        {"name": "Philips Air Fryer", "sku": "PHILIPS-AIR-FRY", "base_price": 12000, "description": "Digital air fryer", "brand": "Philips"},
        {"name": "JBL Flip 6", "sku": "JBL-FLIP-6", "base_price": 8500, "description": "Portable Bluetooth speaker", "brand": "JBL"},
        {"name": "Boat Airdopes", "sku": "BOAT-AIRDOPES-141", "base_price": 1500, "description": "Wireless earbuds", "brand": "Boat"},
        {"name": "Mi Smart Band 8", "sku": "MI-BAND-8", "base_price": 2500, "description": "Fitness tracking smartband", "brand": "Mi"},
        {"name": "Realme Watch 3", "sku": "REALME-WATCH-3", "base_price": 3500, "description": "Smartwatch with health monitoring", "brand": "Realme"},
        {"name": "OnePlus Buds Pro", "sku": "ONEPLUS-BUDS-PRO", "base_price": 9500, "description": "Active noise cancellation earbuds", "brand": "OnePlus"},
        {"name": "Samsung Galaxy Watch", "sku": "SAMS-GAL-WATCH-6", "base_price": 28000, "description": "Premium smartwatch", "brand": "Samsung"}
    ]
}

# Pricing Rules
PRICING_RULES = [
    {
        "name": "Volume Discount - Electronics",
        "rule_type": "VOLUME",
        "discount_type": "PERCENTAGE",
        "discount_value": 10,
        "min_quantity": 5,
        "max_quantity": 10,
        "category_id": None,  # Will be set dynamically
        "priority": 1
    },
    {
        "name": "Seasonal Sale - Clothing",
        "rule_type": "SEASONAL",
        "discount_type": "PERCENTAGE",
        "discount_value": 15,
        "start_date": "2024-01-01",
        "end_date": "2024-12-31",
        "category_id": None,  # Will be set dynamically
        "priority": 2
    },
    {
        "name": "Partner Discount - Distributor",
        "rule_type": "PARTNER",
        "discount_type": "PERCENTAGE",
        "discount_value": 8,
        "priority": 3
    }
]

# Promo Codes
PROMO_CODES = [
    {
        "code": "WELCOME10",
        "name": "Welcome Discount",
        "description": "10% off for new customers",
        "discount_type": "PERCENTAGE",
        "discount_value": 10,
        "min_order_amount": 1000,
        "max_discount_amount": 2000,
        "max_uses": 100,
        "applicable_roles": "retailer,distributor",
        "start_date": "2024-01-01",
        "end_date": "2024-12-31"
    },
    {
        "code": "BULK20",
        "name": "Bulk Purchase Discount",
        "description": "20% off on bulk orders",
        "discount_type": "PERCENTAGE",
        "discount_value": 20,
        "min_order_amount": 5000,
        "max_discount_amount": 5000,
        "max_uses": 50,
        "applicable_roles": "distributor",
        "start_date": "2024-01-01",
        "end_date": "2024-12-31"
    },
    {
        "code": "FLAT500",
        "name": "Flat Discount",
        "description": "Flat ₹500 off on orders above ₹3000",
        "discount_type": "FIXED_AMOUNT",
        "discount_value": 500,
        "min_order_amount": 3000,
        "max_uses": 200,
        "applicable_roles": "retailer,distributor",
        "start_date": "2024-01-01",
        "end_date": "2024-12-31"
    }
]

def make_request(method, endpoint, data=None, is_form_data=False):
    """Make API request with proper headers"""
    url = f"{API_BASE}{endpoint}"
    headers = {}
    
    if not is_form_data and data:
        headers['Content-Type'] = 'application/json'
    
    try:
        if method == "GET":
            response = requests.get(url, headers=headers)
        elif method == "POST":
            if is_form_data:
                response = requests.post(url, files=data, headers=headers)
            else:
                response = requests.post(url, json=data, headers=headers)
        elif method == "PUT":
            response = requests.put(url, json=data, headers=headers)
        elif method == "DELETE":
            response = requests.delete(url, headers=headers)
        
        if response.status_code in [200, 201]:
            return response.json()
        else:
            print(f"❌ {method} {endpoint} failed: {response.status_code} - {response.text}")
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

def create_inventory(product_id, distributor_id, token):
    """Create inventory for a product"""
    headers = {"Authorization": f"Bearer {token}"}
    url = f"{API_BASE}/inventory"
    
    # Random inventory data
    import random
    quantity = random.randint(10, 100)
    low_stock_threshold = max(5, quantity // 4)
    auto_restock_quantity = quantity + random.randint(20, 50)
    selling_price = random.randint(1000, 50000)
    
    inventory_data = {
        "product_id": product_id,
        "distributor_id": distributor_id,
        "quantity": quantity,
        "low_stock_threshold": low_stock_threshold,
        "auto_restock_quantity": auto_restock_quantity,
        "selling_price": selling_price,
        "is_available": True
    }
    
    try:
        response = requests.post(url, json=inventory_data, headers=headers)
        if response.status_code == 201:
            result = response.json()
            print(f"✅ Inventory created for product {product_id}")
            return result
        else:
            print(f"❌ Failed to create inventory: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error creating inventory: {str(e)}")
        return None

def create_pricing_rule(rule_data, token):
    """Create a pricing rule"""
    headers = {"Authorization": f"Bearer {token}"}
    url = f"{API_BASE}/pricing/rules"
    
    try:
        response = requests.post(url, json=rule_data, headers=headers)
        if response.status_code == 201:
            result = response.json()
            print(f"✅ Pricing rule '{rule_data['name']}' created")
            return result
        else:
            print(f"❌ Failed to create pricing rule: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error creating pricing rule: {str(e)}")
        return None

def create_promo_code(promo_data, token):
    """Create a promo code"""
    headers = {"Authorization": f"Bearer {token}"}
    url = f"{API_BASE}/pricing/promo-codes"
    
    try:
        response = requests.post(url, json=promo_data, headers=headers)
        if response.status_code == 201:
            result = response.json()
            print(f"✅ Promo code '{promo_data['code']}' created")
            return result
        else:
            print(f"❌ Failed to create promo code: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error creating promo code: {str(e)}")
        return None

def create_order(buyer_token, seller_id, products, order_data=None):
    """Create an order"""
    headers = {"Authorization": f"Bearer {buyer_token}"}
    url = f"{API_BASE}/orders"
    
    # Add products to cart first
    for product in products:
        cart_data = {
            "productId": product["id"],
            "quantity": product["quantity"]
        }
        cart_response = requests.post(f"{API_BASE}/cart", json=cart_data, headers=headers)
        if cart_response.status_code != 201:
            print(f"❌ Failed to add product to cart: {cart_response.text}")
            return None
    
    # Create order
    order_payload = {
        "seller_id": seller_id,
        "delivery_option": "DELIVER_TO_BUYER",
        "notes": order_data.get("notes", "Demo order"),
        "allow_split_shipment": order_data.get("allow_split_shipment", False),
        "allow_backorders": order_data.get("allow_backorders", True),
        "order_tags": order_data.get("order_tags", ""),
        "priority": order_data.get("priority", "NORMAL")
    }
    
    try:
        response = requests.post(url, json=order_payload, headers=headers)
        if response.status_code == 201:
            result = response.json()
            print(f"✅ Order created successfully")
            return result
        else:
            print(f"❌ Failed to create order: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error creating order: {str(e)}")
        return None

def update_order_status(order_id, status, token, notes=None):
    """Update order status"""
    headers = {"Authorization": f"Bearer {token}"}
    url = f"{API_BASE}/orders/{order_id}/status"
    
    status_data = {
        "status": status,
        "notes": notes or f"Status updated to {status}"
    }
    
    try:
        response = requests.put(url, json=status_data, headers=headers)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Order {order_id} status updated to {status}")
            return result
        else:
            print(f"❌ Failed to update order status: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error updating order status: {str(e)}")
        return None

def generate_invoice(order_id, token):
    """Generate invoice for an order"""
    headers = {"Authorization": f"Bearer {token}"}
    url = f"{API_BASE}/invoices/generate/{order_id}"
    
    try:
        response = requests.post(url, headers=headers)
        if response.status_code == 201:
            result = response.json()
            print(f"✅ Invoice generated for order {order_id}")
            return result
        else:
            print(f"❌ Failed to generate invoice: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error generating invoice: {str(e)}")
        return None

def main():
    """Main function to create comprehensive seed data"""
    print("🚀 Starting comprehensive seed data creation...")
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
    
    # Step 4: Create inventory for distributors
    print("\n📋 Step 4: Creating inventory...")
    
    # Create inventory for distributor
    distributor_id = users["distributor"]["id"]
    for product in all_products[:20]:  # Create inventory for first 20 products
        create_inventory(product["id"], distributor_id, tokens["distributor"])
    
    print(f"✅ Created inventory for distributor")
    
    # Step 5: Create pricing rules
    print("\n📋 Step 5: Creating pricing rules...")
    
    # Get category IDs for pricing rules
    electronics_category = categories.get("Electronics & Gadgets")
    clothing_category = categories.get("Clothing & Fashion")
    
    for rule_data in PRICING_RULES:
        if "Electronics" in rule_data["name"] and electronics_category:
            rule_data["category_id"] = electronics_category["id"]
        elif "Clothing" in rule_data["name"] and clothing_category:
            rule_data["category_id"] = clothing_category["id"]
        
        create_pricing_rule(rule_data, tokens["manufacturer"])
    
    print(f"✅ Created pricing rules")
    
    # Step 6: Create promo codes
    print("\n📋 Step 6: Creating promo codes...")
    
    for promo_data in PROMO_CODES:
        create_promo_code(promo_data, tokens["manufacturer"])
    
    print(f"✅ Created promo codes")
    
    # Step 7: Create demo orders
    print("\n📋 Step 7: Creating demo orders...")
    
    # Order 1: Distributor to Manufacturer
    distributor_products = all_products[:3]
    order1_data = {
        "notes": "First bulk order from distributor",
        "allow_split_shipment": True,
        "allow_backorders": True,
        "order_tags": "BULK,URGENT",
        "priority": "HIGH"
    }
    
    order1 = create_order(tokens["distributor"], users["manufacturer"]["id"], distributor_products, order1_data)
    
    if order1:
        # Update order status
        time.sleep(1)
        update_order_status(order1["id"], "ACCEPTED", tokens["manufacturer"])
        time.sleep(1)
        update_order_status(order1["id"], "PACKED", tokens["manufacturer"])
        time.sleep(1)
        update_order_status(order1["id"], "SHIPPED", tokens["manufacturer"])
        time.sleep(1)
        update_order_status(order1["id"], "DELIVERED", tokens["manufacturer"])
        
        # Generate invoice
        generate_invoice(order1["id"], tokens["manufacturer"])
    
    # Order 2: Retailer to Distributor
    retailer_products = all_products[3:6]
    order2_data = {
        "notes": "Regular order from retailer",
        "allow_split_shipment": False,
        "allow_backorders": True,
        "order_tags": "REGULAR",
        "priority": "NORMAL"
    }
    
    order2 = create_order(tokens["retailer"], users["distributor"]["id"], retailer_products, order2_data)
    
    if order2:
        # Update order status
        time.sleep(1)
        update_order_status(order2["id"], "ACCEPTED", tokens["distributor"])
        time.sleep(1)
        update_order_status(order2["id"], "PACKED", tokens["distributor"])
    
    # Order 3: Partial order with backorders
    order3_products = all_products[6:9]
    order3_data = {
        "notes": "Order with some items on backorder",
        "allow_split_shipment": True,
        "allow_backorders": True,
        "order_tags": "PARTIAL",
        "priority": "NORMAL"
    }
    
    order3 = create_order(tokens["retailer"], users["distributor"]["id"], order3_products, order3_data)
    
    if order3:
        time.sleep(1)
        update_order_status(order3["id"], "PARTIAL", tokens["distributor"], "Some items are out of stock")
    
    print(f"✅ Created demo orders with various statuses")
    
    # Step 8: Create some low stock inventory for testing alerts
    print("\n📋 Step 8: Creating low stock items for testing...")
    
    # Create some inventory with low stock
    low_stock_products = all_products[10:15]
    for product in low_stock_products:
        headers = {"Authorization": f"Bearer {tokens['distributor']}"}
        url = f"{API_BASE}/inventory"
        
        inventory_data = {
            "product_id": product["id"],
            "distributor_id": distributor_id,
            "quantity": 3,  # Low quantity
            "low_stock_threshold": 5,
            "auto_restock_quantity": 20,
            "selling_price": 5000,
            "is_available": True
        }
        
        try:
            response = requests.post(url, json=inventory_data, headers=headers)
            if response.status_code == 201:
                print(f"✅ Created low stock inventory for {product['name']}")
        except Exception as e:
            print(f"❌ Error creating low stock inventory: {str(e)}")
    
    print("\n" + "=" * 60)
    print("🎉 Comprehensive seed data creation completed!")
    print("\n📊 Summary:")
    print(f"   • Users: {len(users)} (Manufacturer, Distributor, Retailer)")
    print(f"   • Categories: {len(categories)}")
    print(f"   • Products: {len(all_products)} (10 per category)")
    print(f"   • Inventory: Created for distributor")
    print(f"   • Pricing Rules: {len(PRICING_RULES)}")
    print(f"   • Promo Codes: {len(PROMO_CODES)}")
    print(f"   • Demo Orders: 3 orders with various statuses")
    print(f"   • Low Stock Items: 5 items for testing alerts")
    
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
