#!/usr/bin/env python3
"""
Test script to verify authentication functionality with MySQL
"""

import requests
import json
import sys

# Configuration
API_BASE_URL = "http://localhost:5000"
TEST_EMAIL = "testuser@example.com"
TEST_PASSWORD = "testpassword123"

def test_health():
    """Test if the server is running"""
    try:
        response = requests.get(f"{API_BASE_URL}/api/health")
        if response.status_code == 200:
            print("✅ Server is running")
            return True
        else:
            print(f"❌ Server health check failed: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Make sure the backend is running on http://localhost:5000")
        return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def test_registration():
    """Test user registration"""
    print("\n🔐 Testing Registration...")
    
    registration_data = {
        "email": TEST_EMAIL,
        "firstName": "Test",
        "lastName": "User",
        "password": TEST_PASSWORD,
        "role": "retailer",
        "businessName": "Test Business",
        "address": "123 Test Street",
        "phoneNumber": "+1234567890"
    }
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/auth/register",
            json=registration_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Registration Response Status: {response.status_code}")
        print(f"Registration Response: {response.text}")
        
        if response.status_code == 201:
            print("✅ Registration successful")
            return True
        elif response.status_code == 409:
            print("⚠️  User already exists, continuing with login test")
            return True
        else:
            print("❌ Registration failed")
            return False
            
    except Exception as e:
        print(f"❌ Registration error: {e}")
        return False

def test_login():
    """Test user login"""
    print("\n🔑 Testing Login...")
    
    login_data = {
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD
    }
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/auth/login",
            json=login_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Login Response Status: {response.status_code}")
        print(f"Login Response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            if "access_token" in data:
                print("✅ Login successful")
                return data["access_token"]
            else:
                print("❌ Login response missing access token")
                return None
        else:
            print("❌ Login failed")
            return None
            
    except Exception as e:
        print(f"❌ Login error: {e}")
        return None

def test_user_info(token):
    """Test getting user information with token"""
    print("\n👤 Testing User Info...")
    
    try:
        response = requests.get(
            f"{API_BASE_URL}/api/auth/user",
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
        )
        
        print(f"User Info Response Status: {response.status_code}")
        print(f"User Info Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ User info retrieval successful")
            return True
        else:
            print("❌ User info retrieval failed")
            return False
            
    except Exception as e:
        print(f"❌ User info error: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Starting Authentication Tests...")
    print(f"API Base URL: {API_BASE_URL}")
    
    # Test 1: Health check
    if not test_health():
        print("\n❌ Health check failed. Please start the backend server first.")
        sys.exit(1)
    
    # Test 2: Registration
    if not test_registration():
        print("\n❌ Registration test failed.")
        sys.exit(1)
    
    # Test 3: Login
    token = test_login()
    if not token:
        print("\n❌ Login test failed.")
        sys.exit(1)
    
    # Test 4: User info
    if not test_user_info(token):
        print("\n❌ User info test failed.")
        sys.exit(1)
    
    print("\n🎉 All authentication tests passed!")
    print("✅ Signup and login functionality is working correctly with MySQL")

if __name__ == "__main__":
    main()
