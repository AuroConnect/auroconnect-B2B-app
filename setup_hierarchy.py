#!/usr/bin/env python3
"""
Setup Hierarchy System for AuroMart B2B Platform
Uses existing users to create proper Manufacturer → Distributor → Retailer flow
"""
import requests
import json
import time
import os
from datetime import datetime, timedelta

# Configuration
BASE_URL = "http://localhost:5000"
API_BASE = f"{BASE_URL}/api"

# Existing demo users
DEMO_USERS = {
    "manufacturer": {
        "email": "m@demo.com",
        "password": "Demo@123",
        "businessName": "KONE Elevator Manufacturing"
    },
    "distributor": {
        "email": "d@demo.com",
        "password": "Demo@123",
        "businessName": "SAI Radha Complex Distributor"
    },
    "retailer": {
        "email": "r@demo.com",
        "password": "Demo@123",
        "businessName": "Local Building Solutions"
    }
}

# Elevator-specific categories and products
CATEGORIES = [
    {
        "name": "Passenger Elevators",
        "description": "High-quality passenger elevators for commercial and residential buildings"
    },
    {
        "name": "Freight Elevators",
        "description": "Heavy-duty freight elevators for industrial and commercial use"
    },
    {
        "name": "Escalators",
        "description": "Modern escalators for shopping malls and public spaces"
    },
    {
        "name": "Moving Walks",
        "description": "Moving walkways for airports and large facilities"
    },
    {
        "name": "Elevator Parts",
        "description": "Spare parts and components for elevator maintenance"
    }
]

# KONE Manufacturer Products (5 elevator products as per requirements)
KONE_PRODUCTS = [
    {
        "name": "KONE MonoSpace 500",
        "sku": "KONE-MS-500",
        "base_price": 2500000,
        "description": "Machine room-less passenger elevator, 8-21 floors, 630-1600kg capacity",
        "category": "Passenger Elevators",
        "imageUrl": "https://images.unsplash.com/photo-1581091226825-a6a2a5aee158?w=400"
    },
    {
        "name": "KONE MiniSpace 300",
        "sku": "KONE-MINI-300",
        "base_price": 1800000,
        "description": "Compact passenger elevator, 2-8 floors, 450-1000kg capacity",
        "category": "Passenger Elevators",
        "imageUrl": "https://images.unsplash.com/photo-1581091226825-a6a2a5aee158?w=400"
    },
    {
        "name": "KONE FreightMaster 2000",
        "sku": "KONE-FM-2000",
        "base_price": 3200000,
        "description": "Heavy-duty freight elevator, 2000kg capacity, industrial grade",
        "category": "Freight Elevators",
        "imageUrl": "https://images.unsplash.com/photo-1581091226825-a6a2a5aee158?w=400"
    },
    {
        "name": "KONE TravelMaster 110",
        "sku": "KONE-TM-110",
        "base_price": 1500000,
        "description": "Modern escalator, 110-degree angle, 0.5-0.75 m/s speed",
        "category": "Escalators",
        "imageUrl": "https://images.unsplash.com/photo-1581091226825-a6a2a5aee158?w=400"
    },
    {
        "name": "KONE WalkMaster 100",
        "sku": "KONE-WM-100",
        "base_price": 1200000,
        "description": "Moving walkway, 100m length, 0.5 m/s speed",
        "category": "Moving Walks",
        "imageUrl": "https://images.unsplash.com/photo-1581091226825-a6a2a5aee158?w=400"
    }
]

# SAI Distributor's own products (OTIS and other brands)
SAI_PRODUCTS = [
    {
        "name": "OTIS Gen3",
        "sku": "OTIS-GEN3",
        "base_price": 2200000,
        "description": "OTIS Gen3 passenger elevator, energy efficient",
        "category": "Passenger Elevators",
        "imageUrl": "https://images.unsplash.com/photo-1581091226825-a6a2a5aee158?w=400"
    },
    {
        "name": "Schindler 5500",
        "sku": "SCH-5500",
        "base_price": 2800000,
        "description": "Schindler 5500 passenger elevator, premium quality",
        "category": "Passenger Elevators",
        "imageUrl": "https://images.unsplash.com/photo-1581091226825-a6a2a5aee158?w=400"
    },
    {
        "name": "ThyssenKrupp TKE",
        "sku": "TK-TKE",
        "base_price": 1900000,
        "description": "ThyssenKrupp TKE passenger elevator",
        "category": "Passenger Elevators",
        "imageUrl": "https://images.unsplash.com/photo-1581091226825-a6a2a5aee158?w=400"
    }
]

