#!/usr/bin/env python3
"""
Debug product creation issue
"""

import requests
import json

# Configuration
BASE_URL = "http://localhost:5000"

def test_backend_health():
    """Test if backend is running"""
    try:
        response = requests.get(f"{BASE_URL}/api/health")
        print(f"✅ Backend health: {response.status_code}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Backend not accessible: {e}")
        return False

def test_login():
    """Test login for Hrushi"""
    login_data = {
        "email": "hrushiEaisehome@gmail.com",
        "password": "password123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
        if response.status_code == 200:
            token = response.json().get('access_token')
            print(f"✅ Login successful, token: {token[:20]}...")
            return token
        else:
            print(f"❌ Login failed: {response.status_code}")
            print(f"Response: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Login error: {e}")
        return None

def test_product_creation(token):
    """Test product creation with detailed error handling"""
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test product data
    product_data = {
        "name": "Test Laptop",
        "sku": "TEST-LAPTOP-001",
        "basePrice": 999.99,
        "category": "Electronics",
        "description": "Test laptop for debugging",
        "imageUrl": "https://example.com/test-laptop.jpg"
    }
    
    print(f"\n📝 Testing product creation with data:")
    print(json.dumps(product_data, indent=2))
    
    try:
        response = requests.post(f"{BASE_URL}/api/products/", json=product_data, headers=headers)
        print(f"\n📊 Response Status: {response.status_code}")
        print(f"📊 Response Headers: {dict(response.headers)}")
        
        if response.status_code == 201:
            print("✅ Product created successfully!")
            print(f"Response: {response.text}")
            return True
        else:
            print(f"❌ Product creation failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Product creation error: {e}")
        return False

def test_categories_endpoint(token):
    """Test categories endpoint"""
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{BASE_URL}/api/products/categories", headers=headers)
        print(f"\n📊 Categories endpoint: {response.status_code}")
        if response.status_code == 200:
            categories = response.json()
            print(f"✅ Categories: {categories}")
        else:
            print(f"❌ Categories failed: {response.text}")
    except Exception as e:
        print(f"❌ Categories error: {e}")

def test_products_endpoint(token):
    """Test products endpoint"""
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{BASE_URL}/api/products/", headers=headers)
        print(f"\n📊 Products endpoint: {response.status_code}")
        if response.status_code == 200:
            products = response.json()
            print(f"✅ Products count: {len(products.get('data', {}).get('products', []))}")
        else:
            print(f"❌ Products failed: {response.text}")
    except Exception as e:
        print(f"❌ Products error: {e}")

def main():
    """Debug product creation"""
    print("🔍 Debugging Product Creation Issue")
    print("=" * 50)
    
    # Step 1: Test backend health
    if not test_backend_health():
        print("❌ Backend is not running. Please start with: docker-compose up -d")
        return
    
    # Step 2: Test login
    token = test_login()
    if not token:
        print("❌ Cannot proceed without authentication")
        return
    
    # Step 3: Test categories endpoint
    test_categories_endpoint(token)
    
    # Step 4: Test products endpoint
    test_products_endpoint(token)
    
    # Step 5: Test product creation
    success = test_product_creation(token)
    
    if success:
        print("\n✅ Product creation is working!")
    else:
        print("\n❌ Product creation is failing. Check the error details above.")
        print("\n🔧 Possible fixes:")
        print("1. Check database connection")
        print("2. Check database schema")
        print("3. Check backend logs: docker-compose logs backend")

if __name__ == "__main__":
    main()
