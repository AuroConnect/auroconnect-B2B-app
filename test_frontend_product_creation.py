#!/usr/bin/env python3
"""
Test script to verify frontend product creation is working
"""
import requests
import json

BASE_URL = "http://localhost:5000"

def test_product_creation_with_image_url(token):
    """Test product creation with image URL"""
    print("Testing product creation with image URL...")
    
    # Test data for a new product
    product_data = {
        "name": "Test Product with Image URL",
        "description": "Sample product with image URL",
        "sku": "TEST-001",
        "basePrice": 49.99,
        "categoryId": "Electronics",
        "imageUrl": "https://example.com/product-image.jpg"
    }
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/products/", 
            json=product_data, 
            headers=headers
        )
        
        print(f"Status Code: {response.status_code}")
        if response.status_code in [200, 201]:
            print(f"Product created successfully!")
            result = response.json()
            print(f"Product ID: {result['data']['id']}")
            print(f"Product SKU: {result['data']['sku']}")
            return True
        else:
            print(f"Failed to create product!")
            if response.content:
                print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"Error creating product: {e}")
        return False

def test_product_creation_without_image(token):
    """Test product creation without image"""
    print("Testing product creation without image...")
    
    # Test data for a new product
    product_data = {
        "name": "Test Product without Image",
        "description": "Sample product without image",
        "sku": "TEST-002",
        "basePrice": 29.99,
        "categoryId": "Clothing"
    }
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/products/", 
            json=product_data, 
            headers=headers
        )
        
        print(f"Status Code: {response.status_code}")
        if response.status_code in [200, 201]:
            print(f"Product created successfully!")
            result = response.json()
            print(f"Product ID: {result['data']['id']}")
            print(f"Product SKU: {result['data']['sku']}")
            return True
        else:
            print(f"Failed to create product!")
            if response.content:
                print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"Error creating product: {e}")
        return False

def main():
    """Main test function"""
    print("Testing Frontend Product Creation")
    print("=" * 50)
    
    # Login as manufacturer to create product
    login_data = {
        "email": "manufacturer@example.com",  # Using sample manufacturer account
        "password": "password123"
    }
    
    token = None
    try:
        response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
        print(f"Login Status Code: {response.status_code}")
        if response.status_code == 200:
            login_result = response.json()
            token = login_result.get('access_token')
            print(f"Login successful! Token: {token[:20]}...")
        else:
            print("Login failed!")
            print(f"Response: {response.text}")
            return
    except Exception as e:
        print(f"Login error: {e}")
        return
    
    # Test product creation
    if token:
        print("\n1. Testing Product Creation with Image URL")
        test_product_creation_with_image_url(token)
        
        print("\n2. Testing Product Creation without Image")
        test_product_creation_without_image(token)

if __name__ == "__main__":
    main()