#!/usr/bin/env python3
"""
Simple test script to verify API endpoints are working
"""

import requests
import json

BASE_URL = "http://localhost:5000"

def test_health():
    """Test health endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/api/health")
        print(f"Health check: {response.status_code}")
        if response.status_code == 200:
            print("✅ Health check passed")
            return True
        else:
            print("❌ Health check failed")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def test_registration():
    """Test user registration"""
    try:
        data = {
            "firstName": "Test",
            "lastName": "User",
            "email": "test@example.com",
            "password": "password123",
            "role": "retailer",
            "businessName": "Test Business"
        }
        
        response = requests.post(f"{BASE_URL}/api/auth/register", json=data)
        print(f"Registration: {response.status_code}")
        
        if response.status_code in [201, 409]:  # 409 means user already exists
            print("✅ Registration endpoint working")
            return True
        else:
            print(f"❌ Registration failed: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Registration error: {e}")
        return False

def test_login():
    """Test user login"""
    try:
        data = {
            "email": "test@example.com",
            "password": "password123"
        }
        
        response = requests.post(f"{BASE_URL}/api/auth/login", json=data)
        print(f"Login: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            if "access_token" in result:
                print("✅ Login successful")
                return result["access_token"]
            else:
                print("❌ Login failed: No token received")
                return None
        else:
            print(f"❌ Login failed: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Login error: {e}")
        return None

def test_user_info(token):
    """Test getting user info with token"""
    if not token:
        print("❌ No token available for user info test")
        return False
    
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BASE_URL}/api/auth/user", headers=headers)
        print(f"User info: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ User info endpoint working")
            return True
        else:
            print(f"❌ User info failed: {response.text}")
            return False
    except Exception as e:
        print(f"❌ User info error: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing AuroMart API...")
    print("=" * 50)
    
    # Test health
    if not test_health():
        print("❌ Health check failed, stopping tests")
        return
    
    # Test registration
    test_registration()
    
    # Test login
    token = test_login()
    
    # Test user info if login was successful
    if token:
        test_user_info(token)
    
    print("=" * 50)
    print("✅ API tests completed")

if __name__ == "__main__":
    main()
