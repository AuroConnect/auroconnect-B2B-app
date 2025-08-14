#!/usr/bin/env python3
"""
Simple B2B Test Setup
Sets up basic B2B flow and tests manufacturer filter
"""
import requests
import json
import time

# Configuration
BASE_URL = "http://localhost:5000"
API_BASE = f"{BASE_URL}/api"

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
        
        if response.status_code in [200, 201]:
            return response.json()
        else:
            print(f"❌ {method} {endpoint} failed: {response.status_code} - {response.text}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Network error for {method} {endpoint}: {e}")
        return None

def login_user(email, password):
    """Login user and return token"""
    print(f"🔐 Logging in as {email}...")
    
    login_data = {
        'email': email,
        'password': password
    }
    
    response = make_request('POST', '/auth/login', login_data)
    if response:
        token = response.get('access_token')
        if token:
            print(f"✅ Login successful")
            return token
        else:
            print("❌ No access token in response")
            return None
    else:
        print(f"❌ Login failed")
        return None

def get_user_id(token, email):
    """Get user ID by email"""
    response = make_request('GET', f'/users/search?email={email}', token=token)
    if response and response.get('users'):
        return response['users'][0]['id']
    return None

def create_product_allocation(manufacturer_token, distributor_id, product_id, quantity=10, price_multiplier=1.2):
    """Create product allocation from manufacturer to distributor"""
    # First get the product to know its base price
    product_response = make_request('GET', f'/products/{product_id}', token=manufacturer_token)
    if not product_response:
        return None
    
    base_price = float(product_response.get('basePrice', 1000))
    selling_price = base_price * price_multiplier
    
    allocation_data = {
        'distributorId': distributor_id,
        'productId': product_id,
        'allocatedQuantity': quantity,
        'sellingPrice': selling_price
    }
    
    response = make_request('POST', '/product-allocations', allocation_data, manufacturer_token)
    if response:
        print(f"✅ Allocated product {product_id} to distributor")
        return response
    else:
        print(f"❌ Failed to allocate product {product_id}")
        return None

def main():
    """Main function to set up and test B2B flow"""
    print("🚀 Setting Up Simple B2B Test")
    print("=" * 50)
    
    # Step 1: Login as manufacturer
    manufacturer_token = login_user("m@demo.com", "Demo@123")
    if not manufacturer_token:
        print("❌ Cannot proceed without manufacturer authentication")
        return False
    
    # Step 2: Get manufacturer's products
    print("\n📦 Getting manufacturer products...")
    manufacturer_products = make_request('GET', '/products', token=manufacturer_token)
    if not manufacturer_products:
        print("❌ No manufacturer products found")
        return False
    
    print(f"✅ Manufacturer has {len(manufacturer_products)} products")
    
    # Step 3: Login as distributor
    distributor_token = login_user("d@demo.com", "Demo@123")
    if not distributor_token:
        print("❌ Cannot proceed without distributor authentication")
        return False
    
    # Step 4: Get distributor ID
    distributor_id = get_user_id(manufacturer_token, "d@demo.com")
    if not distributor_id:
        print("❌ Distributor not found")
        return False
    
    print(f"✅ Distributor ID: {distributor_id}")
    
    # Step 5: Allocate some products to distributor
    print("\n📦 Allocating products to distributor...")
    allocations = []
    
    # Allocate first 3 products
    for i, product in enumerate(manufacturer_products[:3]):
        allocation = create_product_allocation(
            manufacturer_token, 
            distributor_id, 
            product['id'],
            quantity=5,
            price_multiplier=1.2
        )
        if allocation:
            allocations.append(allocation)
        time.sleep(1)
    
    print(f"✅ Created {len(allocations)} product allocations")
    
    # Step 6: Test manufacturer filter
    print("\n🔍 Testing manufacturer filter...")
    
    # Get manufacturers for distributor
    manufacturers = make_request('GET', '/products/manufacturers', token=distributor_token)
    if manufacturers:
        print(f"✅ Distributor can filter by {len(manufacturers)} manufacturers")
        for manufacturer in manufacturers:
            print(f"  - {manufacturer['businessName']}")
    else:
        print("❌ No manufacturers found for filtering")
    
    # Step 7: Test filtered products
    if manufacturers:
        first_manufacturer = manufacturers[0]
        manufacturer_id = first_manufacturer['id']
        
        # Get products filtered by manufacturer
        filtered_products = make_request('GET', f'/products?manufacturerId={manufacturer_id}', token=distributor_token)
        if filtered_products:
            print(f"✅ Filtered products: {len(filtered_products)} products from {first_manufacturer['businessName']}")
        else:
            print("❌ No filtered products found")
    
    # Step 8: Test all products for distributor
    print("\n📦 Testing all products for distributor...")
    all_distributor_products = make_request('GET', '/products', token=distributor_token)
    if all_distributor_products:
        print(f"✅ Distributor sees {len(all_distributor_products)} total products")
        
        # Count by manufacturer
        manufacturer_counts = {}
        for product in all_distributor_products:
            manufacturer_id = product.get('manufacturerId')
            if manufacturer_id:
                if manufacturer_id not in manufacturer_counts:
                    manufacturer_counts[manufacturer_id] = 0
                manufacturer_counts[manufacturer_id] += 1
        
        print(f"📊 Products by manufacturer: {manufacturer_counts}")
    
    print("\n" + "=" * 50)
    print("🎉 B2B Test Setup Complete!")
    print("=" * 50)
    
    print("\n📋 Summary:")
    print(f"  ✅ Created {len(allocations)} product allocations")
    print(f"  ✅ Distributor can see {len(all_distributor_products) if all_distributor_products else 0} products")
    print(f"  ✅ Found {len(manufacturers) if manufacturers else 0} manufacturers for filtering")
    
    print("\n🔧 Next Steps:")
    print("  1. Open browser and go to http://localhost:3000")
    print("  2. Login as distributor: d@demo.com / Demo@123")
    print("  3. Go to Products page")
    print("  4. Test the 'All Manufacturers' dropdown filter")
    print("  5. Verify role-based product visibility")
    
    return True

if __name__ == "__main__":
    main()
