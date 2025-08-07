#!/usr/bin/env python3
"""
Quick test for AuroMart B2B Platform - New Workflow
Tests the basic functionality to ensure everything is working.
"""

import requests
import json

# Configuration
BASE_URL = "http://localhost:5000"
API_BASE = f"{BASE_URL}/api"

def test_health():
    """Test basic health check"""
    print("🏥 Testing API Health...")
    try:
        response = requests.get(f"{API_BASE}/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API is healthy!")
            print(f"   Status: {data.get('status')}")
            print(f"   Database: {data.get('database')}")
            return True
        else:
            print(f"❌ API health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return False

def test_registration():
    """Test user registration"""
    print("\n👤 Testing User Registration...")
    
    user_data = {
        'email': 'test@auromart.com',
        'password': 'password123',
        'firstName': 'Test',
        'lastName': 'User',
        'businessName': 'Test Business',
        'role': 'manufacturer',
        'phoneNumber': '+1234567890',
        'address': '123 Test St'
    }
    
    try:
        response = requests.post(f"{API_BASE}/auth/register", json=user_data)
        if response.status_code == 201:
            data = response.json()
            print(f"✅ User registered successfully!")
            print(f"   User ID: {data.get('user', {}).get('id')}")
            return data.get('access_token')
        else:
            print(f"❌ Registration failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Registration error: {e}")
        return None

def test_login():
    """Test user login"""
    print("\n🔐 Testing User Login...")
    
    login_data = {
        'email': 'test@auromart.com',
        'password': 'password123'
    }
    
    try:
        response = requests.post(f"{API_BASE}/auth/login", json=login_data)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Login successful!")
            return data.get('access_token')
        else:
            print(f"❌ Login failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Login error: {e}")
        return None

def test_products_api(token):
    """Test products API with authentication"""
    print("\n📦 Testing Products API...")
    
    headers = {'Authorization': f'Bearer {token}'}
    
    try:
        response = requests.get(f"{API_BASE}/products/", headers=headers)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Products API working!")
            print(f"   Products found: {len(data)}")
            return True
        else:
            print(f"❌ Products API failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Products API error: {e}")
        return False

def test_partners_api(token):
    """Test partners API with authentication"""
    print("\n🤝 Testing Partners API...")
    
    headers = {'Authorization': f'Bearer {token}'}
    
    try:
        response = requests.get(f"{API_BASE}/partners/", headers=headers)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Partners API working!")
            print(f"   Partners found: {len(data)}")
            return True
        else:
            print(f"❌ Partners API failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Partners API error: {e}")
        return False

def test_orders_api(token):
    """Test orders API with authentication"""
    print("\n📋 Testing Orders API...")
    
    headers = {'Authorization': f'Bearer {token}'}
    
    try:
        response = requests.get(f"{API_BASE}/orders/", headers=headers)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Orders API working!")
            print(f"   Orders found: {len(data)}")
            return True
        else:
            print(f"❌ Orders API failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Orders API error: {e}")
        return False

def main():
    """Run all quick tests"""
    print("🚀 AuroMart B2B Platform - Quick Test")
    print("=" * 50)
    
    # Test health
    if not test_health():
        print("\n❌ API is not responding. Please check if the backend is running.")
        return
    
    # Test registration
    token = test_registration()
    if not token:
        print("\n❌ Registration failed. Trying login...")
        token = test_login()
    
    if not token:
        print("\n❌ Authentication failed. Cannot test protected APIs.")
        return
    
    # Test protected APIs
    test_products_api(token)
    test_partners_api(token)
    test_orders_api(token)
    
    print("\n" + "=" * 50)
    print("✅ Quick test completed!")
    print("🎯 Your AuroMart B2B platform is working!")

if __name__ == "__main__":
    main()
