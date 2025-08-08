#!/usr/bin/env python3
"""
Test database connection and schema
"""

import requests
import json

# Configuration
BASE_URL = "http://localhost:5000"

def test_database_health():
    """Test database health through backend"""
    try:
        response = requests.get(f"{BASE_URL}/api/health")
        print(f"✅ Backend health: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Database status: {data.get('database', 'Unknown')}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Backend not accessible: {e}")
        return False

def test_product_creation_with_minimal_data():
    """Test product creation with minimal required data"""
    # First login
    login_data = {
        "email": "hrushiEaisehome@gmail.com",
        "password": "password123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
        if response.status_code != 200:
            print(f"❌ Login failed: {response.status_code}")
            return False
        
        token = response.json().get('access_token')
        headers = {"Authorization": f"Bearer {token}"}
        
        # Test with minimal data
        minimal_product = {
            "name": "Test Product",
            "sku": "TEST-001",
            "basePrice": 100.00
        }
        
        print(f"\n📝 Testing with minimal data:")
        print(json.dumps(minimal_product, indent=2))
        
        response = requests.post(f"{BASE_URL}/api/products/", json=minimal_product, headers=headers)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 201:
            print("✅ Product created successfully!")
            return True
        else:
            print(f"❌ Product creation failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_product_creation_with_full_data():
    """Test product creation with full data"""
    # First login
    login_data = {
        "email": "hrushiEaisehome@gmail.com",
        "password": "password123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
        if response.status_code != 200:
            print(f"❌ Login failed: {response.status_code}")
            return False
        
        token = response.json().get('access_token')
        headers = {"Authorization": f"Bearer {token}"}
        
        # Test with full data (like in the image)
        full_product = {
            "name": "Laptop",
            "sku": "2332",
            "category": "Electronics",
            "description": "sdasdasd",
            "basePrice": 100,
            "imageUrl": "https://example.com/image.jpg"
        }
        
        print(f"\n📝 Testing with full data (like in image):")
        print(json.dumps(full_product, indent=2))
        
        response = requests.post(f"{BASE_URL}/api/products/", json=full_product, headers=headers)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 201:
            print("✅ Product created successfully!")
            return True
        else:
            print(f"❌ Product creation failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_existing_products():
    """Test getting existing products"""
    login_data = {
        "email": "hrushiEaisehome@gmail.com",
        "password": "password123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
        if response.status_code != 200:
            print(f"❌ Login failed: {response.status_code}")
            return False
        
        token = response.json().get('access_token')
        headers = {"Authorization": f"Bearer {token}"}
        
        response = requests.get(f"{BASE_URL}/api/products/", headers=headers)
        print(f"\n📊 Existing products status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            products = data.get('data', {}).get('products', [])
            print(f"✅ Found {len(products)} existing products")
            return True
        else:
            print(f"❌ Failed to get products: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Test database and product creation"""
    print("🔍 Testing Database Connection and Product Creation")
    print("=" * 60)
    
    # Test 1: Backend health
    if not test_database_health():
        print("❌ Backend is not healthy")
        return
    
    # Test 2: Existing products
    test_existing_products()
    
    # Test 3: Minimal product creation
    print("\n" + "=" * 40)
    print("Testing Minimal Product Creation")
    minimal_success = test_product_creation_with_minimal_data()
    
    # Test 4: Full product creation
    print("\n" + "=" * 40)
    print("Testing Full Product Creation")
    full_success = test_product_creation_with_full_data()
    
    print("\n" + "=" * 60)
    if minimal_success and full_success:
        print("✅ All tests passed! Product creation is working.")
    else:
        print("❌ Some tests failed. Check the error details above.")
        print("\n🔧 Troubleshooting:")
        print("1. Check database connection")
        print("2. Check database schema")
        print("3. Check backend logs: docker-compose logs backend")
        print("4. Restart containers: docker-compose restart")

if __name__ == "__main__":
    main()
