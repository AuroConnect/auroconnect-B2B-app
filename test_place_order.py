#!/usr/bin/env python3
"""
Simple test to debug place order 500 error
"""
import requests
import json

BASE_URL = "http://localhost:5000"
API_BASE = f"{BASE_URL}/api"

def test_place_order():
    # Login
    login_data = {
        "email": "r@demo.com",
        "password": "Demo@123"
    }
    
    response = requests.post(f"{API_BASE}/auth/login", json=login_data)
    if response.status_code != 200:
        print(f"Login failed: {response.text}")
        return
    
    token = response.json().get('access_token')
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    # Get products
    response = requests.get(f"{API_BASE}/products/", headers=headers)
    if response.status_code != 200:
        print(f"Get products failed: {response.text}")
        return
    
    products = response.json()
    if not products:
        print("No products available")
        return
    
    first_product = products[0]
    print(f"Using product: {first_product.get('name')} - ID: {first_product.get('id')}")
    
    # Test place order with minimal data
    order_data = {
        "cart_items": [
            {
                "product_id": first_product.get('id'),
                "quantity": 1
            }
        ],
        "delivery_option": "DELIVER_TO_BUYER",
        "notes": "Test order"
    }
    
    print(f"Order data: {json.dumps(order_data, indent=2)}")
    
    response = requests.post(f"{API_BASE}/orders/", headers=headers, json=order_data)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")

if __name__ == "__main__":
    test_place_order()
