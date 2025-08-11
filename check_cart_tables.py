#!/usr/bin/env python3
"""
Check Cart Tables and API
"""

import pymysql
import requests
import json

# Database configuration
DB_CONFIG = {
    'host': '3.249.132.231',
    'port': 3306,
    'user': 'admin',
    'password': '123@Hrushi',
    'database': 'wa',
    'charset': 'utf8mb4'
}

def check_database_tables():
    """Check if cart tables exist in database"""
    try:
        connection = pymysql.connect(**DB_CONFIG)
        cursor = connection.cursor()
        
        print("🔍 Checking database tables...")
        
        # Check if carts table exists
        cursor.execute("SHOW TABLES LIKE 'carts'")
        carts_exists = cursor.fetchone()
        print(f"✅ Carts table exists: {carts_exists is not None}")
        
        # Check if cart_items table exists
        cursor.execute("SHOW TABLES LIKE 'cart_items'")
        cart_items_exists = cursor.fetchone()
        print(f"✅ Cart items table exists: {cart_items_exists is not None}")
        
        if carts_exists:
            # Check carts table structure
            cursor.execute("DESCRIBE carts")
            carts_structure = cursor.fetchall()
            print(f"📋 Carts table structure:")
            for row in carts_structure:
                print(f"   {row[0]} - {row[1]} - {row[2]} - {row[3]} - {row[4]} - {row[5]}")
        
        if cart_items_exists:
            # Check cart_items table structure
            cursor.execute("DESCRIBE cart_items")
            cart_items_structure = cursor.fetchall()
            print(f"📋 Cart items table structure:")
            for row in cart_items_structure:
                print(f"   {row[0]} - {row[1]} - {row[2]} - {row[3]} - {row[4]} - {row[5]}")
        
        # Check for any cart data
        if carts_exists:
            cursor.execute("SELECT COUNT(*) FROM carts")
            carts_count = cursor.fetchone()[0]
            print(f"📊 Carts count: {carts_count}")
        
        if cart_items_exists:
            cursor.execute("SELECT COUNT(*) FROM cart_items")
            cart_items_count = cursor.fetchone()[0]
            print(f"📊 Cart items count: {cart_items_count}")
        
        cursor.close()
        connection.close()
        
    except Exception as e:
        print(f"❌ Database error: {e}")

def test_cart_api():
    """Test cart API endpoints"""
    try:
        print("\n🧪 Testing Cart API...")
        
        # Login to get token
        login_data = {
            "email": "retailer1@test.com",
            "password": "password123"
        }
        
        response = requests.post("http://localhost:5000/api/auth/login", json=login_data, timeout=10)
        if response.status_code == 200:
            token = response.json().get('access_token')
            print("✅ Login successful")
            
            headers = {"Authorization": f"Bearer {token}"}
            
            # Test GET /api/cart/
            print("\n📋 Testing GET /api/cart/...")
            response = requests.get("http://localhost:5000/api/cart/", headers=headers, timeout=10)
            print(f"   Status: {response.status_code}")
            if response.status_code != 200:
                print(f"   Response: {response.text}")
            else:
                cart_data = response.json()
                print(f"   Cart data: {json.dumps(cart_data, indent=2)}")
            
            # Test POST /api/cart/add
            print("\n➕ Testing POST /api/cart/add...")
            add_data = {
                "productId": "test-product-id",
                "quantity": 1
            }
            response = requests.post("http://localhost:5000/api/cart/add", json=add_data, headers=headers, timeout=10)
            print(f"   Status: {response.status_code}")
            if response.status_code != 200:
                print(f"   Response: {response.text}")
            
        else:
            print(f"❌ Login failed: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"❌ API test error: {e}")

if __name__ == "__main__":
    check_database_tables()
    test_cart_api()
