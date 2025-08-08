#!/usr/bin/env python3
"""
Test products fix with correct response format
"""

import requests
import json

BASE_URL = "http://localhost:5000"

def test_products_visibility():
    """Test if products are now visible"""
    
    # Login
    login_data = {
        "email": "hrushiEaisehome@gmail.com",
        "password": "password123"
    }
    
    try:
        # Login
        response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
        if response.status_code != 200:
            print(f"❌ Login failed: {response.status_code}")
            return False
        
        token = response.json().get('access_token')
        headers = {"Authorization": f"Bearer {token}"}
        
        # Test products endpoint
        response = requests.get(f"{BASE_URL}/api/products/", headers=headers)
        print(f"📊 Products endpoint: {response.status_code}")
        
        if response.status_code == 200:
            products = response.json()
            print(f"✅ Found {len(products)} products")
            
            if products:
                print("📝 Sample products:")
                for i, product in enumerate(products[:3]):
                    print(f"  {i+1}. {product.get('name')} - {product.get('sku')} - ${product.get('price')}")
            else:
                print("❌ No products found")
            
            return len(products) > 0
        else:
            print(f"❌ Products failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_categories_endpoint():
    """Test categories endpoint"""
    login_data = {
        "email": "hrushiEaisehome@gmail.com",
        "password": "password123"
    }
    
    try:
        # Login
        response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
        if response.status_code != 200:
            print(f"❌ Login failed: {response.status_code}")
            return False
        
        token = response.json().get('access_token')
        headers = {"Authorization": f"Bearer {token}"}
        
        # Test categories endpoint
        response = requests.get(f"{BASE_URL}/api/products/categories", headers=headers)
        print(f"\n📊 Categories endpoint: {response.status_code}")
        
        if response.status_code == 200:
            categories = response.json()
            print(f"✅ Found {len(categories)} categories: {categories}")
            return True
        else:
            print(f"❌ Categories failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_frontend_compatibility():
    """Test if the response format is compatible with frontend"""
    login_data = {
        "email": "hrushiEaisehome@gmail.com",
        "password": "password123"
    }
    
    try:
        # Login
        response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
        if response.status_code != 200:
            print(f"❌ Login failed: {response.status_code}")
            return False
        
        token = response.json().get('access_token')
        headers = {"Authorization": f"Bearer {token}"}
        
        # Test products endpoint
        response = requests.get(f"{BASE_URL}/api/products/", headers=headers)
        
        if response.status_code == 200:
            products = response.json()
            
            # Check if it's an array (frontend expects this)
            if isinstance(products, list):
                print("✅ Response format is compatible with frontend (array)")
                
                # Check if products have required fields
                if products:
                    sample_product = products[0]
                    required_fields = ['id', 'name', 'sku', 'price']
                    missing_fields = [field for field in required_fields if field not in sample_product]
                    
                    if missing_fields:
                        print(f"❌ Missing required fields: {missing_fields}")
                        return False
                    else:
                        print("✅ Products have all required fields")
                        return True
                else:
                    print("⚠️ No products found, but format is correct")
                    return True
            else:
                print("❌ Response format is not compatible (not an array)")
                return False
        else:
            print(f"❌ Products endpoint failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("🔍 Testing Products Fix")
    print("=" * 40)
    
    # Test 1: Products visibility
    products_visible = test_products_visibility()
    
    # Test 2: Categories endpoint
    categories_working = test_categories_endpoint()
    
    # Test 3: Frontend compatibility
    frontend_compatible = test_frontend_compatibility()
    
    print("\n" + "=" * 40)
    print("📊 RESULTS:")
    print(f"  • Products visible: {'✅' if products_visible else '❌'}")
    print(f"  • Categories working: {'✅' if categories_working else '❌'}")
    print(f"  • Frontend compatible: {'✅' if frontend_compatible else '❌'}")
    
    if products_visible and categories_working and frontend_compatible:
        print("\n✅ All tests passed! Products should now be visible in the frontend.")
        print("🌐 Try refreshing the Products page in your browser.")
    else:
        print("\n❌ Some tests failed. Check the details above.")
