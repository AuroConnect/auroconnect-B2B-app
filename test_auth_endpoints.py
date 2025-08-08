#!/usr/bin/env python3
"""
Test script to verify auth endpoints
"""
import requests
import json
import time

BASE_URL = "http://localhost:5000"

def test_register():
    """Test user registration"""
    print("Testing user registration...")
    
    # Test data with unique email
    register_data = {
        "firstName": "Test",
        "lastName": "User",
        "email": f"test{int(time.time())}@example.com",  # Unique email
        "password": "testpassword123",
        "role": "retailer",
        "businessName": "Test Business",
        "address": "123 Test Street",
        "phoneNumber": "+1234567890"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/auth/register",
            json=register_data
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 201:
            print("Registration successful!")
            return response.json().get('user', {}), register_data['password']
        else:
            print("Registration failed!")
            return None, None
            
    except Exception as e:
        print(f"Registration error: {e}")
        return None, None

def test_login(email, password):
    """Test user login"""
    print("Testing user login...")
    
    # Test data
    login_data = {
        "email": email,
        "password": password
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json=login_data
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 200:
            print("Login successful!")
            return True
        else:
            print("Login failed!")
            return False
            
    except Exception as e:
        print(f"Login error: {e}")
        return False

def test_existing_user_login():
    """Test login with existing user"""
    print("Testing login with existing user...")
    
    # Test data for existing user
    login_data = {
        "email": "retailer@example.com",
        "password": "password123"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json=login_data
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 200:
            print("Login with existing user successful!")
            return True
        else:
            print("Login with existing user failed!")
            return False
            
    except Exception as e:
        print(f"Login with existing user error: {e}")
        return False

def main():
    """Main test function"""
    print("Testing AuroMart Auth Endpoints")
    print("=" * 40)
    
    # Test login with existing user first
    print("\n1. Testing Login with Existing User")
    test_existing_user_login()
    
    # Test registration
    print("\n2. Testing Registration")
    user, password = test_register()
    
    # Test login with new user
    if user and password:
        print("\n3. Testing Login with New User")
        test_login(user['email'], password)

if __name__ == "__main__":
    main()