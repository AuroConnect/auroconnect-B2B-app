#!/usr/bin/env python3
"""
Create partnership between Hrushi (Manufacturer) and Adity (Distributor)
"""

import requests
import json

# Configuration
BASE_URL = "http://localhost:5000/api"
Hrushi_EMAIL = "hrushiEaisehome@gmail.com"
Adity_EMAIL = "Adityakumar@kone.com"
PASSWORD = "password123"

def login_user(email, password):
    """Login user and return token"""
    try:
        response = requests.post(f"{BASE_URL}/auth/login", json={
            "email": email,
            "password": password
        })
        
        if response.status_code == 200:
            data = response.json()
            return data.get('access_token')
        else:
            print(f"❌ Login failed for {email}: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ Login error for {email}: {e}")
        return None

def get_user_id(token, email):
    """Get user ID by email"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BASE_URL}/users/profile", headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('email') == email:
                return data.get('id')
        return None
    except Exception as e:
        print(f"❌ Error getting user ID: {e}")
        return None

def create_partnership(token, partner_id, partnership_type):
    """Create partnership"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.post(f"{BASE_URL}/partners/", json={
            "partner_id": partner_id,
            "partnership_type": partnership_type
        }, headers=headers)
        
        if response.status_code == 201:
            print(f"✅ Partnership created successfully")
            return response.json()
        else:
            print(f"❌ Failed to create partnership: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error creating partnership: {e}")
        return None

def main():
    print("🤝 Creating Partnership between Hrushi and Adity")
    print("=" * 60)
    
    # Login Hrushi (Manufacturer)
    print(f"\n1. Logging in Hrushi ({Hrushi_EMAIL})...")
    hrushi_token = login_user(Hrushi_EMAIL, PASSWORD)
    if not hrushi_token:
        print("❌ Failed to login Hrushi")
        return
    
    print("✅ Hrushi logged in successfully")
    
    # Login Adity (Distributor)
    print(f"\n2. Logging in Adity ({Adity_EMAIL})...")
    adity_token = login_user(Adity_EMAIL, PASSWORD)
    if not adity_token:
        print("❌ Failed to login Adity")
        return
    
    print("✅ Adity logged in successfully")
    
    # Get Adity's user ID
    print(f"\n3. Getting Adity's user ID...")
    adity_id = get_user_id(adity_token, Adity_EMAIL)
    if not adity_id:
        print("❌ Failed to get Adity's user ID")
        return
    
    print(f"✅ Adity's user ID: {adity_id}")
    
    # Create partnership (Hrushi -> Adity)
    print(f"\n4. Creating partnership (Hrushi -> Adity)...")
    partnership = create_partnership(hrushi_token, adity_id, "manufacturer_distributor")
    if not partnership:
        print("❌ Failed to create partnership")
        return
    
    print("✅ Partnership created successfully!")
    print(f"   Partnership ID: {partnership.get('id')}")
    print(f"   Type: {partnership.get('partnership_type')}")
    print(f"   Status: {partnership.get('status')}")
    
    print("\n" + "=" * 60)
    print("🎉 SUCCESS: Partnership created between Hrushi and Adity!")
    print("   - Hrushi (Manufacturer) is now connected to Adity (Distributor)")
    print("   - They should now be able to see each other in their partner lists")
    print("   - Hrushi can add products that Adity can see")
    print("   - Adity can place orders to Hrushi")

if __name__ == "__main__":
    main()
