#!/usr/bin/env python3
"""
Test Backend APIs Script
Tests the APIs that are returning 500 errors
"""

import requests
import json

# API Base URL
API_BASE_URL = 'http://localhost:5000'

def test_api_endpoint(endpoint, method='GET', data=None, token=None):
    """Test a specific API endpoint"""
    url = f"{API_BASE_URL}{endpoint}"
    headers = {}
    
    if token:
        headers['Authorization'] = f'Bearer {token}'
    
    if data and method in ['POST', 'PUT']:
        headers['Content-Type'] = 'application/json'
    
    try:
        if method == 'GET':
            response = requests.get(url, headers=headers)
        elif method == 'POST':
            response = requests.post(url, headers=headers, json=data)
        else:
            response = requests.request(method, url, headers=headers, json=data)
        
        print(f"🔍 Testing {method} {endpoint}")
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            print(f"   ✅ Success")
            try:
                data = response.json()
                print(f"   Data: {json.dumps(data, indent=2)[:200]}...")
            except:
                print(f"   Response: {response.text[:200]}...")
        elif response.status_code == 401:
            print(f"   ❌ Unauthorized - Need valid token")
        elif response.status_code == 404:
            print(f"   ❌ Not Found - Endpoint doesn't exist")
        elif response.status_code == 500:
            print(f"   ❌ Server Error")
            try:
                error_data = response.json()
                print(f"   Error: {json.dumps(error_data, indent=2)}")
            except:
                print(f"   Error: {response.text}")
        else:
            print(f"   ❌ Unexpected status: {response.status_code}")
            print(f"   Response: {response.text[:200]}...")
        
        print()
        return response
        
    except requests.exceptions.ConnectionError:
        print(f"🔍 Testing {method} {endpoint}")
        print(f"   ❌ Connection Error - Backend not running")
        print()
        return None
    except Exception as e:
        print(f"🔍 Testing {method} {endpoint}")
        print(f"   ❌ Error: {str(e)}")
        print()
        return None

def login_and_get_token():
    """Login and get auth token"""
    print("🔐 Logging in to get auth token...")
    
    # Try to login with existing user
    login_data = {
        "email": "hrushigavhane@gmail.com",
        "password": "password123"
    }
    
    response = requests.post(f"{API_BASE_URL}/api/auth/login", json=login_data)
    
    if response.status_code == 200:
        data = response.json()
        token = data.get('access_token')
        print(f"✅ Login successful, got token: {token[:20]}...")
        return token
    else:
        print(f"❌ Login failed: {response.status_code}")
        print(f"Response: {response.text}")
        return None

def main():
    """Main test function"""
    print("🧪 Backend API Test Script")
    print("=" * 50)
    
    # Test health endpoint first
    print("1. Testing health endpoint...")
    test_api_endpoint('/api/health')
    
    # Login to get token
    token = login_and_get_token()
    
    if not token:
        print("❌ Cannot proceed without auth token")
        return
    
    print("\n2. Testing authenticated endpoints...")
    
    # Test the endpoints that are returning 500 errors
    endpoints_to_test = [
        '/api/orders/recent',
        '/api/notifications/',
        '/api/analytics/stats',
        '/api/orders/',
        '/api/whatsapp/notifications',
        '/api/cart/',
        '/api/auth/user'
    ]
    
    for endpoint in endpoints_to_test:
        test_api_endpoint(endpoint, token=token)
    
    print("✅ API testing completed!")

if __name__ == "__main__":
    main()
