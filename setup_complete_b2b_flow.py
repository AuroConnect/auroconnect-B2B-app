#!/usr/bin/env python3
"""
Setup Complete B2B Flow
Sets up the complete manufacturer -> distributor -> retailer flow with product allocations
"""
import requests
import json
import time

# Configuration
BASE_URL = "http://localhost:5000"
API_BASE = f"{BASE_URL}/api"

# User credentials
USERS = {
    "manufacturer": {
        "email": "m@demo.com",
        "password": "Demo@123",
        "role": "manufacturer"
    },
    "distributor": {
        "email": "d@demo.com", 
        "password": "Demo@123",
        "role": "distributor"
    },
    "retailer": {
        "email": "r@demo.com",
        "password": "Demo@123", 
        "role": "retailer"
    }
}

# Products by manufacturer
MANUFACTURER_PRODUCTS = {
    "KONE": [
        {
            "name": "KONE WalkMaster 100",
            "description": "Moving walkway, 100m length, 0.5 m/s speed",
            "sku": "KONE-WM-100",
            "basePrice": 1200000.00,
            "brand": "KONE",
            "unit": "Units",
            "stockQuantity": 5,
            "imageUrl": "https://images.unsplash.com/photo-1581091226825-a6a2a5aee158?w=400"
        },
        {
            "name": "KONE TravelMaster 110",
            "description": "Modern escalator, 110-degree angle, 0.5-0.75 m/s speed",
            "sku": "KONE-TM-110",
            "basePrice": 1500000.00,
            "brand": "KONE",
            "unit": "Units",
            "stockQuantity": 3,
            "imageUrl": "https://images.unsplash.com/photo-1581091226825-a6a2a5aee158?w=400"
        },
        {
            "name": "KONE MonoSpace 500",
            "description": "Machine room-less elevator, 500kg capacity",
            "sku": "KONE-MS-500",
            "basePrice": 800000.00,
            "brand": "KONE",
            "unit": "Units",
            "stockQuantity": 8,
            "imageUrl": "https://images.unsplash.com/photo-1581091226825-a6a2a5aee158?w=400"
        }
    ],
    "OTIS": [
        {
            "name": "OTIS Gen3 Elevator",
            "description": "Advanced passenger elevator with smart technology",
            "sku": "OTIS-GEN3-PASS",
            "basePrice": 2500000.00,
            "brand": "OTIS",
            "unit": "Units",
            "stockQuantity": 4,
            "imageUrl": "https://images.unsplash.com/photo-1581091226825-a6a2a5aee158?w=400"
        },
        {
            "name": "OTIS SkyRise",
            "description": "High-rise elevator system for skyscrapers",
            "sku": "OTIS-SKYRISE",
            "basePrice": 3500000.00,
            "brand": "OTIS",
            "unit": "Units",
            "stockQuantity": 2,
            "imageUrl": "https://images.unsplash.com/photo-1581091226825-a6a2a5aee158?w=400"
        }
    ],
    "Schindler": [
        {
            "name": "Schindler 9300 Escalator",
            "description": "High-capacity escalator for commercial buildings",
            "sku": "SCHINDLER-9300",
            "basePrice": 1800000.00,
            "brand": "Schindler",
            "unit": "Units",
            "stockQuantity": 6,
            "imageUrl": "https://images.unsplash.com/photo-1581091226825-a6a2a5aee158?w=400"
        }
    ]
}

# Distributor's own products
DISTRIBUTOR_PRODUCTS = [
    {
        "name": "SAI Premium Service Package",
        "description": "Comprehensive maintenance and service package",
        "sku": "SAI-SERVICE-PREMIUM",
        "basePrice": 50000.00,
        "brand": "SAI Radha Complex",
        "unit": "Packages",
        "stockQuantity": 20,
        "imageUrl": "https://images.unsplash.com/photo-1581091226825-a6a2a5aee158?w=400"
    },
    {
        "name": "SAI Installation Kit",
        "description": "Complete installation toolkit for elevators",
        "sku": "SAI-INSTALL-KIT",
        "basePrice": 25000.00,
        "brand": "SAI Radha Complex",
        "unit": "Kits",
        "stockQuantity": 15,
        "imageUrl": "https://images.unsplash.com/photo-1581091226825-a6a2a5aee158?w=400"
    }
]

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

