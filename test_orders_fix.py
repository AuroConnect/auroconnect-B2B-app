#!/usr/bin/env python3
"""
Test Orders Fix
Verify that manufacturer orders are now showing correctly
"""

import requests
import json

BASE_URL = "http://localhost:5000"

def test_orders_fix():
    print("🔧 Testing Orders Fix for Manufacturer")
    print("=" * 50)
    
    # Login as manufacturer
    print("\n1. Logging in as Manufacturer...")
    login_data = {
        "email": "hrushigavhane@gmail.com",
        "password": "password123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
        if response.status_code == 200:
            token = response.json().get('access_token')
            headers = {"Authorization": f"Bearer {token}"}
            print("✅ Manufacturer login successful")
        else:
            print(f"❌ Login failed: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Login error: {e}")
        return
    
    # Test recent orders (dashboard)
    print("\n2. Testing Recent Orders (Dashboard)...")
    try:
        recent_response = requests.get(f"{BASE_URL}/api/orders/recent", headers=headers)
        if recent_response.status_code == 200:
            recent_orders = recent_response.json()
            print(f"✅ Found {len(recent_orders)} recent orders")
            for order in recent_orders:
                print(f"   - Order: {order.get('order_number')} (Status: {order.get('status')}) - ₹{order.get('total_amount')}")
        else:
            print(f"❌ Recent orders failed: {recent_response.status_code}")
    except Exception as e:
        print(f"❌ Recent orders error: {e}")
    
    # Test all orders (orders page)
    print("\n3. Testing All Orders (Orders Page)...")
    try:
        all_orders_response = requests.get(f"{BASE_URL}/api/orders", headers=headers)
        if all_orders_response.status_code == 200:
            all_orders = all_orders_response.json()
            print(f"✅ Found {len(all_orders)} total orders")
            for order in all_orders:
                print(f"   - Order: {order.get('order_number')} (Status: {order.get('status')}) - ₹{order.get('total_amount')}")
        else:
            print(f"❌ All orders failed: {all_orders_response.status_code}")
    except Exception as e:
        print(f"❌ All orders error: {e}")
    
    print("\n🎉 Orders Fix Test Complete!")

if __name__ == "__main__":
    test_orders_fix()
