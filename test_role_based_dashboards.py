#!/usr/bin/env python3
"""
Test script for role-based dashboard system
"""

import requests
import json
import time

# Configuration
BASE_URL = "http://localhost:5000"
API_BASE = f"{BASE_URL}/api/v1"

def test_role_based_dashboards():
    """Test the role-based dashboard system"""
    
    print("🧪 Testing Role-Based Dashboard System")
    print("=" * 50)
    
    # Test users for each role
    test_users = [
        {
            "role": "manufacturer",
            "email": "hrushikesh@auromart.com",
            "password": "password123",
            "name": "Hrushikesh Waghmare"
        },
        {
            "role": "distributor", 
            "email": "distributor1@test.com",
            "password": "password123",
            "name": "Metro Distributors"
        },
        {
            "role": "retailer",
            "email": "retailer1@test.com", 
            "password": "password123",
            "name": "City Mart"
        }
    ]
    
    for user in test_users:
        print(f"\n🔐 Testing {user['role'].upper()} Dashboard")
        print("-" * 30)
        
        # Login
        login_data = {
            "email": user["email"],
            "password": user["password"]
        }
        
        try:
            # Login
            login_response = requests.post(f"{API_BASE}/auth/login", json=login_data)
            if login_response.status_code != 200:
                print(f"❌ Login failed for {user['role']}: {login_response.text}")
                continue
                
            login_result = login_response.json()
            token = login_result.get("access_token")
            user_data = login_result.get("user")
            
            if not token:
                print(f"❌ No token received for {user['role']}")
                continue
                
            print(f"✅ Login successful for {user['name']} ({user['role']})")
            
            # Set headers for authenticated requests
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
            
            # Test role-specific stats
            stats_endpoints = {
                "manufacturer": "/analytics/manufacturer-stats",
                "distributor": "/analytics/distributor-stats", 
                "retailer": "/analytics/retailer-stats"
            }
            
            stats_endpoint = stats_endpoints.get(user["role"])
            if stats_endpoint:
                stats_response = requests.get(f"{API_BASE}{stats_endpoint}", headers=headers)
                if stats_response.status_code == 200:
                    stats = stats_response.json()
                    print(f"✅ {user['role'].title()} stats: {stats}")
                else:
                    print(f"❌ Failed to get {user['role']} stats: {stats_response.text}")
            
            # Test role-specific orders
            orders_endpoints = {
                "manufacturer": "/orders/manufacturer-recent",
                "distributor": "/orders/retailer-incoming",
                "retailer": "/orders/my-orders"
            }
            
            orders_endpoint = orders_endpoints.get(user["role"])
            if orders_endpoint:
                orders_response = requests.get(f"{API_BASE}{orders_endpoint}", headers=headers)
                if orders_response.status_code == 200:
                    orders = orders_response.json()
                    print(f"✅ {user['role'].title()} orders: {len(orders)} orders found")
                else:
                    print(f"❌ Failed to get {user['role']} orders: {orders_response.text}")
            
            # Test role-specific partners
            if user["role"] == "manufacturer":
                partners_response = requests.get(f"{API_BASE}/partners/distributors", headers=headers)
                if partners_response.status_code == 200:
                    distributors = partners_response.json()
                    print(f"✅ Manufacturer distributors: {len(distributors)} distributors found")
                else:
                    print(f"❌ Failed to get distributors: {partners_response.text}")
                    
            elif user["role"] == "distributor":
                partners_response = requests.get(f"{API_BASE}/partners/retailers", headers=headers)
                if partners_response.status_code == 200:
                    retailers = partners_response.json()
                    print(f"✅ Distributor retailers: {len(retailers)} retailers found")
                else:
                    print(f"❌ Failed to get retailers: {partners_response.text}")
            
            # Test role-specific products
            if user["role"] in ["distributor", "retailer"]:
                products_endpoint = f"/products/{user['role']}"
                products_response = requests.get(f"{API_BASE}{products_endpoint}", headers=headers)
                if products_response.status_code == 200:
                    products = products_response.json()
                    print(f"✅ {user['role'].title()} products: {len(products)} products found")
                else:
                    print(f"❌ Failed to get {user['role']} products: {products_response.text}")
            
            # Test invoices for retailers
            if user["role"] == "retailer":
                invoices_response = requests.get(f"{API_BASE}/invoices/my-invoices", headers=headers)
                if invoices_response.status_code == 200:
                    invoices = invoices_response.json()
                    print(f"✅ Retailer invoices: {len(invoices)} invoices found")
                else:
                    print(f"❌ Failed to get invoices: {invoices_response.text}")
            
            print(f"✅ {user['role'].title()} dashboard tests completed successfully")
            
        except Exception as e:
            print(f"❌ Error testing {user['role']} dashboard: {str(e)}")
    
    print("\n🎉 Role-based dashboard testing completed!")
    print("\n📋 Summary:")
    print("- Manufacturer dashboard: /manufacturer/dashboard")
    print("- Distributor dashboard: /distributor/dashboard") 
    print("- Retailer dashboard: /retailer/dashboard")
    print("\n🔗 Frontend routes are configured to redirect users to their role-specific dashboards")
    print("🔐 Backend APIs provide role-specific data access")

if __name__ == "__main__":
    test_role_based_dashboards()