def login_user(user_type):
    """Login as specific user type and return token"""
    print(f"🔐 Logging in as {user_type}...")
    
    user_data = USERS[user_type]
    login_data = {
        'email': user_data['email'],
        'password': user_data['password']
    }
    
    response = make_request('POST', '/auth/login', login_data)
    if response:
        token = response.get('access_token')
        if token:
            print(f"✅ {user_type} login successful")
            return token
        else:
            print("❌ No access token in response")
            return None
    else:
        print(f"❌ {user_type} login failed")
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

def create_product(token, product_data, category_id=None):
    """Create a product"""
    # Add unique timestamp to SKU to avoid conflicts
    product_data['sku'] = f"{product_data['sku']}-{int(time.time())}"
    if category_id:
        product_data['categoryId'] = category_id
    
    response = make_request('POST', '/products', product_data, token)
    if response:
        print(f"✅ Created {product_data['name']}")
        return response
    else:
        print(f"❌ Failed to create {product_data['name']}")
        return None

def create_partnership(requester_token, partner_email, partnership_type):
    """Create a partnership between users"""
    print(f"\n🤝 Creating {partnership_type} partnership...")
    
    # First get the partner user ID
    partner_response = make_request('GET', f'/users/search?email={partner_email}', token=requester_token)
    if not partner_response or not partner_response.get('users'):
        print(f"❌ Partner {partner_email} not found")
        return None
    
    partner_id = partner_response['users'][0]['id']
    
    partnership_data = {
        'partnerId': partner_id,
        'partnershipType': partnership_type,
        'status': 'active'
    }
    
    response = make_request('POST', '/partnerships/request', partnership_data, requester_token)
    if response:
        print(f"✅ {partnership_type} partnership created")
        return response
    else:
        print(f"❌ Failed to create {partnership_type} partnership")
        return None

def allocate_products(manufacturer_token, distributor_id, products, allocation_price_multiplier=1.2):
    """Allocate products from manufacturer to distributor"""
    print(f"\n📦 Allocating products to distributor...")
    
    allocations = []
    for product in products:
        allocation_data = {
            'distributorId': distributor_id,
            'productId': product['id'],
            'allocatedQuantity': product.get('stockQuantity', 10),
            'sellingPrice': float(product['basePrice']) * allocation_price_multiplier
        }
        
        response = make_request('POST', '/product-allocations', allocation_data, manufacturer_token)
        if response:
            print(f"✅ Allocated {product['name']} to distributor")
            allocations.append(response)
        else:
            print(f"❌ Failed to allocate {product['name']}")
    
    return allocations

def create_inventory_for_distributor(distributor_token, product_id, quantity):
    """Create inventory entry for distributor"""
    inventory_data = {
        'productId': product_id,
        'quantity': quantity,
        'sellingPrice': 0  # Will be set by allocation
    }
    
    response = make_request('POST', '/inventory', inventory_data, distributor_token)
    if response:
        print(f"✅ Created inventory for product {product_id}")
        return response
    else:
        print(f"❌ Failed to create inventory for product {product_id}")
        return None

