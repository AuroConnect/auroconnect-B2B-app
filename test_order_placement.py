#!/usr/bin/env python3
"""
Test script for order placement functionality
"""

import requests
import json
import time

BASE_URL = "http://localhost:5000/api"

def test_order_placement():
    """Test the complete order placement flow"""
    
    print("🧪 Testing Order Placement Functionality")
    print("=" * 50)
    
    # Test 1: Check if backend is running
    print("\n1. Checking backend status...")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Backend is running")
        else:
            print(f"❌ Backend returned status {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Backend is not accessible: {e}")
        return
    
    # Test 2: Test login to get a valid token
    print("\n2. Testing login...")
    login_data = {
        "email": "retailer@test.com",
        "password": "password123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/login", json=login_data, timeout=10)
        if response.status_code == 200:
            token = response.json().get('access_token')
            print("✅ Login successful")
            print(f"   Token: {token[:20]}...")
        else:
            print(f"❌ Login failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return
    except Exception as e:
        print(f"❌ Login error: {e}")
        return
    
    # Test 3: Test cart API
    print("\n3. Testing cart API...")
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{BASE_URL}/cart", headers=headers, timeout=10)
        if response.status_code == 200:
            cart_data = response.json()
            print("✅ Cart API working")
            print(f"   Cart items: {cart_data.get('totalItems', 0)}")
            print(f"   Total amount: ${cart_data.get('totalAmount', 0):.2f}")
        else:
            print(f"❌ Cart API failed: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Cart API error: {e}")
    
    # Test 4: Test order placement
    print("\n4. Testing order placement...")
    try:
        response = requests.post(f"{BASE_URL}/orders", headers=headers, timeout=10)
        if response.status_code == 201:
            order_data = response.json()
            print("✅ Order placement successful!")
            print(f"   Order ID: {order_data.get('orderId')}")
            print(f"   Order Number: {order_data.get('orderNumber')}")
            print(f"   Total Amount: ${order_data.get('totalAmount', 0):.2f}")
            print(f"   Items Count: {order_data.get('itemsCount', 0)}")
        elif response.status_code == 400:
            error_data = response.json()
            print(f"⚠️  Order placement failed (expected): {error_data.get('message')}")
            if "Cart is empty" in error_data.get('message', ''):
                print("   This is expected if the cart is empty")
        else:
            print(f"❌ Order placement failed: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Order placement error: {e}")
    
    # Test 5: Test orders list
    print("\n5. Testing orders list...")
    try:
        response = requests.get(f"{BASE_URL}/orders", headers=headers, timeout=10)
        if response.status_code == 200:
            orders = response.json()
            print(f"✅ Orders API working")
            print(f"   Total orders: {len(orders)}")
            if orders:
                latest_order = orders[0]
                print(f"   Latest order: {latest_order.get('orderNumber')}")
                print(f"   Status: {latest_order.get('status')}")
        else:
            print(f"❌ Orders API failed: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Orders API error: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 Order placement functionality test completed!")

if __name__ == "__main__":
    test_order_placement()