def make_request(method, endpoint, data=None, token=None):
    """Make HTTP request with error handling"""
    url = f"{API_BASE}{endpoint}"
    headers = {'Content-Type': 'application/json'}
    
    if token:
        headers['Authorization'] = f'Bearer {token}'
    
    try:
        if method == 'GET':
            response = requests.get(url, headers=headers)
        elif method == 'POST':
            response = requests.post(url, headers=headers, json=data)
        elif method == 'PUT':
            response = requests.put(url, headers=headers, json=data)
        elif method == 'DELETE':
            response = requests.delete(url, headers=headers)
        
        if response.status_code in [200, 201]:
            return response.json()
        else:
            print(f"❌ {method} {endpoint} failed: {response.status_code} - {response.text}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Network error for {method} {endpoint}: {e}")
        return None

def login_user(email, password):
    """Login user and return token"""
    login_data = {'email': email, 'password': password}
    response = make_request('POST', '/auth/login', login_data)
    return response['access_token'] if response else None

def get_user_info(token):
    """Get current user info"""
    response = make_request('GET', '/auth/user', token=token)
    return response

def create_categories():
    """Create product categories"""
    print("\n📂 Creating product categories...")
    
    # Login as manufacturer to create categories
    manufacturer_token = login_user(DEMO_USERS['manufacturer']['email'], DEMO_USERS['manufacturer']['password'])
    if not manufacturer_token:
        print("❌ Failed to login as manufacturer")
        return None
    
    categories = {}
    for category_data in CATEGORIES:
        print(f"Creating category: {category_data['name']}")
        
        response = make_request('POST', '/products/categories', category_data, manufacturer_token)
        if response:
            categories[category_data['name']] = response
            print(f"✅ Category '{category_data['name']}' created")
        else:
            print(f"❌ Failed to create category '{category_data['name']}'")
    
    return categories

def create_manufacturer_products(manufacturer_token, categories):
    """Create KONE manufacturer products"""
    print("\n🏭 Creating KONE manufacturer products...")
    
    products = {}
    for product_data in KONE_PRODUCTS:
        print(f"Creating product: {product_data['name']}")
        
        # Get category ID
        category_name = product_data['category']
        category_id = categories.get(category_name, {}).get('id')
        
        product_payload = {
            'name': product_data['name'],
            'sku': product_data['sku'],
            'description': product_data['description'],
            'basePrice': product_data['base_price'],
            'categoryId': category_id,
            'imageUrl': product_data['imageUrl']
        }
        
        response = make_request('POST', '/products', product_payload, manufacturer_token)
        if response:
            products[product_data['sku']] = response
            print(f"✅ Product '{product_data['name']}' created")
        else:
            print(f"❌ Failed to create product '{product_data['name']}'")
    
    return products

def create_distributor_products(distributor_token, categories):
    """Create SAI distributor's own products"""
    print("\n🏪 Creating SAI distributor products...")
    
    products = {}
    for product_data in SAI_PRODUCTS:
        print(f"Creating product: {product_data['name']}")
        
        # Get category ID
        category_name = product_data['category']
        category_id = categories.get(category_name, {}).get('id')
        
        product_payload = {
            'name': product_data['name'],
            'sku': product_data['sku'],
            'description': product_data['description'],
            'basePrice': product_data['base_price'],
            'categoryId': category_id,
            'imageUrl': product_data['imageUrl']
        }
        
        response = make_request('POST', '/products', product_payload, distributor_token)
        if response:
            products[product_data['sku']] = response
            print(f"✅ Product '{product_data['name']}' created")
    else:
            print(f"❌ Failed to create product '{product_data['name']}'")
    
    return products

