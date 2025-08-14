#!/usr/bin/env python3
"""
Test Frontend Manufacturer Experience
Tests that the frontend properly shows manufacturer functionality
"""
import requests
import json

# Configuration
FRONTEND_URL = "http://localhost:3000"
BACKEND_URL = "http://localhost:5000"

def test_frontend_accessibility():
    """Test if frontend is accessible"""
    print("🌐 Testing Frontend Accessibility")
    print("=" * 40)
    
    try:
        response = requests.get(FRONTEND_URL, timeout=5)
        if response.status_code == 200:
            print("✅ Frontend is accessible")
            return True
        else:
            print(f"❌ Frontend returned status code: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Frontend not accessible: {e}")
        return False

def test_backend_api():
    """Test if backend API is accessible"""
    print("\n🔧 Testing Backend API")
    print("=" * 40)
    
    try:
        response = requests.get(f"{BACKEND_URL}/api/health", timeout=5)
        if response.status_code == 200:
            print("✅ Backend API is accessible")
            return True
        else:
            print(f"❌ Backend API returned status code: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Backend API not accessible: {e}")
        return False

def test_manufacturer_login():
    """Test manufacturer login via API"""
    print("\n🔐 Testing Manufacturer Login")
    print("=" * 40)
    
    login_data = {
        'email': 'm@demo.com',
        'password': 'Demo@123'
    }
    
    try:
        response = requests.post(f"{BACKEND_URL}/api/auth/login", json=login_data, timeout=5)
        if response.status_code == 200:
            data = response.json()
            if 'access_token' in data:
                print("✅ Manufacturer login successful")
                return data['access_token']
            else:
                print("❌ No access token in response")
                return None
        else:
            print(f"❌ Login failed with status code: {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"❌ Login request failed: {e}")
        return None

def test_manufacturer_products(token):
    """Test manufacturer products API"""
    print("\n📦 Testing Manufacturer Products API")
    print("=" * 40)
    
    headers = {'Authorization': f'Bearer {token}'}
    
    try:
        response = requests.get(f"{BACKEND_URL}/api/products", headers=headers, timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Found {len(data)} products for manufacturer")
            
            # Check if products have manufacturer-specific fields
            if data:
                product = data[0]
                if 'manufacturerId' in product:
                    print("✅ Products have manufacturer ID")
                if 'basePrice' in product:
                    print("✅ Products have base price")
                if 'sku' in product:
                    print("✅ Products have SKU")
                    
            return data
        else:
            print(f"❌ Products API failed with status code: {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"❌ Products request failed: {e}")
        return None

def test_categories_api():
    """Test categories API"""
    print("\n📂 Testing Categories API")
    print("=" * 40)
    
    try:
        response = requests.get(f"{BACKEND_URL}/api/products/categories", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Found {len(data)} categories")
            return data
        else:
            print(f"❌ Categories API failed with status code: {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"❌ Categories request failed: {e}")
        return None

def main():
    """Main test function"""
    print("🚀 Testing Frontend Manufacturer Experience")
    print("=" * 50)
    
    # Test 1: Frontend accessibility
    if not test_frontend_accessibility():
        print("❌ Frontend test failed - cannot proceed")
        return False
    
    # Test 2: Backend API accessibility
    if not test_backend_api():
        print("❌ Backend API test failed - cannot proceed")
        return False
    
    # Test 3: Manufacturer login
    token = test_manufacturer_login()
    if not token:
        print("❌ Manufacturer login test failed - cannot proceed")
        return False
    
    # Test 4: Categories API
    categories = test_categories_api()
    if not categories:
        print("❌ Categories API test failed")
        return False
    
    # Test 5: Manufacturer products
    products = test_manufacturer_products(token)
    if not products:
        print("❌ Manufacturer products test failed")
        return False
    
    print("\n" + "=" * 50)
    print("🎉 Frontend Manufacturer Experience Test Complete!")
    print("=" * 50)
    print("\n📋 Summary:")
    print(f"  ✅ Frontend accessible at: {FRONTEND_URL}")
    print(f"  ✅ Backend API accessible at: {BACKEND_URL}")
    print(f"  ✅ Manufacturer login working")
    print(f"  ✅ Found {len(categories)} categories")
    print(f"  ✅ Found {len(products)} manufacturer products")
    print("\n🌐 To test the UI:")
    print(f"  1. Open {FRONTEND_URL} in your browser")
    print("  2. Login with manufacturer credentials:")
    print("     Email: m@demo.com")
    print("     Password: Demo@123")
    print("  3. Navigate to Products page")
    print("  4. Test Add Product and Edit Product functionality")
    
    return True

if __name__ == "__main__":
    main()
