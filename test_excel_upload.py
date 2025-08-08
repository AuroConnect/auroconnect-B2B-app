#!/usr/bin/env python3
"""
Test script to verify Excel product upload functionality
"""
import requests
import json
import pandas as pd
import random
import string
from io import BytesIO

BASE_URL = "http://localhost:5000"

def generate_test_excel():
    """Generate a test Excel file with sample product data"""
    # Sample product data
    data = {
        'name': ['Product A', 'Product B', 'Product C', 'Product D', 'Product E'],
        'sku': [f'SKU-{"".join(random.choices(string.ascii_uppercase + string.digits, k=6))}' for _ in range(5)],
        'basePrice': [100.00, 150.50, 200.75, 99.99, 250.00],
        'category': ['Electronics', 'Clothing', 'Home & Garden', 'Electronics', 'Sports'],
        'description': [
            'High-quality electronic product',
            'Comfortable clothing item',
            'Beautiful home decoration',
            'Advanced electronic device',
            'Professional sports equipment'
        ],
        'stock': [50, 100, 25, 75, 30],
        'unit': ['piece', 'piece', 'piece', 'piece', 'piece'],
        'is_active': [True, True, True, True, True],
        'imageUrl': [
            'https://example.com/product-a.jpg',
            'https://example.com/product-b.jpg',
            'https://example.com/product-c.jpg',
            'https://example.com/product-d.jpg',
            'https://example.com/product-e.jpg'
        ]
    }
    
    # Create DataFrame
    df = pd.DataFrame(data)
    
    # Save to Excel in memory
    excel_buffer = BytesIO()
    df.to_excel(excel_buffer, index=False)
    excel_buffer.seek(0)
    
    return excel_buffer

def test_excel_upload(token):
    """Test Excel product upload"""
    print("Testing Excel product upload...")
    
    # Generate test Excel file
    excel_file = generate_test_excel()
    
    headers = {
        'Authorization': f'Bearer {token}'
    }
    
    files = {
        'file': ('products.xlsx', excel_file, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/products/upload-excel",
            headers=headers,
            files=files
        )
        
        print(f"Status Code: {response.status_code}")
        if response.status_code in [200, 201]:
            print("Excel upload successful!")
            result = response.json()
            print(f"Created {result['data']['created_count']} products")
            if result['data']['errors']:
                print("Errors encountered:")
                for error in result['data']['errors']:
                    print(f"  - {error}")
            return True
        else:
            print("Excel upload failed!")
            if response.content:
                print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"Error uploading Excel: {e}")
        return False

def main():
    """Main test function"""
    print("Testing Excel Product Upload")
    print("=" * 50)
    
    # Login as manufacturer to upload products
    login_data = {
        "email": "manufacturer@example.com",
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
    
    # Test Excel upload
    if token:
        print("\nTesting Excel Product Upload")
        test_excel_upload(token)

if __name__ == "__main__":
    main()