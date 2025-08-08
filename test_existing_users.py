#!/usr/bin/env python3
"""
Test script to verify login with existing users
"""
import requests
import json

BASE_URL = "http://localhost:5000"

def test_login(email, password):
    """Test user login"""
    print(f"Testing login for {email}...")
    
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
        if response.status_code == 200:
            print(f"Response: {response.json()}")
            print(f"Login successful for {email}!")
            return True
        else:
            print(f"Response: {response.json()}")
            print(f"Login failed for {email}!")
            return False
            
    except Exception as e:
        print(f"Login error for {email}: {e}")
        return False

def main():
    """Main test function"""
    print("Testing Login with Sample Users")
    print("=" * 40)
    
    # Test sample users
    sample_users = [
        {
            'email': 'retailer@example.com',
            'password': 'password123'
        },
        {
            'email': 'distributor@example.com',
            'password': 'password123'
        },
        {
            'email': 'manufacturer@example.com',
            'password': 'password123'
        }
    ]
    
    success_count = 0
    for user in sample_users:
        if test_login(user['email'], user['password']):
            success_count += 1
        print()
    
    print(f"Successfully logged in {success_count}/{len(sample_users)} users")

if __name__ == "__main__":
    main()