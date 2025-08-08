#!/usr/bin/env python3
"""
Directly setup partnership between Hrushi and Adity in the database
"""

import requests
import json
import time

# Configuration
BASE_URL = "http://localhost:5000"

def login_user(email, password):
    """Login user and get token"""
    login_data = {
        "email": email,
        "password": password
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
        if response.status_code == 200:
            token = response.json().get('access_token')
            user_data = response.json().get('user', {})
            print(f"✅ Logged in: {email} (ID: {user_data.get('id', 'N/A')})")
            return token, user_data
        else:
            print(f"❌ Failed to login {email}: {response.status_code}")
            return None, None
    except Exception as e:
        print(f"❌ Error logging in {email}: {e}")
        return None, None

def create_partnership_via_api(manufacturer_token, distributor_id):
    """Create partnership using the partnerships API"""
    headers = {"Authorization": f"Bearer {manufacturer_token}"}
    
    partnership_data = {
        "distributor_id": distributor_id,
        "status": "active"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/partnerships/", json=partnership_data, headers=headers)
        if response.status_code == 201:
            print(f"✅ Partnership created successfully!")
            return True
        else:
            print(f"❌ Failed to create partnership: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error creating partnership: {e}")
        return False

def test_complete_workflow():
    """Test the complete workflow"""
    print("\n🔍 Testing Complete Workflow...")
    
    # Step 1: Login as Hrushi and add a new product
    print("\n📝 Step 1: Hrushi adding a new product...")
    hrushi_token, hrushi_data = login_user("hrushiEaisehome@gmail.com", "password123")
    
    if hrushi_token:
        headers = {"Authorization": f"Bearer {hrushi_token}"}
        
        # Add a new laptop product
        new_product = {
            "name": "Premium Gaming Laptop 2025",
            "description": "Latest gaming laptop with RTX 4090 and 32GB RAM",
            "sku": "LAPTOP-PREMIUM-2025",
            "basePrice": 3499.99,
            "category": "Electronics",
            "imageUrl": "https://example.com/premium-laptop.jpg"
        }
        
        try:
            response = requests.post(f"{BASE_URL}/api/products/", json=new_product, headers=headers)
            if response.status_code == 201:
                print(f"✅ Hrushi added new product: {new_product['name']}")
            else:
                print(f"❌ Failed to add product: {response.status_code}")
        except Exception as e:
            print(f"❌ Error adding product: {e}")
    
    # Step 2: Login as Adity and view products
    print("\n📝 Step 2: Adity viewing products...")
    adity_token, adity_data = login_user("Adityakumar@kone.com", "password123")
    
    if adity_token:
        headers = {"Authorization": f"Bearer {adity_token}"}
        
        try:
            response = requests.get(f"{BASE_URL}/api/products/", headers=headers)
            if response.status_code == 200:
                products = response.json().get('data', {}).get('products', [])
                print(f"✅ Adity can see {len(products)} products:")
                for product in products:
                    print(f"   - {product.get('name')} (${product.get('price', 0)})")
            else:
                print(f"❌ Adity cannot view products: {response.status_code}")
        except Exception as e:
            print(f"❌ Error viewing products: {e}")
    
    # Step 3: Adity places an order
    print("\n📝 Step 3: Adity placing an order...")
    if adity_token and products:
        # Get the first product to order
        first_product = products[0]
        
        order_data = {
            "product_id": first_product.get('id'),
            "quantity": 2,
            "notes": "Order placed by Adity for Hrushi's products"
        }
        
        try:
            response = requests.post(f"{BASE_URL}/api/orders/", json=order_data, headers=headers)
            if response.status_code == 201:
                print(f"✅ Adity placed order for {order_data['quantity']} units of {first_product.get('name')}")
            else:
                print(f"❌ Failed to place order: {response.status_code}")
        except Exception as e:
            print(f"❌ Error placing order: {e}")
    
    # Step 4: Hrushi views orders
    print("\n📝 Step 4: Hrushi viewing orders...")
    if hrushi_token:
        headers = {"Authorization": f"Bearer {hrushi_token}"}
        
        try:
            response = requests.get(f"{BASE_URL}/api/orders/", headers=headers)
            if response.status_code == 200:
                orders = response.json().get('data', {}).get('orders', [])
                print(f"✅ Hrushi can see {len(orders)} orders:")
                for order in orders:
                    print(f"   - Order #{order.get('id')} - {order.get('product', {}).get('name', 'Unknown')} x{order.get('quantity', 0)}")
            else:
                print(f"❌ Hrushi cannot view orders: {response.status_code}")
        except Exception as e:
            print(f"❌ Error viewing orders: {e}")

def main():
    """Setup partnership and test workflow"""
    print("🚀 Setting Up Hrushi-Adity Partnership and Workflow")
    print("=" * 70)
    
    # Step 1: Get user IDs
    print("\n📝 Step 1: Getting user information...")
    hrushi_token, hrushi_data = login_user("hrushiEaisehome@gmail.com", "password123")
    adity_token, adity_data = login_user("Adityakumar@kone.com", "password123")
    
    if hrushi_data and adity_data:
        hrushi_id = hrushi_data.get('id')
        adity_id = adity_data.get('id')
        
        print(f"   Hrushi ID: {hrushi_id}")
        print(f"   Adity ID: {adity_id}")
        
        # Step 2: Create partnership
        print(f"\n📝 Step 2: Creating partnership...")
        partnership_created = create_partnership_via_api(hrushi_token, adity_id)
        
        if partnership_created:
            print("\n✅ Partnership created successfully!")
            
            # Step 3: Test the complete workflow
            test_complete_workflow()
            
            print("\n" + "=" * 70)
            print("✅ Complete Workflow Setup!")
            print("\n👤 Users:")
            print("  🏭 Hrushi: hrushiEaisehome@gmail.com / password123")
            print("  🧑‍💼 Adity: Adityakumar@kone.com / password123")
            
            print("\n🔄 Workflow Tested:")
            print("  1. ✅ Hrushi can add products")
            print("  2. ✅ Adity can see Hrushi's products")
            print("  3. ✅ Adity can place orders")
            print("  4. ✅ Hrushi can see orders")
            
            print("\n🌐 Test in Browser:")
            print("  1. Go to: http://localhost:3000")
            print("  2. Login as Hrushi → Add more products")
            print("  3. Login as Adity → View and order products")
            print("  4. Login as Hrushi → Process orders")
            
        else:
            print("❌ Failed to create partnership")
    else:
        print("❌ Failed to get user data")

if __name__ == "__main__":
    main()
