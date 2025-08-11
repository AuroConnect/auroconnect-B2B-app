#!/usr/bin/env python3
"""
Test Enhanced Order Status Management
Tests the comprehensive order status management system including:
- Status transitions and validation
- Status history tracking
- Inventory updates
- Role-based access control
"""

import requests
import json
import time
from datetime import datetime

BASE_URL = "http://localhost:5000/api"

def test_order_status_management():
    """Test comprehensive order status management"""
    
    print("🧪 Testing Enhanced Order Status Management")
    print("=" * 60)
    
    # Step 1: Login as distributor (can update order status)
    print(f"\n🔐 Logging in as distributor...")
    login_data = {
        "email": "distributor1@test.com",
        "password": "password123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/login", json=login_data, timeout=10)
        if response.status_code == 200:
            distributor_token = response.json().get('access_token')
            print("✅ Distributor login successful")
        else:
            print(f"❌ Distributor login failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return
    except Exception as e:
        print(f"❌ Login error: {e}")
        return
    
    distributor_headers = {"Authorization": f"Bearer {distributor_token}"}
    
    # Step 2: Get orders for distributor
    print(f"\n📋 Getting distributor orders...")
    try:
        response = requests.get(f"{BASE_URL}/orders", headers=distributor_headers, timeout=10)
        if response.status_code == 200:
            orders = response.json()
            print(f"✅ Found {len(orders)} orders")
            
            if not orders:
                print("⚠️  No orders found for distributor. Creating a test order...")
                # Create a test order by logging in as retailer and placing an order
                retailer_login_data = {
                    "email": "retailer1@test.com",
                    "password": "password123"
                }
                
                retailer_response = requests.post(f"{BASE_URL}/auth/login", json=retailer_login_data, timeout=10)
                if retailer_response.status_code == 200:
                    retailer_token = retailer_response.json().get('access_token')
                    retailer_headers = {"Authorization": f"Bearer {retailer_token}"}
                    
                    # Add products to cart
                    products_response = requests.get(f"{BASE_URL}/products", headers=retailer_headers, timeout=10)
                    if products_response.status_code == 200:
                        products = products_response.json()
                        if products:
                            # Add first product to cart
                            cart_data = {
                                "productId": products[0]['id'],
                                "quantity": 2
                            }
                            cart_response = requests.post(f"{BASE_URL}/cart/add", 
                                                        json=cart_data,
                                                        headers=retailer_headers, timeout=10)
                            if cart_response.status_code == 200:
                                print("✅ Added product to cart")
                                
                                # Place order
                                order_response = requests.post(f"{BASE_URL}/orders", 
                                                             headers=retailer_headers, timeout=10)
                                if order_response.status_code == 201:
                                    order_data = order_response.json()
                                    print(f"✅ Created test order: {order_data.get('orderNumber')}")
                                    
                                    # Get updated orders list
                                    response = requests.get(f"{BASE_URL}/orders", headers=distributor_headers, timeout=10)
                                    if response.status_code == 200:
                                        orders = response.json()
                                        print(f"✅ Now found {len(orders)} orders")
                                    else:
                                        print(f"❌ Failed to get updated orders: {response.status_code}")
                                        return
                                else:
                                    print(f"❌ Failed to place order: {order_response.status_code}")
                                    return
                            else:
                                print(f"❌ Failed to add to cart: {cart_response.status_code}")
                                return
                        else:
                            print("❌ No products available")
                            return
                    else:
                        print(f"❌ Failed to get products: {products_response.status_code}")
                        return
                else:
                    print(f"❌ Retailer login failed: {retailer_response.status_code}")
                    return
        else:
            print(f"❌ Failed to get orders: {response.status_code}")
            print(f"   Response: {response.text}")
            return
    except Exception as e:
        print(f"❌ Error getting orders: {e}")
        return
    
    if not orders:
        print("❌ No orders available for testing")
        return
    
    # Step 3: Test status updates on first order
    test_order = orders[0]
    order_id = test_order['id']
    current_status = test_order['status']
    
    print(f"\n📦 Testing status updates for order: {test_order['orderNumber']}")
    print(f"   Current status: {current_status}")
    
    # Test valid status transitions
    valid_transitions = {
        'pending': ['confirmed', 'accepted', 'rejected', 'cancelled'],
        'confirmed': ['accepted', 'processing', 'rejected', 'cancelled'],
        'accepted': ['processing', 'packed', 'rejected', 'cancelled'],
        'processing': ['packed', 'shipped', 'rejected', 'cancelled'],
        'packed': ['shipped', 'out_for_delivery', 'rejected', 'cancelled'],
        'shipped': ['out_for_delivery', 'delivered', 'rejected', 'cancelled'],
        'out_for_delivery': ['delivered', 'rejected', 'cancelled'],
        'delivered': [],
        'rejected': [],
        'cancelled': []
    }
    
    available_transitions = valid_transitions.get(current_status, [])
    
    if not available_transitions:
        print(f"⚠️  Order is in final state '{current_status}', cannot update")
        return
    
    # Test first available transition
    new_status = available_transitions[0]
    print(f"\n🔄 Testing status transition: {current_status} → {new_status}")
    
    status_update_data = {
        "status": new_status,
        "notes": f"Test status update from {current_status} to {new_status} at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    }
    
    try:
        response = requests.put(f"{BASE_URL}/orders/{order_id}/status", 
                              json=status_update_data,
                              headers=distributor_headers, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Status update successful!")
            print(f"   Previous status: {result.get('previousStatus')}")
            print(f"   New status: {result.get('newStatus')}")
            print(f"   Updated by: {result.get('updatedBy')}")
            print(f"   Notes: {result.get('notes')}")
            
            # Test status history
            print(f"\n📜 Testing status history...")
            history_response = requests.get(f"{BASE_URL}/orders/{order_id}/status-history", 
                                          headers=distributor_headers, timeout=10)
            
            if history_response.status_code == 200:
                history_data = history_response.json()
                print("✅ Status history retrieved successfully!")
                print(f"   Current status: {history_data.get('currentStatus')}")
                print(f"   History entries: {len(history_data.get('statusHistory', []))}")
                
                for i, entry in enumerate(history_data.get('statusHistory', [])):
                    print(f"   Entry {i+1}: {entry.get('status')} at {entry.get('timestamp')}")
                    if entry.get('notes'):
                        print(f"      Notes: {entry.get('notes')}")
                    if entry.get('updatedBy'):
                        print(f"      Updated by: {entry.get('updatedBy')}")
            else:
                print(f"❌ Failed to get status history: {history_response.status_code}")
                print(f"   Response: {history_response.text}")
            
            # Test invalid status transition
            print(f"\n🚫 Testing invalid status transition...")
            invalid_status = "invalid_status"
            invalid_update_data = {
                "status": invalid_status,
                "notes": "This should fail"
            }
            
            invalid_response = requests.put(f"{BASE_URL}/orders/{order_id}/status", 
                                          json=invalid_update_data,
                                          headers=distributor_headers, timeout=10)
            
            if invalid_response.status_code == 400:
                print("✅ Invalid status transition correctly rejected!")
                error_data = invalid_response.json()
                print(f"   Error: {error_data.get('message')}")
            else:
                print(f"❌ Invalid status transition should have been rejected: {invalid_response.status_code}")
            
            # Test role-based access control
            print(f"\n🔒 Testing role-based access control...")
            
            # Login as retailer (should not be able to update status)
            retailer_login_data = {
                "email": "retailer1@test.com",
                "password": "password123"
            }
            
            retailer_response = requests.post(f"{BASE_URL}/auth/login", json=retailer_login_data, timeout=10)
            if retailer_response.status_code == 200:
                retailer_token = retailer_response.json().get('access_token')
                retailer_headers = {"Authorization": f"Bearer {retailer_token}"}
                
                retailer_update_data = {
                    "status": "processing",
                    "notes": "This should fail - retailer cannot update status"
                }
                
                retailer_status_response = requests.put(f"{BASE_URL}/orders/{order_id}/status", 
                                                      json=retailer_update_data,
                                                      headers=retailer_headers, timeout=10)
                
                if retailer_status_response.status_code == 403:
                    print("✅ Role-based access control working correctly!")
                    print("   Retailer correctly denied access to update order status")
                else:
                    print(f"❌ Role-based access control failed: {retailer_status_response.status_code}")
                    print(f"   Response: {retailer_status_response.text}")
            else:
                print(f"❌ Failed to login as retailer for access control test: {retailer_response.status_code}")
            
        else:
            print(f"❌ Status update failed: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error updating status: {e}")
    
    print(f"\n✅ Order Status Management Test Completed!")

if __name__ == "__main__":
    test_order_status_management()
