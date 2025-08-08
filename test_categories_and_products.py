#!/usr/bin/env python3
"""
Test script to verify categories and product creation are working
"""
import requests
import json

BASE_URL = "http://localhost:5000"

def test_product_creation_with_category(token, category_name):
    """Test product creation with a specific category"""
    print(f"Testing product creation with category '{category_name}'...")
    
    # Test data for a new product
    product_data = {
        "name": f"Test Product in {category_name}",
        "description": f"Sample product in the {category_name} category",
        "price": 99.99,
        "category": category_name,
        "stock": 25,
        "unit": "piece"
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
            print(f"Product created successfully in category '{category_name}'!")
            result = response.json()
            print(f"Product ID: {result['data']['id']}")
            print(f"Product SKU: {result['data']['sku']}")
            return True
        else:
            print(f"Failed to create product in category '{category_name}'!")
            if response.content:
                print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"Error creating product: {e}")
        return False

def test_get_categories(token):
    """Test getting categories"""
    print("Testing category retrieval...")
    
    headers = {
        'Authorization': f'Bearer {token}'
    }
    
    try:
        response = requests.get(f"{BASE_URL}/api/products/categories", headers=headers)
        
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            categories = result.get('data', [])
            print(f"Categories retrieved successfully! Found {len(categories)} categories:")
            for category in categories:
                print(f"  - {category}")
            return categories
        else:
            print(f"Failed to retrieve categories!")
            if response.content:
                print(f"Response: {response.text}")
            return []
            
    except Exception as e:
        print(f"Error retrieving categories: {e}")
        return []

def main():
    """Main test function"""
    print("Testing Categories and Product Creation")
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
    
    # Test getting categories first
    if token:
        print("\n1. Testing Category Retrieval")
        categories = test_get_categories(token)
        
        print("\n2. Testing Product Creation with Different Categories")
        # Test creating products in different categories
        test_categories = ["Electronics", "Clothing", "Home & Garden", "AMD FIX"]
        
        for category in test_categories:
            test_product_creation_with_category(token, category)
        
        print("\n3. Testing Category Retrieval After Product Creation")
        # Check categories again after creating products
        final_categories = test_get_categories(token)
        
        print(f"\nSummary: Successfully tested product creation with categories.")
        print(f"Categories available: {len(final_categories)}")
        for category in final_categories:
            print(f"  - {category}")

if __name__ == "__main__":
    main()