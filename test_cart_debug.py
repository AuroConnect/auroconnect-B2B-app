#!/usr/bin/env python3
"""
Debug script to test cart functionality
"""

import requests
import json

BASE_URL = "http://localhost:5000"

def test_cart():
    print("🔍 Testing Cart API step by step...")
    
    # Step 1: Login
    print("\n1. Logging in...")
    login_data = {
        "email": "m@demo.com",
        "password": "Demo@123"
    }
    
    login_response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
    print(f"   Login Status: {login_response.status_code}")
    
    if login_response.status_code != 200:
        print(f"   Login failed: {login_response.text}")
        return
    
    token = login_response.json()['access_token']
    print(f"   Token received: {token[:20]}...")
    
    # Step 2: Test GET cart
    print("\n2. Testing GET /api/cart...")
    headers = {"Authorization": f"Bearer {token}"}
    
    get_cart_response = requests.get(f"{BASE_URL}/api/cart", headers=headers)
    print(f"   GET Cart Status: {get_cart_response.status_code}")
    print(f"   GET Cart Response: {get_cart_response.text}")
    
    # Step 3: Test POST cart without trailing slash
    print("\n3. Testing POST /api/cart (no trailing slash)...")
    cart_data = {
        "productId": "a592053e-8bc8-4482-8769-1ee8caeb737d",
        "quantity": 1
    }
    
    post_cart_response = requests.post(f"{BASE_URL}/api/cart", headers=headers, json=cart_data)
    print(f"   POST Cart Status: {post_cart_response.status_code}")
    print(f"   POST Cart Response: {post_cart_response.text}")
    
    # Step 4: Test POST cart with trailing slash
    print("\n4. Testing POST /api/cart/ (with trailing slash)...")
    post_cart_slash_response = requests.post(f"{BASE_URL}/api/cart/", headers=headers, json=cart_data)
    print(f"   POST Cart/ Status: {post_cart_slash_response.status_code}")
    print(f"   POST Cart/ Response: {post_cart_slash_response.text}")
    
    # Step 5: Test OPTIONS cart
    print("\n5. Testing OPTIONS /api/cart...")
    options_response = requests.options(f"{BASE_URL}/api/cart", headers=headers)
    print(f"   OPTIONS Status: {options_response.status_code}")
    print(f"   OPTIONS Headers: {dict(options_response.headers)}")

if __name__ == "__main__":
    test_cart()