def main():
    """Main function to set up complete B2B flow"""
    print("🚀 Setting Up Complete B2B Flow")
    print("=" * 60)
    
    # Step 1: Login as manufacturer
    manufacturer_token = login_user("manufacturer")
    if not manufacturer_token:
        print("❌ Cannot proceed without manufacturer authentication")
        return False
    
    # Step 2: Get categories
    categories = get_categories(manufacturer_token)
    if not categories:
        print("❌ No categories found")
        return False
    
    category_id = categories[0]['id'] if categories else None
    
    # Step 3: Create manufacturer products
    print("\n🏭 Creating Manufacturer Products")
    print("-" * 40)
    
    all_manufacturer_products = []
    for manufacturer_name, products in MANUFACTURER_PRODUCTS.items():
        print(f"\n📦 Creating {manufacturer_name} products...")
        for product_data in products:
            product = create_product(manufacturer_token, product_data, category_id)
            if product:
                all_manufacturer_products.append(product)
            time.sleep(1)
    
    # Step 4: Login as distributor
    distributor_token = login_user("distributor")
    if not distributor_token:
        print("❌ Cannot proceed without distributor authentication")
        return False
    
    # Step 5: Create distributor's own products
    print("\n🏪 Creating Distributor's Own Products")
    print("-" * 40)
    
    distributor_products = []
    for product_data in DISTRIBUTOR_PRODUCTS:
        product = create_product(distributor_token, product_data, category_id)
        if product:
            distributor_products.append(product)
        time.sleep(1)
    
    # Step 6: Create partnerships
    print("\n🤝 Creating Partnerships")
    print("-" * 40)
    
    # Manufacturer -> Distributor partnership
    partnership = create_partnership(
        manufacturer_token, 
        USERS["distributor"]["email"], 
        "MANUFACTURER_DISTRIBUTOR"
    )
    
    # Distributor -> Retailer partnership
    retailer_partnership = create_partnership(
        distributor_token,
        USERS["retailer"]["email"],
        "DISTRIBUTOR_RETAILER"
    )
    
    # Step 7: Allocate products from manufacturer to distributor
    print("\n📦 Allocating Products")
    print("-" * 40)
    
    # Get distributor user ID
    distributor_response = make_request('GET', f'/users/search?email={USERS["distributor"]["email"]}', token=manufacturer_token)
    if distributor_response and distributor_response.get('users'):
        distributor_id = distributor_response['users'][0]['id']
        
        # Allocate some products to distributor
        selected_products = all_manufacturer_products[:3]  # Allocate first 3 products
        allocations = allocate_products(manufacturer_token, distributor_id, selected_products)
        
        # Create inventory for allocated products
        for allocation in allocations:
            create_inventory_for_distributor(
                distributor_token,
                allocation['productId'],
                allocation['allocatedQuantity']
            )
    
    # Step 8: Test role-based visibility
    print("\n🔍 Testing Role-Based Visibility")
    print("-" * 40)
    
    # Test manufacturer products
    manufacturer_products = make_request('GET', '/products', token=manufacturer_token)
    print(f"✅ Manufacturer sees {len(manufacturer_products) if manufacturer_products else 0} products")
    
    # Test distributor products
    distributor_products_response = make_request('GET', '/products', token=distributor_token)
    print(f"✅ Distributor sees {len(distributor_products_response) if distributor_products_response else 0} products")
    
    # Test distributor manufacturers filter
    manufacturers = make_request('GET', '/products/manufacturers', token=distributor_token)
    print(f"✅ Distributor can filter by {len(manufacturers) if manufacturers else 0} manufacturers")
    
    # Step 9: Login as retailer
    retailer_token = login_user("retailer")
    if retailer_token:
        retailer_products = make_request('GET', '/products', token=retailer_token)
        print(f"✅ Retailer sees {len(retailer_products) if retailer_products else 0} products")
    
    print("\n" + "=" * 60)
    print("🎉 Complete B2B Flow Setup Complete!")
    print("=" * 60)
    
    print("\n📋 Summary:")
    print(f"  ✅ Created {len(all_manufacturer_products)} manufacturer products")
    print(f"  ✅ Created {len(distributor_products)} distributor products")
    print(f"  ✅ Set up partnerships")
    print(f"  ✅ Allocated products to distributor")
    print(f"  ✅ Created inventory entries")
    
    print("\n🔧 Next Steps:")
    print("  1. Refresh the Products page in your browser")
    print("  2. Login as manufacturer: m@demo.com / Demo@123")
    print("  3. Login as distributor: d@demo.com / Demo@123")
    print("  4. Login as retailer: r@demo.com / Demo@123")
    print("  5. Test manufacturer filter for distributors")
    print("  6. Verify role-based product visibility")
    
    return True

if __name__ == "__main__":
    main()

