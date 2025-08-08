#!/usr/bin/env python3
"""
Test script to verify partnership visibility
"""

import requests
import json
import time

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

def get_partners(token):
    """Get partners for the authenticated user"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BASE_URL}/partners/", headers=headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ Failed to get partners: {response.status_code} - {response.text}")
            return []
    except Exception as e:
        print(f"❌ Error getting partners: {e}")
        return []

def get_connected_distributors(token):
    """Get connected distributors for manufacturer"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BASE_URL}/partners/distributors", headers=headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ Failed to get connected distributors: {response.status_code} - {response.text}")
            return []
    except Exception as e:
        print(f"❌ Error getting connected distributors: {e}")
        return []

def get_available_partners(token):
    """Get available partners (not yet connected)"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BASE_URL}/partners/available", headers=headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ Failed to get available partners: {response.status_code} - {response.text}")
            return []
    except Exception as e:
        print(f"❌ Error getting available partners: {e}")
        return []

def main():
    print("🔍 Testing Partnership Visibility")
    print("=" * 50)
    
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
    
    # Test 1: Check Hrushi's connected distributors
    print("\n3. Checking Hrushi's connected distributors...")
    hrushi_connected = get_connected_distributors(hrushi_token)
    print(f"📊 Hrushi has {len(hrushi_connected)} connected distributors")
    
    adity_found = False
    for distributor in hrushi_connected:
        print(f"   - {distributor.get('business_name', 'N/A')} ({distributor.get('email', 'N/A')})")
        if distributor.get('email') == Adity_EMAIL:
            adity_found = True
            print(f"   ✅ Found Adity in connected distributors!")
    
    if not adity_found:
        print("   ❌ Adity not found in connected distributors")
    
    # Test 2: Check Hrushi's available partners
    print("\n4. Checking Hrushi's available partners...")
    hrushi_available = get_available_partners(hrushi_token)
    print(f"📊 Hrushi has {len(hrushi_available)} available partners")
    
    adity_in_available = False
    for partner in hrushi_available:
        print(f"   - {partner.get('business_name', 'N/A')} ({partner.get('email', 'N/A')})")
        if partner.get('email') == Adity_EMAIL:
            adity_in_available = True
            print(f"   ⚠️  Adity found in available partners (should not be here if connected)")
    
    if not adity_in_available:
        print("   ✅ Adity correctly removed from available partners")
    
    # Test 3: Check Adity's connected manufacturers
    print("\n5. Checking Adity's connected manufacturers...")
    adity_connected = get_partners(adity_token)
    print(f"📊 Adity has {len(adity_connected)} connected partners")
    
    hrushi_found = False
    for partner in adity_connected:
        print(f"   - {partner.get('business_name', 'N/A')} ({partner.get('email', 'N/A')})")
        if partner.get('email') == Hrushi_EMAIL:
            hrushi_found = True
            print(f"   ✅ Found Hrushi in connected partners!")
    
    if not hrushi_found:
        print("   ❌ Hrushi not found in connected partners")
    
    # Summary
    print("\n" + "=" * 50)
    print("📋 SUMMARY:")
    print(f"✅ Hrushi connected distributors: {len(hrushi_connected)}")
    print(f"✅ Adity in connected: {adity_found}")
    print(f"✅ Adity removed from available: {not adity_in_available}")
    print(f"✅ Adity connected partners: {len(adity_connected)}")
    print(f"✅ Hrushi in Adity's connected: {hrushi_found}")
    
    if adity_found and not adity_in_available and hrushi_found:
        print("\n🎉 SUCCESS: Partnership visibility is working correctly!")
        print("   - Hrushi can see Adity as a connected distributor")
        print("   - Adity is removed from available partners")
        print("   - Adity can see Hrushi as a connected manufacturer")
    else:
        print("\n❌ ISSUES FOUND:")
        if not adity_found:
            print("   - Adity not visible as connected distributor to Hrushi")
        if adity_in_available:
            print("   - Adity still appears in available partners")
        if not hrushi_found:
            print("   - Hrushi not visible as connected manufacturer to Adity")

if __name__ == "__main__":
    main()
