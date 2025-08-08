#!/usr/bin/env python3
"""
Test script to verify orders endpoint is working
"""
import requests
import json

BASE_URL = "http://localhost:5000"

def test_orders_endpoint(token):
    """Test orders endpoint"""
    print("Testing /api/orders/ endpoint...")
    
    headers = {
        'Authorization': f'Bearer {token}'
    }
    
    try:
        response = requests.get(f"{BASE_URL}/api/orders/", headers=headers)
        
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            print(f"Response: {response.json()}")
            print("Success for /api/orders/!")
            return True
        else:
            print(f"Failed for /api/orders/!")
            if response.content:
                print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"Error for /api/orders/: {e}")
        return False

def main():
    """Main test function"""
    print("Testing Orders Endpoint")
    print("=" * 40)
    
    # Login to get token
    login_data = {
        "email": "test_api@test.com",
        "password": "testpassword123"
    }
    
    token = None
    try:
        response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
        print(f"Login Status Code: {response.status_code}")
        if response.status_code == 200:
            login_result = response.json()
            token = login_result.get('access_token')
            print(f"Login successful! Token: {token[:20]}...")
        else:
            print("Login failed!")
            print(f"Response: {response.text}")
            return
    except Exception as e:
        print(f"Login error: {e}")
        return
    
    # Test orders endpoint with token
    if token:
        test_orders_endpoint(token)

if __name__ == "__main__":
    main()