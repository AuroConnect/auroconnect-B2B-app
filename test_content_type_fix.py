#!/usr/bin/env python3
"""
Test Content-Type header issue
"""

import requests
import json

BASE_URL = "http://localhost:5000"

def test_content_type_issue():
    """Test the Content-Type header issue"""
    
    # Login first
    login_data = {
        "email": "hrushiEaisehome@gmail.com",
        "password": "password123"
    }
    
    try:
        # Login
        response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
        if response.status_code != 200:
            print(f"❌ Login failed: {response.status_code}")
            return False
        
        token = response.json().get('access_token')
        
        # Test 1: With explicit Content-Type header
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        product_data = {
            "name": "Test Laptop",
            "sku": "TEST-001",
            "basePrice": 100.00,
            "category": "Electronics",
            "description": "Test laptop"
        }
        
        print("📝 Testing with explicit Content-Type header:")
        print(f"Headers: {headers}")
        print(f"Data: {json.dumps(product_data, indent=2)}")
        
        response = requests.post(f"{BASE_URL}/api/products/", json=product_data, headers=headers)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 201:
            print("✅ Product created successfully with explicit Content-Type!")
            return True
        else:
            print(f"❌ Failed with explicit Content-Type: {response.status_code}")
            
            # Test 2: Without Content-Type header (let requests set it)
            headers_no_content_type = {
                "Authorization": f"Bearer {token}"
            }
            
            print("\n📝 Testing without explicit Content-Type header:")
            print(f"Headers: {headers_no_content_type}")
            
            response2 = requests.post(f"{BASE_URL}/api/products/", json=product_data, headers=headers_no_content_type)
            print(f"Status: {response2.status_code}")
            print(f"Response: {response2.text}")
            
            if response2.status_code == 201:
                print("✅ Product created successfully without explicit Content-Type!")
                return True
            else:
                print(f"❌ Failed without explicit Content-Type: {response2.status_code}")
                return False
                
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_backend_content_type_handling():
    """Test how the backend handles Content-Type"""
    
    # Test with different Content-Type values
    test_cases = [
        ("application/json", True),
        ("application/json; charset=utf-8", True),
        ("text/plain", False),
        ("", False)
    ]
    
    for content_type, should_work in test_cases:
        print(f"\n📝 Testing Content-Type: '{content_type}' (should work: {should_work})")
        
        headers = {"Content-Type": content_type} if content_type else {}
        
        try:
            response = requests.post(f"{BASE_URL}/api/products/", 
                                  json={"name": "test", "sku": "test", "basePrice": 100},
                                  headers=headers)
            
            print(f"Status: {response.status_code}")
            if response.status_code == 400:
                print(f"Response: {response.text}")
            
            if should_work and response.status_code != 400:
                print("✅ Backend accepted this Content-Type")
            elif not should_work and response.status_code == 400:
                print("✅ Backend correctly rejected this Content-Type")
            else:
                print("❌ Unexpected behavior")
                
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("🔍 Testing Content-Type Header Issue")
    print("=" * 50)
    
    success = test_content_type_issue()
    
    if success:
        print("\n✅ Content-Type issue resolved!")
    else:
        print("\n❌ Content-Type issue persists.")
        print("\n🔧 Testing backend Content-Type handling:")
        test_backend_content_type_handling()
