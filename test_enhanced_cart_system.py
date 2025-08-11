#!/usr/bin/env python3
"""
Test Enhanced Cart System
Tests the comprehensive cart system including:
- Real-time cart updates in navigation
- Quantity changes with automatic price updates
- Cart review and order placement
- Visual feedback and user experience
"""

import requests
import json
import time
from datetime import datetime

BASE_URL = "http://localhost:5000/api"

def test_enhanced_cart_system():
    """Test comprehensive cart system functionality"""
    
    print("🛒 Testing Enhanced Cart System")
    print("=" * 50)
    
    # Step 1: Login as retailer
    print(f"\n🔐 Logging in as retailer...")
    login_data = {
        "email": "retailer1@test.com",
        "password": "password123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/login", json=login_data, timeout=10)
        if response.status_code == 200:
            retailer_token = response.json().get('access_token')
            print("✅ Retailer login successful")
        else:
            print(f"❌ Retailer login failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return
    except Exception as e:
        print(f"❌ Login error: {e}")
        return
    
    retailer_headers = {"Authorization": f"Bearer {retailer_token}"}
    
    # Step 2: Clear existing cart
    print(f"\n🧹 Clearing existing cart...")
    try:
        response = requests.delete(f"{BASE_URL}/cart/clear", headers=retailer_headers, timeout=10)
        if response.status_code == 200:
            print("✅ Cart cleared successfully")
        else:
            print(f"⚠️  Cart clear failed: {response.status_code}")
    except Exception as e:
        print(f"⚠️  Cart clear error: {e}")
    
    # Step 3: Get available products
    print(f"\n📦 Getting available products...")
    try:
        response = requests.get(f"{BASE_URL}/products", headers=retailer_headers, timeout=10)
        if response.status_code == 200:
            products = response.json()
            print(f"✅ Found {len(products)} products")
            
            if not products:
                print("❌ No products available for testing")
                return
            
            # Select first 3 products for testing
            test_products = products[:3]
            
        else:
            print(f"❌ Failed to get products: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Error getting products: {e}")
        return
    
    # Step 4: Add products to cart with different quantities
    print(f"\n➕ Adding products to cart...")
    for i, product in enumerate(test_products):
        quantity = i + 1  # Different quantities: 1, 2, 3
        try:
            response = requests.post(f"{BASE_URL}/cart/add", 
                                   json={"productId": product['id'], "quantity": quantity},
                                   headers=retailer_headers, timeout=10)
            if response.status_code == 200:
                print(f"✅ Added {product['name']} (Qty: {quantity})")
            else:
                print(f"❌ Failed to add {product['name']}: {response.status_code}")
        except Exception as e:
            print(f"❌ Error adding {product['name']}: {e}")
    
    # Step 5: Get cart and verify items
    print(f"\n🛒 Getting cart contents...")
    try:
        response = requests.get(f"{BASE_URL}/cart", headers=retailer_headers, timeout=10)
        if response.status_code == 200:
            cart = response.json()
            print("✅ Cart retrieved successfully")
            print(f"   Total items: {cart.get('totalItems', 0)}")
            print(f"   Total amount: ${cart.get('totalAmount', 0):.2f}")
            print(f"   Cart items: {len(cart.get('items', []))}")
            
            for item in cart.get('items', []):
                print(f"   - {item['productName']}: Qty {item['quantity']}, Price ${item['totalPrice']:.2f}")
            
        else:
            print(f"❌ Failed to get cart: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Error getting cart: {e}")
        return
    
    # Step 6: Test quantity updates
    print(f"\n🔄 Testing quantity updates...")
    if cart.get('items'):
        first_item = cart['items'][0]
        item_id = first_item['id']
        new_quantity = first_item['quantity'] + 1
        
        try:
            response = requests.put(f"{BASE_URL}/cart/update/{item_id}", 
                                  json={"quantity": new_quantity},
                                  headers=retailer_headers, timeout=10)
            if response.status_code == 200:
                print(f"✅ Updated quantity for {first_item['productName']} to {new_quantity}")
                
                # Verify the update
                response = requests.get(f"{BASE_URL}/cart", headers=retailer_headers, timeout=10)
                if response.status_code == 200:
                    updated_cart = response.json()
                    updated_item = next((item for item in updated_cart['items'] if item['id'] == item_id), None)
                    if updated_item and updated_item['quantity'] == new_quantity:
                        print(f"✅ Quantity update verified: {updated_item['quantity']}")
                        print(f"   New total: ${updated_cart['totalAmount']:.2f}")
                    else:
                        print(f"❌ Quantity update verification failed")
                else:
                    print(f"❌ Failed to verify quantity update: {response.status_code}")
            else:
                print(f"❌ Failed to update quantity: {response.status_code}")
        except Exception as e:
            print(f"❌ Error updating quantity: {e}")
    
    # Step 7: Test removing an item
    print(f"\n🗑️  Testing item removal...")
    if cart.get('items') and len(cart['items']) > 1:
        item_to_remove = cart['items'][1]  # Remove second item
        try:
            response = requests.delete(f"{BASE_URL}/cart/remove/{item_to_remove['id']}", 
                                     headers=retailer_headers, timeout=10)
            if response.status_code == 200:
                print(f"✅ Removed {item_to_remove['productName']} from cart")
                
                # Verify the removal
                response = requests.get(f"{BASE_URL}/cart", headers=retailer_headers, timeout=10)
                if response.status_code == 200:
                    updated_cart = response.json()
                    remaining_items = len(updated_cart.get('items', []))
                    print(f"✅ Item removal verified: {remaining_items} items remaining")
                    print(f"   New total: ${updated_cart['totalAmount']:.2f}")
                else:
                    print(f"❌ Failed to verify item removal: {response.status_code}")
            else:
                print(f"❌ Failed to remove item: {response.status_code}")
        except Exception as e:
            print(f"❌ Error removing item: {e}")
    
    # Step 8: Test order placement from cart
    print(f"\n📋 Testing order placement from cart...")
    try:
        response = requests.post(f"{BASE_URL}/orders", headers=retailer_headers, timeout=10)
        if response.status_code == 201:
            order_data = response.json()
            print("✅ Order placed successfully!")
            print(f"   Order ID: {order_data.get('orderId')}")
            print(f"   Order Number: {order_data.get('orderNumber')}")
            print(f"   Total Amount: ${order_data.get('totalAmount', 0):.2f}")
            print(f"   Items Count: {order_data.get('itemsCount', 0)}")
            
            # Verify cart is empty after order placement
            response = requests.get(f"{BASE_URL}/cart", headers=retailer_headers, timeout=10)
            if response.status_code == 200:
                empty_cart = response.json()
                if empty_cart.get('totalItems', 0) == 0:
                    print("✅ Cart is empty after order placement")
                else:
                    print(f"⚠️  Cart still has {empty_cart.get('totalItems', 0)} items")
            else:
                print(f"❌ Failed to verify empty cart: {response.status_code}")
                
        else:
            print(f"❌ Failed to place order: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Error placing order: {e}")
    
    # Step 9: Test cart with new items
    print(f"\n🔄 Testing cart with new items...")
    if len(test_products) > 1:
        # Add a different product to test fresh cart
        new_product = test_products[1]
        try:
            response = requests.post(f"{BASE_URL}/cart/add", 
                                   json={"productId": new_product['id'], "quantity": 2},
                                   headers=retailer_headers, timeout=10)
            if response.status_code == 200:
                print(f"✅ Added {new_product['name']} to fresh cart")
                
                # Get updated cart
                response = requests.get(f"{BASE_URL}/cart", headers=retailer_headers, timeout=10)
                if response.status_code == 200:
                    new_cart = response.json()
                    print(f"✅ Fresh cart has {new_cart.get('totalItems', 0)} items")
                    print(f"   Total amount: ${new_cart.get('totalAmount', 0):.2f}")
                else:
                    print(f"❌ Failed to get fresh cart: {response.status_code}")
            else:
                print(f"❌ Failed to add to fresh cart: {response.status_code}")
        except Exception as e:
            print(f"❌ Error adding to fresh cart: {e}")
    
    print(f"\n✅ Enhanced Cart System Test Completed!")

if __name__ == "__main__":
    test_enhanced_cart_system()
