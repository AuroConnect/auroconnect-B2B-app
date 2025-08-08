#!/usr/bin/env python3
"""
Test that the users exist and can login
"""

import requests
import json

# Configuration
BASE_URL = "http://localhost:5000"

def test_user_login(email, password):
    """Test user login"""
    login_data = {
        "email": email,
        "password": password
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
        if response.status_code == 200:
            user_data = response.json().get('user', {})
            print(f"✅ {email} - Login successful (ID: {user_data.get('id', 'N/A')})")
            return True
        else:
            print(f"❌ {email} - Login failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ {email} - Error: {e}")
        return False

def test_user_products(email, password):
    """Test user can view products"""
    login_data = {
        "email": email,
        "password": password
    }
    
    try:
        # Login first
        response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
        if response.status_code == 200:
            token = response.json().get('access_token')
            headers = {"Authorization": f"Bearer {token}"}
            
            # Get products
            response = requests.get(f"{BASE_URL}/api/products/", headers=headers)
            if response.status_code == 200:
                products = response.json().get('data', {}).get('products', [])
                print(f"✅ {email} - Can see {len(products)} products")
                return True
            else:
                print(f"❌ {email} - Cannot view products: {response.status_code}")
                return False
        else:
            print(f"❌ {email} - Login failed for product test")
            return False
    except Exception as e:
        print(f"❌ {email} - Error testing products: {e}")
        return False

def main():
    """Test all users"""
    print("🚀 Testing User Accounts")
    print("=" * 50)
    
    users = [
        ("hrushiEaisehome@gmail.com", "password123", "Hrushi (Manufacturer)"),
        ("Adityakumar@kone.com", "password123", "Adity (Distributor)"),
        ("manufacturer@example.com", "password123", "Existing Manufacturer")
    ]
    
    print("\n📝 Testing User Logins:")
    for email, password, name in users:
        test_user_login(email, password)
    
    print("\n📝 Testing Product Access:")
    for email, password, name in users:
        test_user_products(email, password)
    
    print("\n" + "=" * 50)
    print("✅ User Test Complete!")
    print("\n👤 Available Users:")
    print("  🏭 Hrushi: hrushiEaisehome@gmail.com / password123")
    print("  🧑‍💼 Adity: Adityakumar@kone.com / password123")
    print("  🏭 Existing: manufacturer@example.com / password123")
    
    print("\n🌐 Test in Browser:")
    print("  1. Go to: http://localhost:3000")
    print("  2. Login with any of the above accounts")
    print("  3. Navigate to respective dashboards")

if __name__ == "__main__":
    main()
