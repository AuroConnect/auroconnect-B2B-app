#!/usr/bin/env python3
"""
Simple test script to verify registration endpoint works
"""
import requests
import json

def test_registration():
    """Test the registration endpoint"""
    url = "http://localhost:5000/api/auth/register"
    
    # Test data
    test_user = {
        "firstName": "Test",
        "lastName": "User",
        "email": "test@example.com",
        "password": "password123",
        "role": "retailer",
        "businessName": "Test Business",
        "address": "123 Test Street",
        "phoneNumber": "1234567890",
        "whatsappNumber": "1234567890"
    }
    
    try:
        print("Testing registration endpoint...")
        response = requests.post(url, json=test_user)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 201:
            print("✅ Registration test PASSED")
            return True
        else:
            print("❌ Registration test FAILED")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection failed - server may not be running")
        return False
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False

def test_login():
    """Test the login endpoint"""
    url = "http://localhost:5000/api/auth/login"
    
    # Test data
    login_data = {
        "email": "test@example.com",
        "password": "password123"
    }
    
    try:
        print("\nTesting login endpoint...")
        response = requests.post(url, json=login_data)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ Login test PASSED")
            return True
        else:
            print("❌ Login test FAILED")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection failed - server may not be running")
        return False
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing AuroMart Authentication System")
    print("=" * 50)
    
    # Test registration
    reg_success = test_registration()
    
    # Test login
    login_success = test_login()
    
    print("\n" + "=" * 50)
    if reg_success and login_success:
        print("🎉 All tests PASSED! Authentication system is working.")
    else:
        print("💥 Some tests FAILED. Please check the server and database.") 