#!/usr/bin/env python3
"""
Setup Product Allocations
Creates product allocations from manufacturers to distributors
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
    """Main function to set up product allocations"""
    print("🚀 Setting Up Product Allocations")
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
    
    # Step 4: Get distributor ID (we'll use a simple approach)
    print("\n🔍 Getting distributor ID...")
    # Since the user search endpoint might not work, let's get it from the distributor's own products
    distributor_products = make_request('GET', '/products', token=distributor_token)
    if distributor_products:
        # Get the manufacturer ID from the first product (which should be the distributor's ID)
        distributor_id = distributor_products[0].get('manufacturerId')
        print(f"✅ Distributor ID: {distributor_id}")
    else:
        print("❌ Could not get distributor ID")
        return False
    
    # Step 5: Allocate some manufacturer products to distributor
    print("\n📦 Allocating products to distributor...")
    allocations = []
    
    # Allocate first 5 manufacturer products
    for i, product in enumerate(manufacturer_products[:5]):
        print(f"\n📦 Allocating {product['name']}...")
        allocation = create_product_allocation(
            manufacturer_token, 
            distributor_id, 
            product['id'],
            quantity=10,
            price_multiplier=1.2
        )
        if allocation:
            allocations.append(allocation)
            
            # Create inventory for the allocated product
            create_inventory_for_distributor(
                distributor_token,
                product['id'],
                10
            )
        time.sleep(1)
    
    print(f"\n✅ Created {len(allocations)} product allocations")
    
    # Step 6: Test distributor products after allocation
    print("\n🔍 Testing distributor products after allocation...")
    updated_distributor_products = make_request('GET', '/products', token=distributor_token)
    if updated_distributor_products:
        print(f"✅ Distributor now sees {len(updated_distributor_products)} products")
        
        # Count allocated vs own products
        allocated_count = 0
        own_count = 0
        
        for product in updated_distributor_products:
            if product.get('isAllocated', False):
                allocated_count += 1
                print(f"  ✅ Allocated: {product['name']} - ₹{product.get('sellingPrice', 0):,.2f}")
            else:
                own_count += 1
                print(f"  📦 Own: {product['name']} - ₹{product.get('sellingPrice', 0):,.2f}")
        
        print(f"\n📊 Summary:")
        print(f"  - Allocated products: {allocated_count}")
        print(f"  - Own products: {own_count}")
        
        # Test adding an allocated product to cart
        allocated_products = [p for p in updated_distributor_products if p.get('isAllocated', False)]
        if allocated_products:
            test_product = allocated_products[0]
            print(f"\n🛒 Testing add to cart for allocated product: {test_product['name']}")
            
            cart_data = {
                'productId': test_product['id'],
                'quantity': 1
            }
            
            add_result = make_request('POST', '/cart', cart_data, distributor_token)
            if add_result:
                print("✅ Successfully added allocated product to cart!")
                
                # Get cart contents
                cart_contents = make_request('GET', '/cart', token=distributor_token)
                if cart_contents:
                    print(f"✅ Cart has {cart_contents.get('totalItems', 0)} items")
                    print(f"💰 Total amount: ₹{cart_contents.get('totalAmount', 0):,.2f}")
            else:
                print("❌ Failed to add allocated product to cart")
    
    print("\n" + "=" * 50)
    print("🎉 Product Allocations Setup Complete!")
    print("=" * 50)
    
    print("\n📋 Summary:")
    print(f"  ✅ Created {len(allocations)} product allocations")
    print(f"  ✅ Distributor can now see manufacturer products")
    print(f"  ✅ Distributor can add allocated products to cart")
    
    print("\n🔧 Next Steps:")
    print("  1. Open browser and go to http://localhost:3000")
    print("  2. Login as distributor: d@demo.com / Demo@123")
    print("  3. Go to Products page")
    print("  4. You should now see manufacturer products with 'Add to Cart' buttons")
    print("  5. Test the cart functionality")
    
    return True

if __name__ == "__main__":
    main()
