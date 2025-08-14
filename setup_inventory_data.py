#!/usr/bin/env python3
"""
Setup Inventory Data Script
Creates inventory records for distributors so retailers can see available stock
"""
import requests
import json
import time
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:5000"
API_BASE = f"{BASE_URL}/api"

def make_request(method, endpoint, data=None, token=None):
    """Make HTTP request with error handling"""
    url = f"{API_BASE}{endpoint}"
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    
    try:
        if method == "GET":
            response = requests.get(url, headers=headers)
        elif method == "POST":
            response = requests.post(url, headers=headers, json=data)
        elif method == "PUT":
            response = requests.put(url, headers=headers, json=data)
        elif method == "DELETE":
            response = requests.delete(url, headers=headers)
        
        return response
    except Exception as e:
        print(f"❌ Request failed: {e}")
        return None

def login_user(email, password):
    """Login user and return token"""
    print(f"🔐 Logging in {email}...")
    
    login_data = {
        "email": email,
        "password": password
    }
    
    response = make_request("POST", "/auth/login", login_data)
    if response and response.status_code == 200:
        token = response.json().get('access_token')
        print(f"✅ Login successful for {email}")
        return token
    else:
        print(f"❌ Login failed for {email}: {response.text if response else 'No response'}")
        return None

def setup_inventory_data():
    """Setup inventory data for distributors"""
    print("📦 Setting up Inventory Data")
    print("=" * 50)
    
    # Login as distributor
    distributor_token = login_user("d@demo.com", "Demo@123")
    if not distributor_token:
        print("❌ Cannot proceed without distributor login")
        return
    
    # Get all products
    print("\n1. Getting all products...")
    response = make_request("GET", "/products", token=distributor_token)
    if response and response.status_code == 200:
        products = response.json()
        print(f"✅ Found {len(products)} products")
    else:
        print(f"❌ Failed to get products: {response.text if response else 'No response'}")
        return
    
    # Get current inventory
    print("\n2. Getting current inventory...")
    response = make_request("GET", "/inventory", token=distributor_token)
    if response and response.status_code == 200:
        current_inventory = response.json()
        print(f"✅ Found {len(current_inventory.get('inventory', []))} inventory items")
    else:
        print(f"❌ Failed to get inventory: {response.text if response else 'No response'}")
        current_inventory = {"inventory": []}
    
    # Create inventory records for products that don't have them
    print("\n3. Creating inventory records...")
    existing_product_ids = {item.get('productId') for item in current_inventory.get('inventory', [])}
    
    for product in products:
        product_id = product.get('id')
        if product_id not in existing_product_ids:
            # Create inventory record for this product
            inventory_data = {
                "productId": product_id,
                "quantity": 50,  # Set default stock to 50
                "lowStockThreshold": 10,
                "autoRestockQuantity": 50,
                "sellingPrice": product.get('basePrice', 0),
                "isAvailable": True
            }
            
            response = make_request("POST", "/inventory", inventory_data, distributor_token)
            if response and response.status_code == 201:
                print(f"✅ Created inventory for {product.get('name')} - Stock: 50")
            else:
                print(f"❌ Failed to create inventory for {product.get('name')}: {response.text if response else 'No response'}")
        else:
            print(f"ℹ️  Inventory already exists for {product.get('name')}")
    
    # Update existing inventory with proper stock quantities
    print("\n4. Updating existing inventory with stock...")
    for item in current_inventory.get('inventory', []):
        if item.get('quantity', 0) == 0:
            update_data = {
                "quantity": 50,
                "lowStockThreshold": 10,
                "autoRestockQuantity": 50,
                "sellingPrice": item.get('sellingPrice', 0),
                "isAvailable": True
            }
            
            response = make_request("PUT", f"/inventory/{item.get('id')}", update_data, distributor_token)
            if response and response.status_code == 200:
                print(f"✅ Updated inventory for {item.get('productName')} - Stock: 50")
            else:
                print(f"❌ Failed to update inventory for {item.get('productName')}: {response.text if response else 'No response'}")
    
    print("\n" + "=" * 50)
    print("🎉 Inventory Setup Completed!")
    print("=" * 50)
    print("\nNow retailers should be able to:")
    print("✅ See available stock quantities")
    print("✅ Add products to cart")
    print("✅ Adjust quantities based on available stock")
    print("✅ Place orders successfully")

if __name__ == "__main__":
    setup_inventory_data()
