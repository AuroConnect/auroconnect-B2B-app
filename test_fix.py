#!/usr/bin/env python3
"""
Test the Content-Type fix
"""

import requests
import json

BASE_URL = "http://localhost:5000"

def test_product_creation():
    """Test product creation with the fix"""
    
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
        
        # Test product data (like in the image)
        product_data = {
            "name": "Laptop",
            "sku": "2333",
            "category": "Electronics",
            "description": "asfafasfdasfasffas",
            "basePrice": 100,
            "imageUrl": "https://example.com/image.jpg"
        }
        
        print("📝 Testing product creation with fix:")
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
    print("🔍 Testing Content-Type Fix")
    print("=" * 40)
    
    success = test_product_creation()
    
    if success:
        print("\n✅ Content-Type fix is working!")
        print("🌐 You can now add products through the frontend.")
    else:
        print("\n❌ Content-Type fix is not working.")
        print("Check the backend logs for more details.")
