#!/usr/bin/env python3
"""
Test script to verify role-based product access control
"""
import requests
import json

BASE_URL = "http://localhost:5000"

def login_user(email, password):
    """Login user and return token"""
    login_data = {
        "email": email,
        "password": password
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
        if response.status_code == 200:
            result = response.json()
            return result.get('access_token'), result.get('user', {})
        else:
            print(f"Login failed for {email}: {response.status_code}")
            if response.content:
                print(f"Response: {response.text}")
            return None, None
    except Exception as e:
        print(f"Login error for {email}: {e}")
        return None, None

def create_product(token, product_data):
    """Create a product as manufacturer"""
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
        
        if response.status_code in [200, 201]:
            result = response.json()
            return result.get('data', {})
        else:
            print(f"Failed to create product: {response.status_code}")
            if response.content:
                print(f"Response: {response.text}")
            return None
    except Exception as e:
        print(f"Error creating product: {e}")
        return None

def get_products(token):
    """Get products for user"""
    headers = {
        'Authorization': f'Bearer {token}'
    }
    
    try:
        response = requests.get(f"{BASE_URL}/api/products/", headers=headers)
        
        if response.status_code == 200:
            result = response.json()
            return result.get('data', {}).get('products', [])
        else:
            print(f"Failed to get products: {response.status_code}")
            if response.content:
                print(f"Response: {response.text}")
            return []
    except Exception as e:
        print(f"Error getting products: {e}")
        return []

def test_role_based_access():
    """Test role-based access control"""
    print("Testing Role-Based Product Access Control")
    print("=" * 50)
    
    # Login as manufacturer
    print("\n1. Logging in as manufacturer...")
    manufacturer_token, manufacturer_user = login_user("manufacturer@example.com", "password123")
    if not manufacturer_token:
        print("Failed to login as manufacturer")
        return
    
    print(f"Manufacturer ID: {manufacturer_user.get('id')}")
    print(f"Manufacturer Role: {manufacturer_user.get('role')}")
    
    # Create a product as manufacturer
    print("\n2. Creating product as manufacturer...")
    product_data = {
        "name": "Role-Based Test Product",
        "description": "Product created for role-based access testing",
        "price": 149.99,
        "category": "Electronics",
        "stock": 30,
        "unit": "piece"
    }
    
    product = create_product(manufacturer_token, product_data)
    if not product:
        print("Failed to create product")
        return
    
    product_id = product.get('id')
    print(f"Product created successfully with ID: {product_id}")
    print(f"Product created by: {product.get('createdBy')}")
    
    # Manufacturer should be able to see their own product
    print("\n3. Testing manufacturer access to their own product...")
    manufacturer_products = get_products(manufacturer_token)
    manufacturer_product_count = len(manufacturer_products)
    print(f"Manufacturer can see {manufacturer_product_count} products")
    
    # Check if manufacturer can see the product they created
    found_product = False
    for p in manufacturer_products:
        if p.get('id') == product_id:
            found_product = True
            print("PASS: Manufacturer can see their own product")
            break
    
    if not found_product:
        print("FAIL: Manufacturer cannot see their own product")
    
    # Login as distributor
    print("\n4. Logging in as distributor...")
    distributor_token, distributor_user = login_user("distributor@example.com", "password123")
    if not distributor_token:
        print("Failed to login as distributor")
        return
    
    print(f"Distributor ID: {distributor_user.get('id')}")
    print(f"Distributor Role: {distributor_user.get('role')}")
    
    # Distributor should not see the product yet (no partnership established)
    print("\n5. Testing distributor access (no partnership)...")
    distributor_products = get_products(distributor_token)
    distributor_product_count = len(distributor_products)
    print(f"Distributor can see {distributor_product_count} products")
    
    # Check if distributor can see the manufacturer's product
    found_product = False
    for p in distributor_products:
        if p.get('id') == product_id:
            found_product = True
            print("FAIL: Distributor can see manufacturer's product (should not be able to)")
            break
    
    if not found_product:
        print("PASS: Distributor cannot see manufacturer's product (no partnership)")
    
    # Login as retailer
    print("\n6. Logging in as retailer...")
    retailer_token, retailer_user = login_user("retailer@example.com", "password123")
    if not retailer_token:
        print("Failed to login as retailer")
        return
    
    print(f"Retailer ID: {retailer_user.get('id')}")
    print(f"Retailer Role: {retailer_user.get('role')}")
    
    # Retailer should not see the product yet (no partnership established)
    print("\n7. Testing retailer access (no partnership)...")
    retailer_products = get_products(retailer_token)
    retailer_product_count = len(retailer_products)
    print(f"Retailer can see {retailer_product_count} products")
    
    # Check if retailer can see the manufacturer's product
    found_product = False
    for p in retailer_products:
        if p.get('id') == product_id:
            found_product = True
            print("FAIL: Retailer can see manufacturer's product (should not be able to)")
            break
    
    if not found_product:
        print("PASS: Retailer cannot see manufacturer's product (no partnership)")
    
    print("\n" + "=" * 50)
    print("Role-based access control test completed!")
    print("To test with partnerships, you would need to create partnerships between users.")

if __name__ == "__main__":
    test_role_based_access()