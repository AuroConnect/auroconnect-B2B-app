#!/usr/bin/env python3
"""
Add Products by Category
Adds one product for each category to demonstrate filtering
"""
import requests
import json
import time

# Configuration
BASE_URL = "http://localhost:5000"
API_BASE = f"{BASE_URL}/api"

# Manufacturer credentials
MANUFACTURER_CREDENTIALS = {
    "email": "m@demo.com",
    "password": "Demo@123"
}

# Products by category
CATEGORY_PRODUCTS = {
    "Electronics": {
        "name": "Samsung Galaxy S24",
        "description": "Latest flagship smartphone with AI features",
        "sku": "SAMSUNG-S24",
        "basePrice": 89999.00,
        "brand": "Samsung",
        "unit": "Pieces",
        "stockQuantity": 50,
        "imageUrl": "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=400"
    },
    "Clothing": {
        "name": "Nike Air Max 270",
        "description": "Comfortable running shoes with Air Max technology",
        "sku": "NIKE-AIR-270",
        "basePrice": 12999.00,
        "brand": "Nike",
        "unit": "Pairs",
        "stockQuantity": 100,
        "imageUrl": "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=400"
    },
    "Furniture": {
        "name": "IKEA Malm Bed Frame",
        "description": "Modern queen-size bed frame with storage",
        "sku": "IKEA-MALM-BED",
        "basePrice": 25000.00,
        "brand": "IKEA",
        "unit": "Pieces",
        "stockQuantity": 25,
        "imageUrl": "https://images.unsplash.com/photo-1505693314120-0d443867891c?w=400"
    },
    "Passenger Elevators": {
        "name": "OTIS Gen3 Elevator",
        "description": "Advanced passenger elevator with smart technology",
        "sku": "OTIS-GEN3-PASS",
        "basePrice": 2500000.00,
        "brand": "OTIS",
        "unit": "Units",
        "stockQuantity": 5,
        "imageUrl": "https://images.unsplash.com/photo-1581091226825-a6a2a5aee158?w=400"
    },
    "Automotive": {
        "name": "Honda City Hybrid",
        "description": "Fuel-efficient hybrid sedan for urban driving",
        "sku": "HONDA-CITY-HYBRID",
        "basePrice": 1500000.00,
        "brand": "Honda",
        "unit": "Units",
        "stockQuantity": 10,
        "imageUrl": "https://images.unsplash.com/photo-1552519507-da3b142c6e3d?w=400"
    },
    "Escalators": {
        "name": "Schindler 9300 Escalator",
        "description": "High-capacity escalator for commercial buildings",
        "sku": "SCHINDLER-9300",
        "basePrice": 1800000.00,
        "brand": "Schindler",
        "unit": "Units",
        "stockQuantity": 8,
        "imageUrl": "https://images.unsplash.com/photo-1581091226825-a6a2a5aee158?w=400"
    },
    "Healthcare": {
        "name": "Philips HeartStart AED",
        "description": "Automated external defibrillator for emergency use",
        "sku": "PHILIPS-AED",
        "basePrice": 150000.00,
        "brand": "Philips",
        "unit": "Units",
        "stockQuantity": 20,
        "imageUrl": "https://images.unsplash.com/photo-1559757148-5c350d0d3c56?w=400"
    },
    "Food & Beverages": {
        "name": "Nestle KitKat Chunky",
        "description": "Premium chocolate bar with extra thick wafer",
        "sku": "NESTLE-KITKAT-CHUNKY",
        "basePrice": 150.00,
        "brand": "Nestle",
        "unit": "Pieces",
        "stockQuantity": 500,
        "imageUrl": "https://images.unsplash.com/photo-1606313564200-e75d5e30476c?w=400"
    },
    "Sports & Fitness": {
        "name": "Bowflex SelectTech Dumbbells",
        "description": "Adjustable dumbbells for home gym",
        "sku": "BOWFLEX-DUMBBELLS",
        "basePrice": 45000.00,
        "brand": "Bowflex",
        "unit": "Pairs",
        "stockQuantity": 15,
        "imageUrl": "https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?w=400"
    },
    "Books & Stationery": {
        "name": "Moleskine Classic Notebook",
        "description": "Premium leather-bound notebook for writing",
        "sku": "MOLESKINE-CLASSIC",
        "basePrice": 2500.00,
        "brand": "Moleskine",
        "unit": "Pieces",
        "stockQuantity": 200,
        "imageUrl": "https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=400"
    }
}

