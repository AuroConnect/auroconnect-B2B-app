#!/usr/bin/env python3
"""
Fix product visibility and 404 issues
"""

import requests
import json

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

def test_user_login():
    """Test login for Hrushi"""
    login_data = {
        "email": "hrushiEaisehome@gmail.com",
        "password": "password123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
        if response.status_code == 200:
            token = response.json().get('access_token')
            user_data = response.json().get('user', {})
            print(f"✅ Login successful for {user_data.get('name', 'Unknown')} ({user_data.get('role', 'Unknown')})")
            return token, user_data
        else:
            print(f"❌ Login failed: {response.status_code}")
            return None, None
    except Exception as e:
        print(f"❌ Login error: {e}")
        return None, None

def test_products_endpoint(token):
    """Test products endpoint"""
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{BASE_URL}/api/products/", headers=headers)
        print(f"\n📊 Products endpoint: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            products = data.get('data', {}).get('products', [])
            total = data.get('data', {}).get('pagination', {}).get('total', 0)
            print(f"✅ Found {len(products)} products (total: {total})")
            
            if products:
                print("📝 Sample products:")
                for i, product in enumerate(products[:3]):
                    print(f"  {i+1}. {product.get('name')} - {product.get('sku')} - ${product.get('price')}")
            else:
                print("❌ No products found")
            
            return products
        else:
            print(f"❌ Products failed: {response.text}")
            return []
    except Exception as e:
        print(f"❌ Products error: {e}")
        return []

def test_analytics_endpoint(token):
    """Test analytics endpoint"""
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{BASE_URL}/api/analytics/stats", headers=headers)
        print(f"\n📊 Analytics endpoint: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Analytics data: {json.dumps(data, indent=2)}")
            return data
        else:
            print(f"❌ Analytics failed: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Analytics error: {e}")
        return None

def test_product_creation(token):
    """Test product creation"""
    headers = {"Authorization": f"Bearer {token}"}
    
    product_data = {
        "name": "Test Laptop",
        "sku": "TEST-LAPTOP-001",
        "basePrice": 999.99,
        "category": "Electronics",
        "description": "Test laptop for debugging",
        "imageUrl": "https://example.com/test-laptop.jpg"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/products/", json=product_data, headers=headers)
        print(f"\n📝 Product creation: {response.status_code}")
        
        if response.status_code == 201:
            print("✅ Product created successfully!")
            return True
        else:
            print(f"❌ Product creation failed: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Product creation error: {e}")
        return False

def test_routing_issues():
    """Test common routing issues"""
    endpoints_to_test = [
        "/api/health",
        "/api/auth/login",
        "/api/products/",
        "/api/analytics/stats",
        "/api/partners/",
        "/api/orders/",
        "/api/products/categories"
    ]
    
    print("\n🔍 Testing routing issues:")
    for endpoint in endpoints_to_test:
        try:
            response = requests.get(f"{BASE_URL}{endpoint}")
            print(f"  {endpoint}: {response.status_code}")
        except Exception as e:
            print(f"  {endpoint}: ERROR - {e}")

def main():
    """Main diagnostic function"""
    print("🔍 Diagnosing Product Visibility and 404 Issues")
    print("=" * 60)
    
    # Step 1: Test backend health
    if not test_backend_health():
        print("❌ Backend is not running. Please start with: docker-compose up -d")
        return
    
    # Step 2: Test routing issues
    test_routing_issues()
    
    # Step 3: Test user login
    token, user_data = test_user_login()
    if not token:
        print("❌ Cannot proceed without authentication")
        return
    
    # Step 4: Test analytics (this shows the 7 products count)
    analytics_data = test_analytics_endpoint(token)
    
    # Step 5: Test products endpoint (this should show the same products)
    products = test_products_endpoint(token)
    
    # Step 6: Test product creation
    creation_success = test_product_creation(token)
    
    # Analysis
    print("\n" + "=" * 60)
    print("📊 ANALYSIS:")
    
    if analytics_data:
        products_count = analytics_data.get('productsCount', 0)
        print(f"  • Analytics shows {products_count} products")
    
    print(f"  • Products endpoint shows {len(products)} products")
    
    if len(products) == 0 and analytics_data and analytics_data.get('productsCount', 0) > 0:
        print("  ❌ ISSUE: Analytics shows products but Products endpoint doesn't!")
        print("  🔧 This suggests a filtering or data access issue.")
    elif len(products) > 0:
        print("  ✅ Products are visible in both endpoints")
    
    if creation_success:
        print("  ✅ Product creation is working")
    else:
        print("  ❌ Product creation has issues")
    
    print("\n🔧 RECOMMENDATIONS:")
    print("1. Check if products are being created with correct user_id")
    print("2. Verify database connections and data integrity")
    print("3. Check if there are any partnership filters affecting visibility")
    print("4. Ensure the frontend is calling the correct endpoints")

if __name__ == "__main__":
    main()