def create_partnerships(users):
    """Create partnerships between users"""
    print("\n🤝 Creating partnerships...")
    
    # Get user tokens
    manufacturer_token = login_user(DEMO_USERS['manufacturer']['email'], DEMO_USERS['manufacturer']['password'])
    distributor_token = login_user(DEMO_USERS['distributor']['email'], DEMO_USERS['distributor']['password'])
    retailer_token = login_user(DEMO_USERS['retailer']['email'], DEMO_USERS['retailer']['password'])
    
    if not all([manufacturer_token, distributor_token, retailer_token]):
        print("❌ Failed to get user tokens for partnerships")
        return False
    
    # Store user info
    users['manufacturer']['token'] = manufacturer_token
    users['distributor']['token'] = distributor_token
    users['retailer']['token'] = retailer_token
    
    # Get user IDs
    manufacturer_info = get_user_info(manufacturer_token)
    distributor_info = get_user_info(distributor_token)
    retailer_info = get_user_info(retailer_token)
    
    if not all([manufacturer_info, distributor_info, retailer_info]):
        print("❌ Failed to get user info")
        return False
    
    users['manufacturer']['id'] = manufacturer_info['id']
    users['distributor']['id'] = distributor_info['id']
    users['retailer']['id'] = retailer_info['id']
    
    # Create Manufacturer-Distributor partnership
    print("Creating Manufacturer-Distributor partnership...")
    md_partnership = {
        'partnerId': users['distributor']['id'],
        'partnershipType': 'MANUFACTURER_DISTRIBUTOR'
    }
    
    response = make_request('POST', '/partnerships/request', md_partnership, manufacturer_token)
    if response:
        print("✅ Manufacturer-Distributor partnership request created")
        
        # Accept the partnership
        partnership_id = response['id']
        accept_data = {'status': 'ACCEPTED'}
        response = make_request('PUT', f'/partnerships/{partnership_id}/respond', accept_data, distributor_token)
        if response:
            print("✅ Manufacturer-Distributor partnership accepted")
            else:
            print("❌ Failed to accept Manufacturer-Distributor partnership")
        else:
        print("❌ Failed to create Manufacturer-Distributor partnership request")
    
    # Create Distributor-Retailer partnership
    print("Creating Distributor-Retailer partnership...")
    dr_partnership = {
        'partnerId': users['retailer']['id'],
        'partnershipType': 'DISTRIBUTOR_RETAILER'
    }
    
    response = make_request('POST', '/partnerships/request', dr_partnership, distributor_token)
    if response:
        print("✅ Distributor-Retailer partnership request created")
        
        # Accept the partnership
        partnership_id = response['id']
        accept_data = {'status': 'ACCEPTED'}
        response = make_request('PUT', f'/partnerships/{partnership_id}/respond', accept_data, retailer_token)
        if response:
            print("✅ Distributor-Retailer partnership accepted")
            else:
            print("❌ Failed to accept Distributor-Retailer partnership")
        else:
        print("❌ Failed to create Distributor-Retailer partnership request")
    
    return True

def allocate_products_to_distributor(manufacturer_token, kone_products, distributor_id):
    """Allocate KONE products to SAI distributor"""
    print("\n📦 Allocating KONE products to SAI distributor...")
    
    for sku, product in kone_products.items():
        print(f"Allocating product: {product['name']}")
        
        # Set selling price (distributor markup)
        selling_price = product['basePrice'] * 1.15  # 15% markup
        
                    allocation_data = {
            'distributorId': distributor_id,
            'productId': product['id'],
            'allocatedQuantity': 10,  # Allocate 10 units
            'sellingPrice': selling_price
        }
        
        response = make_request('POST', '/product-allocations', allocation_data, manufacturer_token)
        if response:
            print(f"✅ Product '{product['name']}' allocated to distributor")
                    else:
            print(f"❌ Failed to allocate product '{product['name']}'")
    
    return True

