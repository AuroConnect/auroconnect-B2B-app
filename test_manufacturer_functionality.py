#!/usr/bin/env python3
"""
Test Manufacturer Functionality
Tests that manufacturer can add and edit products
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

def get_manufacturer_products(token):
    """Get manufacturer's products"""
    print("\n📦 Getting manufacturer products...")
    
    response = make_request('GET', '/products', token=token)
    if response:
        print(f"✅ Found {len(response)} products")
        return response
    else:
        print("❌ Failed to get products")
        return []

def create_test_product(token, categories):
    """Create a test product"""
    print("\n➕ Creating test product...")
    
    # Get first category if available
    category_id = categories[0]['id'] if categories else None
    
    product_data = {
        'name': 'Test Elevator Product',
        'description': 'A test elevator product for manufacturer functionality testing',
        'sku': f'TEST-ELEVATOR-{int(time.time())}',
        'categoryId': category_id,
        'basePrice': 1500000.00,
        'imageUrl': 'https://images.unsplash.com/photo-1581091226825-a6a2a5aee158?w=400'
    }
    
    response = make_request('POST', '/products', product_data, token)
    if response:
        print("✅ Test product created successfully")
        return response
    else:
        print("❌ Failed to create test product")
        return None

def update_test_product(token, product_id):
    """Update the test product"""
    print("\n✏️ Updating test product...")
    
    update_data = {
        'name': 'Updated Test Elevator Product',
        'description': 'This product has been updated by the manufacturer',
        'basePrice': 1800000.00
    }
    
    response = make_request('PUT', f'/products/{product_id}', update_data, token)
    if response:
        print("✅ Test product updated successfully")
        return response
    else:
        print("❌ Failed to update test product")
        return None

def delete_test_product(token, product_id):
    """Delete the test product"""
    print("\n🗑️ Deleting test product...")
    
    response = make_request('DELETE', f'/products/{product_id}', token=token)
    if response:
        print("✅ Test product deleted successfully")
        return True
    else:
        print("❌ Failed to delete test product")
        return False

def test_manufacturer_functionality():
    """Test complete manufacturer functionality"""
    print("🚀 Testing Manufacturer Functionality")
    print("=" * 50)
    
    # Step 1: Login as manufacturer
    token = login_manufacturer()
    if not token:
        print("❌ Cannot proceed without authentication")
        return False
    
    # Step 2: Get categories
    categories = get_categories(token)
    
    # Step 3: Get current products
    current_products = get_manufacturer_products(token)
    initial_count = len(current_products)
    
    # Step 4: Create test product
    new_product = create_test_product(token, categories)
    if not new_product:
        return False
    
    product_id = new_product['id']
    
    # Step 5: Verify product was created
    updated_products = get_manufacturer_products(token)
    if len(updated_products) == initial_count + 1:
        print("✅ Product count increased correctly")
    else:
        print(f"❌ Product count mismatch: expected {initial_count + 1}, got {len(updated_products)}")
    
    # Step 6: Update test product
    updated_product = update_test_product(token, product_id)
    if not updated_product:
        return False
    
    # Step 7: Verify product was updated
    if updated_product['name'] == 'Updated Test Elevator Product':
        print("✅ Product name updated correctly")
    else:
        print("❌ Product name not updated correctly")
    
    # Step 8: Delete test product
    if delete_test_product(token, product_id):
        # Step 9: Verify product was deleted
        final_products = get_manufacturer_products(token)
        if len(final_products) == initial_count:
            print("✅ Product count returned to original")
        else:
            print(f"❌ Product count mismatch after deletion: expected {initial_count}, got {len(final_products)}")
    
    print("\n" + "=" * 50)
    print("🎉 Manufacturer Functionality Test Complete!")
    print("=" * 50)
    
    return True

if __name__ == "__main__":
    test_manufacturer_functionality()
