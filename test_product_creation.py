#!/usr/bin/env python3
"""
Test script to verify product creation with categories
"""
import requests
import json

BASE_URL = "http://localhost:5000"

def test_product_creation(token):
    """Test product creation"""
    print("Testing product creation...")
    
    # Test data for a new product
    product_data = {
        "name": "AMD FIX Processor",
        "description": "High-performance AMD processor for gaming and productivity",
        "price": 299.99,
        "category": "Electronics",
        "stock": 50,
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
            print(f"Product created successfully!")
            print(f"Response: {response.json()}")
            return True
        else:
            print(f"Failed to create product!")
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
            print(f"Categories retrieved successfully!")
            print(f"Response: {response.json()}")
            return True
        else:
            print(f"Failed to retrieve categories!")
            if response.content:
                print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"Error retrieving categories: {e}")
        return False

def main():
    """Main test function"""
    print("Testing Product Creation and Categories")
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
        test_get_categories(token)
        
        print("\n2. Testing Product Creation")
        test_product_creation(token)

if __name__ == "__main__":
    main()