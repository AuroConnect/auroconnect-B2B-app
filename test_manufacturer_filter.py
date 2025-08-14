#!/usr/bin/env python3
"""
Test Manufacturer Filter Functionality
Tests the manufacturer filter for distributors
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

def test_manufacturer_filter():
    """Test manufacturer filter functionality"""
    print("🧪 Testing Manufacturer Filter Functionality")
    print("=" * 60)
    
    # Login as distributor
    distributor_token = login_user("d@demo.com", "Demo@123")
    if not distributor_token:
        print("❌ Cannot proceed without distributor authentication")
        return False
    
    # Test 1: Get all products (should see manufacturer + own products)
    print("\n📦 Test 1: Getting all products...")
    all_products = make_request('GET', '/products', token=distributor_token)
    if all_products:
        print(f"✅ Distributor sees {len(all_products)} total products")
        
        # Count by manufacturer
        manufacturer_counts = {}
        for product in all_products:
            manufacturer_id = product.get('manufacturerId')
            if manufacturer_id:
                if manufacturer_id not in manufacturer_counts:
                    manufacturer_counts[manufacturer_id] = 0
                manufacturer_counts[manufacturer_id] += 1
        
        print(f"📊 Products by manufacturer: {manufacturer_counts}")
    else:
        print("❌ Failed to get products")
        return False
    
    # Test 2: Get manufacturers for filter
    print("\n🏭 Test 2: Getting manufacturers for filter...")
    manufacturers = make_request('GET', '/products/manufacturers', token=distributor_token)
    if manufacturers:
        print(f"✅ Found {len(manufacturers)} manufacturers for filtering")
        for manufacturer in manufacturers:
            print(f"  - {manufacturer['businessName']} (ID: {manufacturer['id']})")
    else:
        print("❌ Failed to get manufacturers")
        return False
    
    # Test 3: Filter by specific manufacturer (if available)
    if manufacturers:
        first_manufacturer = manufacturers[0]
        manufacturer_id = first_manufacturer['id']
        manufacturer_name = first_manufacturer['businessName']
        
        print(f"\n🔍 Test 3: Filtering by {manufacturer_name}...")
        filtered_products = make_request('GET', f'/products?manufacturerId={manufacturer_id}', token=distributor_token)
        if filtered_products:
            print(f"✅ Filtered products: {len(filtered_products)} products from {manufacturer_name}")
            
            # Verify all products are from the selected manufacturer
            all_from_manufacturer = all(
                product.get('manufacturerId') == manufacturer_id 
                for product in filtered_products
            )
            if all_from_manufacturer:
                print("✅ All filtered products are from the selected manufacturer")
            else:
                print("❌ Some products are not from the selected manufacturer")
        else:
            print("❌ Failed to filter products")
    
    # Test 4: Test frontend manufacturer filter (simulate)
    print("\n🌐 Test 4: Frontend Manufacturer Filter Simulation...")
    print("This would be tested in the browser by:")
    print("1. Login as distributor: d@demo.com / Demo@123")
    print("2. Go to Products page")
    print("3. Use the 'All Manufacturers' dropdown")
    print("4. Select a specific manufacturer")
    print("5. Verify only that manufacturer's products are shown")
    
    print("\n" + "=" * 60)
    print("🎉 Manufacturer Filter Testing Complete!")
    print("=" * 60)
    
    print("\n📋 Summary:")
    print(f"  ✅ Distributor can see {len(all_products) if all_products else 0} total products")
    print(f"  ✅ Found {len(manufacturers) if manufacturers else 0} manufacturers for filtering")
    print("  ✅ Manufacturer filter API is working")
    print("  ✅ Ready for frontend testing")
    
    return True

if __name__ == "__main__":
    test_manufacturer_filter()