def make_request(method, endpoint, data=None, token=None):
    """Make HTTP request with error handling"""
    url = f"{API_BASE}{endpoint}"
    headers = {'Content-Type': 'application/json'}
    
    if token:
        headers['Authorization'] = f'Bearer {token}'
    
    try:
        if method == 'GET':
            response = requests.get(url, headers=headers)
        elif method == 'POST':
            response = requests.post(url, headers=headers, json=data)
        elif method == 'PUT':
            response = requests.put(url, headers=headers, json=data)
        elif method == 'DELETE':
            response = requests.delete(url, headers=headers)
        
        if response.status_code in [200, 201]:
            return response.json()
        else:
            print(f"❌ {method} {endpoint} failed: {response.status_code} - {response.text}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Network error for {method} {endpoint}: {e}")
        return None

def login_manufacturer():
    """Login as manufacturer and return token"""
    print("🔐 Logging in as manufacturer...")
    
    login_data = {
        'email': MANUFACTURER_CREDENTIALS['email'],
        'password': MANUFACTURER_CREDENTIALS['password']
    }
    
    response = make_request('POST', '/auth/login', login_data)
    if response:
        token = response.get('access_token')
        if token:
            print("✅ Manufacturer login successful")
            return token
        else:
            print("❌ No access token in response")
            return None
    else:
        print("❌ Manufacturer login failed")
        return None

def get_categories(token):
    """Get available categories"""
    print("\n📂 Getting categories...")
    
    response = make_request('GET', '/products/categories', token=token)
    if response:
        print(f"✅ Found {len(response)} categories")
        return response
    else:
        print("❌ Failed to get categories")
        return []

def create_product_for_category(token, category_name, category_id, product_data):
    """Create a product for a specific category"""
    print(f"\n➕ Creating product for {category_name}...")
    
    # Add unique timestamp to SKU to avoid conflicts
    product_data['sku'] = f"{product_data['sku']}-{int(time.time())}"
    product_data['categoryId'] = category_id
    
    response = make_request('POST', '/products', product_data, token)
    if response:
        print(f"✅ Created {product_data['name']} for {category_name}")
        return response
    else:
        print(f"❌ Failed to create product for {category_name}")
        return None

def main():
    """Main function to add products by category"""
    print("🚀 Adding Products by Category")
    print("=" * 50)
    
    # Step 1: Login as manufacturer
    token = login_manufacturer()
    if not token:
        print("❌ Cannot proceed without authentication")
        return False
    
    # Step 2: Get categories
    categories = get_categories(token)
    if not categories:
        print("❌ No categories found")
        return False
    
    # Step 3: Create category mapping
    category_map = {cat['name']: cat['id'] for cat in categories}
    
    # Step 4: Create products for each category
    created_products = []
    
    for category_name, product_data in CATEGORY_PRODUCTS.items():
        if category_name in category_map:
            product = create_product_for_category(
                token, 
                category_name, 
                category_map[category_name], 
                product_data
            )
            if product:
                created_products.append(product)
            time.sleep(1)  # Small delay between requests
        else:
            print(f"⚠️ Category '{category_name}' not found in database")
    
    print("\n" + "=" * 50)
    print(f"🎉 Successfully created {len(created_products)} products")
    print("=" * 50)
    
    print("\n📋 Created Products:")
    for product in created_products:
        print(f"  ✅ {product['name']} - ₹{product['basePrice']:,}")
    
    print("\n🔧 Next Steps:")
    print("  1. Refresh the Products page in your browser")
    print("  2. Test the category filter dropdown")
    print("  3. Test sorting by name and price")
    print("  4. Verify each category has a product")
    
    return True

if __name__ == "__main__":
    main()
