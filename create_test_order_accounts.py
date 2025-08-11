#!/usr/bin/env python3
"""
Create test accounts and add products to cart for testing order placement
"""

import requests
import json
import time

BASE_URL = "http://localhost:5000/api"

def create_test_accounts():
    """Create test accounts for order placement testing"""
    
    print("🔧 Creating Test Accounts for Order Placement")
    print("=" * 50)
    
    # Test accounts data
    test_accounts = [
        {
            "email": "retailer@test.com",
            "password": "password123",
            "firstName": "Test",
            "lastName": "Retailer",
            "businessName": "Test Retail Store",
            "phoneNumber": "+1234567890",
            "role": "retailer"
        },
        {
            "email": "distributor@test.com", 
            "password": "password123",
            "firstName": "Test",
            "lastName": "Distributor",
            "businessName": "Test Distribution Co",
            "phoneNumber": "+1234567891",
            "role": "distributor"
        },
        {
            "email": "manufacturer@test.com",
            "password": "password123", 
            "firstName": "Test",
            "lastName": "Manufacturer",
            "businessName": "Test Manufacturing Inc",
            "phoneNumber": "+1234567892",
            "role": "manufacturer"
        }
    ]
    
    created_accounts = []
    
    for account in test_accounts:
        print(f"\n📝 Creating {account['role']} account: {account['email']}")
        
        try:
            response = requests.post(f"{BASE_URL}/auth/register", json=account, timeout=10)
            if response.status_code == 201:
                print(f"✅ {account['role']} account created successfully")
                created_accounts.append(account)
            elif response.status_code == 400:
                error_data = response.json()
                if "already exists" in error_data.get('message', '').lower():
                    print(f"⚠️  {account['role']} account already exists")
                    created_accounts.append(account)
                else:
                    print(f"❌ {account['role']} account creation failed: {error_data.get('message')}")
            else:
                print(f"❌ {account['role']} account creation failed: {response.status_code}")
                print(f"   Response: {response.text}")
        except Exception as e:
            print(f"❌ Error creating {account['role']} account: {e}")
    
    return created_accounts

def add_products_to_cart(token, products_to_add):
    """Add products to cart for testing"""
    
    print(f"\n🛒 Adding {len(products_to_add)} products to cart...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    for product in products_to_add:
        try:
            response = requests.post(f"{BASE_URL}/cart/add", 
                                   json={"productId": product['id'], "quantity": product['quantity']},
                                   headers=headers, timeout=10)
            if response.status_code == 200:
                print(f"✅ Added {product['name']} (Qty: {product['quantity']})")
            else:
                print(f"❌ Failed to add {product['name']}: {response.status_code}")
        except Exception as e:
            print(f"❌ Error adding {product['name']}: {e}")

def test_complete_flow():
    """Test the complete order placement flow"""
    
    print("\n🧪 Testing Complete Order Placement Flow")
    print("=" * 50)
    
    # Step 1: Create test accounts
    accounts = create_test_accounts()
    
    if not accounts:
        print("❌ No accounts available for testing")
        return
    
    # Step 2: Login as retailer
    print(f"\n🔐 Logging in as retailer...")
    login_data = {
        "email": "retailer@test.com",
        "password": "password123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/login", json=login_data, timeout=10)
        if response.status_code == 200:
            token = response.json().get('access_token')
            print("✅ Retailer login successful")
        else:
            print(f"❌ Retailer login failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return
    except Exception as e:
        print(f"❌ Login error: {e}")
        return
    
    # Step 3: Get available products
    print(f"\n📦 Getting available products...")
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{BASE_URL}/products", headers=headers, timeout=10)
        if response.status_code == 200:
            products = response.json()
            print(f"✅ Found {len(products)} products")
            
            if products:
                # Add first 2 products to cart
                products_to_add = products[:2]
                for i, product in enumerate(products_to_add):
                    products_to_add[i]['quantity'] = 2  # Add 2 of each
                
                add_products_to_cart(token, products_to_add)
                
                # Step 4: Test order placement
                print(f"\n📋 Testing order placement...")
                response = requests.post(f"{BASE_URL}/orders", headers=headers, timeout=10)
                if response.status_code == 201:
                    order_data = response.json()
                    print("✅ Order placement successful!")
                    print(f"   Order ID: {order_data.get('orderId')}")
                    print(f"   Order Number: {order_data.get('orderNumber')}")
                    print(f"   Total Amount: ${order_data.get('totalAmount', 0):.2f}")
                    print(f"   Items Count: {order_data.get('itemsCount', 0)}")
                else:
                    print(f"❌ Order placement failed: {response.status_code}")
                    print(f"   Response: {response.text}")
            else:
                print("⚠️  No products available to add to cart")
        else:
            print(f"❌ Failed to get products: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Error in product flow: {e}")

if __name__ == "__main__":
    test_complete_flow()
