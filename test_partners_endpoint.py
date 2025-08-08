#!/usr/bin/env python3
"""
Test script to verify partners endpoint is working
"""
import requests
import json

BASE_URL = "http://localhost:5000"

def test_partners_endpoint(token):
    """Test partners endpoint"""
    print("Testing /api/partners/distributors endpoint...")
    
    headers = {
        'Authorization': f'Bearer {token}'
    }
    
    try:
        response = requests.get(f"{BASE_URL}/api/partners/distributors", headers=headers)
        
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            print(f"Response: {response.json()}")
            print("Success for /api/partners/distributors!")
            return True
        else:
            print(f"Failed for /api/partners/distributors!")
            if response.content:
                print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"Error for /api/partners/distributors: {e}")
        return False

def main():
    """Main test function"""
    print("Testing Partners Endpoint")
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
    
    # Test partners endpoint with token
    if token:
        test_partners_endpoint(token)

if __name__ == "__main__":
    main()