#!/usr/bin/env python3
"""
Test product creation fix
"""

import requests
import json

BASE_URL = "http://localhost:5000"

def test_product_creation():
    """Test product creation with the data from the image"""
    
    # Login
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
        headers = {"Authorization": f"Bearer {token}"}
        
        # Test with data from the image
        product_data = {
            "name": "Laptop",
            "sku": "2332",
            "category": "Electronics",
            "description": "sdasdasd",
            "basePrice": 100,
            "imageUrl": "https://example.com/image.jpg"
        }
        
        print("📝 Testing product creation with data from image:")
        print(json.dumps(product_data, indent=2))
        
        response = requests.post(f"{BASE_URL}/api/products/", json=product_data, headers=headers)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 201:
            print("✅ Product created successfully!")
            return True
        else:
            print(f"❌ Product creation failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("🔍 Testing Product Creation Fix")
    print("=" * 40)
    
    success = test_product_creation()
    
    if success:
        print("\n✅ Product creation is now working!")
        print("🌐 You can now add products through the frontend.")
    else:
        print("\n❌ Product creation still has issues.")
        print("Check the backend logs for more details.")
