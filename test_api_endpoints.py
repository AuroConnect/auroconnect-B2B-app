#!/usr/bin/env python3
"""
Test script to verify API endpoints are working
"""
import requests
import json

BASE_URL = "http://localhost:5000"

def test_api_endpoint(url, token=None):
    """Test API endpoint"""
    print(f"Testing {url}...")
    
    headers = {}
    if token:
        headers['Authorization'] = f'Bearer {token}'
    
    try:
        response = requests.get(f"{BASE_URL}{url}", headers=headers)
        
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            print(f"Response: {response.json()}")
            print(f"Success for {url}!")
            return response.json() if response.content else None
        else:
            print(f"Failed for {url}!")
            if response.content:
                print(f"Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"Error for {url}: {e}")
        return None

def main():
    """Main test function"""
    print("Testing API Endpoints")
    print("=" * 40)
    
    # Test public endpoints first
    test_api_endpoint("/api/health")
    
    # Test auth endpoints
    print("\n1. Testing Auth Endpoints")
    register_data = {
        "firstName": "Test",
        "lastName": "User",
        "email": "test_api@test.com",
        "password": "testpassword123",
        "role": "retailer"
    }
    
    # Register a new user
    try:
        response = requests.post(f"{BASE_URL}/api/auth/register", json=register_data)
        print(f"Register Status Code: {response.status_code}")
        if response.status_code == 201:
            print("Registration successful!")
            user_data = response.json()
            print(f"User: {user_data}")
        else:
            print("Registration failed!")
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"Registration error: {e}")
    
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
    except Exception as e:
        print(f"Login error: {e}")
    
    # Test protected endpoints with token
    if token:
        print("\n2. Testing Protected API Endpoints")
        test_api_endpoint("/api/auth/user", token)
        test_api_endpoint("/api/analytics/stats", token)
        test_api_endpoint("/api/notifications/", token)
        test_api_endpoint("/api/whatsapp/notifications", token)
        test_api_endpoint("/api/favorites/", token)

if __name__ == "__main__":
    main()