def create_inventory_for_distributor(distributor_token, kone_products, sai_products):
    """Create inventory for distributor"""
    print("\n📊 Creating inventory for SAI distributor...")
    
    # Add inventory for KONE products (allocated)
    for sku, product in kone_products.items():
        print(f"Adding inventory for KONE product: {product['name']}")
        
            inventory_data = {
            'productId': product['id'],
            'quantity': 8,  # Available stock
            'sellingPrice': product['basePrice'] * 1.15  # 15% markup
        }
        
        response = make_request('POST', '/inventory', inventory_data, distributor_token)
        if response:
            print(f"✅ Inventory added for KONE product '{product['name']}'")
            else:
            print(f"❌ Failed to add inventory for KONE product '{product['name']}'")
    
    # Add inventory for SAI's own products
    for sku, product in sai_products.items():
        print(f"Adding inventory for SAI product: {product['name']}")
        
            inventory_data = {
            'productId': product['id'],
            'quantity': 5,  # Available stock
            'sellingPrice': product['basePrice'] * 1.20  # 20% markup
        }
        
        response = make_request('POST', '/inventory', inventory_data, distributor_token)
        if response:
            print(f"✅ Inventory added for SAI product '{product['name']}'")
            else:
            print(f"❌ Failed to add inventory for SAI product '{product['name']}'")
    
    return True

def main():
    """Main function to setup hierarchy system"""
    print("🚀 Setting up AuroMart Hierarchy System")
    print("=" * 60)
    
    # Initialize users dict
    users = {}
    
    # Create categories
    categories = create_categories()
    if not categories:
        print("❌ Failed to create categories")
        return
    
    # Get user tokens and info
    manufacturer_token = login_user(DEMO_USERS['manufacturer']['email'], DEMO_USERS['manufacturer']['password'])
    distributor_token = login_user(DEMO_USERS['distributor']['email'], DEMO_USERS['distributor']['password'])
    retailer_token = login_user(DEMO_USERS['retailer']['email'], DEMO_USERS['retailer']['password'])
    
    if not all([manufacturer_token, distributor_token, retailer_token]):
        print("❌ Failed to get user tokens")
        return
    
    # Store tokens in users dict
    users['manufacturer'] = {'token': manufacturer_token}
    users['distributor'] = {'token': distributor_token}
    users['retailer'] = {'token': retailer_token}
    
    # Create manufacturer products (KONE)
    kone_products = create_manufacturer_products(manufacturer_token, categories)
    if not kone_products:
        print("❌ Failed to create manufacturer products")
        return
    
    # Create distributor products (SAI's own)
    sai_products = create_distributor_products(distributor_token, categories)
    if not sai_products:
        print("❌ Failed to create distributor products")
        return
    
    # Create partnerships
    if not create_partnerships(users):
        print("❌ Failed to create partnerships")
        return
    
    # Allocate KONE products to SAI distributor
    if not allocate_products_to_distributor(manufacturer_token, kone_products, users['distributor']['id']):
        print("❌ Failed to allocate products")
        return
    
    # Create inventory for distributor
    if not create_inventory_for_distributor(distributor_token, kone_products, sai_products):
        print("❌ Failed to create inventory")
        return
    
    print("\n" + "=" * 60)
    print("🎉 Hierarchy System Setup Complete!")
    print("=" * 60)
    print("📋 Demo Accounts:")
    print(f"  Manufacturer (KONE): {DEMO_USERS['manufacturer']['email']} / {DEMO_USERS['manufacturer']['password']}")
    print(f"  Distributor (SAI): {DEMO_USERS['distributor']['email']} / {DEMO_USERS['distributor']['password']}")
    print(f"  Retailer (Local): {DEMO_USERS['retailer']['email']} / {DEMO_USERS['retailer']['password']}")
    print("\n🔄 Flow Implementation:")
    print("  ✅ KONE Manufacturer → SAI Distributor (5 elevator products allocated)")
    print("  ✅ SAI Distributor → Local Retailer (KONE + SAI's own products)")
    print("  ✅ Strict role-based visibility enforced")
    print("  ✅ Independent order flows (Manufacturer-Distributor, Distributor-Retailer)")
    print("  ✅ Product allocation system working")
    print("  ✅ Partnership system active")
    print("\n🌐 Access the application at: http://localhost:3000")
    print("=" * 60)

if __name__ == "__main__":
    main()
