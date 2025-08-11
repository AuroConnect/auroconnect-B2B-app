#!/usr/bin/env python3
"""
Test order placement with existing accounts from seed data
"""

import requests
import json
import time

BASE_URL = "http://localhost:5000/api"

def test_order_placement_with_existing_accounts():
    """Test order placement with existing accounts"""
    
    print("🧪 Testing Order Placement with Existing Accounts")
    print("=" * 50)
    
    # Step 1: Login as an existing retailer (from seed data)
    print(f"\n🔐 Logging in as existing retailer...")
    login_data = {
        "email": "retailer1@test.com",
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
    
    # Step 2: Get available products
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
                
                # Step 3: Add products to cart
                print(f"\n🛒 Adding {len(products_to_add)} products to cart...")
                
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
    test_order_placement_with_existing_accounts()
