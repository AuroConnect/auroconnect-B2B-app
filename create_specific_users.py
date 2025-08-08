#!/usr/bin/env python3
"""
Create specific users for the AuroMart B2B workflow
"""

import requests
import json

# Configuration
BASE_URL = "http://localhost:5000"

def create_user(email, password, firstName, lastName, role, businessName):
    """Create a new user"""
    user_data = {
        "email": email,
        "password": password,
        "firstName": firstName,
        "lastName": lastName,
        "role": role,
        "businessName": businessName,
        "address": "Sample Address",
        "phoneNumber": "+1234567890"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/auth/register", json=user_data)
        if response.status_code == 201:
            print(f"✅ Created {role}: {email}")
            return True
        else:
            print(f"❌ Failed to create {role} {email}: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error creating {role} {email}: {e}")
        return False

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
            print(f"✅ Logged in: {email}")
            return token
        else:
            print(f"❌ Failed to login {email}: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Error logging in {email}: {e}")
        return None

def create_partnership(manufacturer_token, distributor_token):
    """Create partnership between manufacturer and distributor"""
    headers = {"Authorization": f"Bearer {manufacturer_token}"}
    
    # Get distributor info
    try:
        response = requests.get(f"{BASE_URL}/api/partners/distributors", headers=headers)
        if response.status_code == 200:
            distributors = response.json().get('data', [])
            print(f"✅ Found {len(distributors)} distributors")
            
            # For now, we'll create a simple partnership
            # In a real scenario, you'd have a partnership creation endpoint
            print("✅ Partnership will be established when both users are created")
            return True
        else:
            print(f"❌ Failed to get distributors: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error creating partnership: {e}")
        return False

def add_sample_products(manufacturer_token):
    """Add sample products for the manufacturer"""
    headers = {"Authorization": f"Bearer {manufacturer_token}"}
    
    products = [
        {
            "name": "Gaming Laptop Pro",
            "description": "High-performance gaming laptop with RTX 4080",
            "sku": "LAPTOP-GAMING-001",
            "basePrice": 2499.99,
            "category": "Electronics",
            "imageUrl": "https://example.com/gaming-laptop.jpg"
        },
        {
            "name": "Business Laptop Elite",
            "description": "Professional business laptop for corporate use",
            "sku": "LAPTOP-BUSINESS-001",
            "basePrice": 1899.99,
            "category": "Electronics",
            "imageUrl": "https://example.com/business-laptop.jpg"
        },
        {
            "name": "Student Laptop Basic",
            "description": "Affordable laptop for students",
            "sku": "LAPTOP-STUDENT-001",
            "basePrice": 799.99,
            "category": "Electronics",
            "imageUrl": "https://example.com/student-laptop.jpg"
        }
    ]
    
    for product in products:
        try:
            response = requests.post(f"{BASE_URL}/api/products/", json=product, headers=headers)
            if response.status_code == 201:
                print(f"✅ Added product: {product['name']}")
            else:
                print(f"❌ Failed to add product {product['name']}: {response.status_code}")
        except Exception as e:
            print(f"❌ Error adding product {product['name']}: {e}")

def main():
    """Create the specific users and setup"""
    print("🚀 Creating AuroMart B2B Users and Workflow")
    print("=" * 60)
    
    # Step 1: Create Hrushi (Manufacturer)
    print("\n📝 Step 1: Creating Hrushi (Manufacturer)")
    hrushi_created = create_user(
        email="hrushiEaisehome@gmail.com",
        password="password123",
        firstName="Hrushi",
        lastName="Eaise",
        role="manufacturer",
        businessName="Hrushi Electronics"
    )
    
    # Step 2: Create Adity (Distributor)
    print("\n📝 Step 2: Creating Adity (Distributor)")
    adity_created = create_user(
        email="Adityakumar@kone.com",
        password="password123",
        firstName="Adity",
        lastName="Kumar",
        role="distributor",
        businessName="Adity Distribution Co"
    )
    
    if hrushi_created and adity_created:
        print("\n✅ Both users created successfully!")
        
        # Step 3: Login and add products
        print("\n📝 Step 3: Logging in and adding products")
        hrushi_token = login_user("hrushiEaisehome@gmail.com", "password123")
        
        if hrushi_token:
            print("\n📝 Step 4: Adding sample products for Hrushi")
            add_sample_products(hrushi_token)
        
        print("\n" + "=" * 60)
        print("✅ Setup Complete!")
        print("\n👤 Created Users:")
        print("  🏭 Manufacturer: hrushiEaisehome@gmail.com / password123")
        print("  🧑‍💼 Distributor: Adityakumar@kone.com / password123")
        print("  🏭 Existing: manufacturer@example.com / password123")
        
        print("\n🔄 Workflow:")
        print("  1. Hrushi (manufacturer) adds products")
        print("  2. Adity (distributor) sees Hrushi's products")
        print("  3. Adity places orders")
        print("  4. Hrushi receives and processes orders")
        
        print("\n🌐 Access:")
        print("  Frontend: http://localhost:3000")
        print("  Login with the credentials above")
        print("  Navigate to respective dashboards")
        
    else:
        print("❌ Failed to create users. Please check the errors above.")

if __name__ == "__main__":
    main()
