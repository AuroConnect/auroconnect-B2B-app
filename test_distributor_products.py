#!/usr/bin/env python3
"""
Test Distributor Products
See what products distributors are seeing and identify cart issues
"""
import requests
import json

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

def test_distributor_products():
    """Test distributor products and cart functionality"""
    print("🔍 Testing Distributor Products")
    print("=" * 50)
    
    # Login as distributor
    distributor_token = login_user("d@demo.com", "Demo@123")
    if not distributor_token:
        print("❌ Cannot proceed without distributor authentication")
        return False
    
    # Get distributor's products
    print("\n📦 Getting distributor products...")
    distributor_products = make_request('GET', '/products', token=distributor_token)
    if distributor_products:
        print(f"✅ Distributor sees {len(distributor_products)} products")
        
        print("\n📋 Product Details:")
        print("-" * 40)
        
        for i, product in enumerate(distributor_products, 1):
            print(f"\n{i}. {product['name']}")
            print(f"   SKU: {product['sku']}")
            print(f"   Price: ₹{product.get('sellingPrice', 0):,.2f}")
            print(f"   Stock: {product.get('availableStock', 0)}")
            print(f"   Manufacturer: {product.get('manufacturerName', 'Unknown')}")
            print(f"   Is Allocated: {product.get('isAllocated', False)}")
            print(f"   Manufacturer ID: {product.get('manufacturerId', 'Unknown')}")
            
            # Try to add to cart
            print(f"   🛒 Testing add to cart...")
            cart_data = {
                'productId': product['id'],
                'quantity': 1
            }
            
            add_result = make_request('POST', '/cart', cart_data, distributor_token)
            if add_result:
                print(f"   ✅ Successfully added to cart")
            else:
                print(f"   ❌ Failed to add to cart")
        
        # Get cart contents
        print("\n📋 Getting cart contents...")
        cart_contents = make_request('GET', '/cart', token=distributor_token)
        if cart_contents:
            print(f"✅ Cart has {cart_contents.get('totalItems', 0)} items")
            print(f"💰 Total amount: ₹{cart_contents.get('totalAmount', 0):,.2f}")
            
            items = cart_contents.get('items', [])
            for item in items:
                print(f"  - {item['productName']}: {item['quantity']} x ₹{item['unitPrice']:,.2f} = ₹{item['totalPrice']:,.2f}")
        else:
            print("❌ Failed to get cart contents")
    else:
        print("❌ Failed to get distributor products")
    
    print("\n" + "=" * 50)
    print("🎉 Distributor Products Test Complete!")
    print("=" * 50)
    
    return True

if __name__ == "__main__":
    test_distributor_products()
