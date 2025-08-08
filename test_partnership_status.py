#!/usr/bin/env python3
"""
Test partnership status and visibility
"""

import requests
import json

BASE_URL = "http://localhost:5000"

def test_partnership_status():
    """Test current partnership status"""
    
    # Test Hrushi's partners
    print("🔍 Testing Hrushi's (Manufacturer) Partners")
    print("=" * 50)
    
    # Login as Hrushi
    hrushi_login = {
        "email": "hrushiEaisehome@gmail.com",
        "password": "password123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/auth/login", json=hrushi_login)
        if response.status_code != 200:
            print(f"❌ Hrushi login failed: {response.status_code}")
            return
        
        hrushi_token = response.json().get('access_token')
        hrushi_headers = {"Authorization": f"Bearer {hrushi_token}"}
        
        # Get Hrushi's partners
        response = requests.get(f"{BASE_URL}/api/partners/", headers=hrushi_headers)
        print(f"📊 Hrushi's partners endpoint: {response.status_code}")
        
        if response.status_code == 200:
            partners = response.json()
            print(f"✅ Hrushi sees {len(partners)} partners")
            
            for i, partner in enumerate(partners):
                print(f"  {i+1}. {partner.get('business_name', 'N/A')} ({partner.get('email', 'N/A')}) - {partner.get('role', 'N/A')}")
        else:
            print(f"❌ Failed to get Hrushi's partners: {response.text}")
        
        # Test Adity's partners
        print("\n🔍 Testing Adity's (Distributor) Partners")
        print("=" * 50)
        
        # Login as Adity
        adity_login = {
            "email": "Adityakumar@kone.com",
            "password": "password123"
        }
        
        response = requests.post(f"{BASE_URL}/api/auth/login", json=adity_login)
        if response.status_code != 200:
            print(f"❌ Adity login failed: {response.status_code}")
            return
        
        adity_token = response.json().get('access_token')
        adity_headers = {"Authorization": f"Bearer {adity_token}"}
        
        # Get Adity's partners
        response = requests.get(f"{BASE_URL}/api/partners/", headers=adity_headers)
        print(f"📊 Adity's partners endpoint: {response.status_code}")
        
        if response.status_code == 200:
            partners = response.json()
            print(f"✅ Adity sees {len(partners)} partners")
            
            for i, partner in enumerate(partners):
                print(f"  {i+1}. {partner.get('business_name', 'N/A')} ({partner.get('email', 'N/A')}) - {partner.get('role', 'N/A')}")
        else:
            print(f"❌ Failed to get Adity's partners: {response.text}")
        
        # Test partnership creation
        print("\n🔍 Testing Partnership Creation")
        print("=" * 50)
        
        # Create partnership between Hrushi and Adity
        partnership_data = {
            "partner_id": "Adityakumar@kone.com",  # Adity's email
            "partnership_type": "manufacturer_distributor"
        }
        
        response = requests.post(f"{BASE_URL}/api/partnerships/request", json=partnership_data, headers=hrushi_headers)
        print(f"📊 Partnership request: {response.status_code}")
        
        if response.status_code == 201:
            print("✅ Partnership request created successfully")
        else:
            print(f"❌ Partnership request failed: {response.text}")
        
        # Test available partners (should show unconnected partners)
        print("\n🔍 Testing Available Partners")
        print("=" * 50)
        
        response = requests.get(f"{BASE_URL}/api/partners/available", headers=hrushi_headers)
        print(f"📊 Available partners endpoint: {response.status_code}")
        
        if response.status_code == 200:
            available = response.json()
            print(f"✅ Found {len(available)} available partners")
            
            for i, partner in enumerate(available):
                print(f"  {i+1}. {partner.get('business_name', 'N/A')} ({partner.get('email', 'N/A')}) - {partner.get('role', 'N/A')}")
        else:
            print(f"❌ Failed to get available partners: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def test_partnership_workflow():
    """Test the complete partnership workflow"""
    
    print("\n🔍 Testing Complete Partnership Workflow")
    print("=" * 50)
    
    # Step 1: Hrushi sends partnership request to Adity
    print("Step 1: Hrushi sends partnership request to Adity")
    
    hrushi_login = {
        "email": "hrushiEaisehome@gmail.com",
        "password": "password123"
    }
    
    response = requests.post(f"{BASE_URL}/api/auth/login", json=hrushi_login)
    hrushi_token = response.json().get('access_token')
    hrushi_headers = {"Authorization": f"Bearer {hrushi_token}"}
    
    # Get Adity's user ID
    adity_login = {
        "email": "Adityakumar@kone.com",
        "password": "password123"
    }
    
    response = requests.post(f"{BASE_URL}/api/auth/login", json=adity_login)
    adity_token = response.json().get('access_token')
    adity_headers = {"Authorization": f"Bearer {adity_token}"}
    
    # Get user info to find Adity's ID
    response = requests.get(f"{BASE_URL}/api/auth/user", headers=adity_headers)
    if response.status_code == 200:
        adity_user = response.json()
        adity_id = adity_user.get('id')
        
        print(f"✅ Found Adity's ID: {adity_id}")
        
        # Send partnership request
        partnership_request = {
            "partner_id": adity_id,
            "partnership_type": "manufacturer_distributor",
            "message": "Hi Adity, I'd like to partner with you as a distributor."
        }
        
        response = requests.post(f"{BASE_URL}/api/partnerships/request", json=partnership_request, headers=hrushi_headers)
        print(f"📊 Partnership request status: {response.status_code}")
        
        if response.status_code == 201:
            print("✅ Partnership request sent successfully")
            
            # Step 2: Adity accepts the partnership
            print("\nStep 2: Adity accepts the partnership")
            
            # Get received requests
            response = requests.get(f"{BASE_URL}/api/partnerships/received", headers=adity_headers)
            if response.status_code == 200:
                received_requests = response.json()
                print(f"✅ Adity has {len(received_requests)} received requests")
                
                if received_requests:
                    request_id = received_requests[0].get('id')
                    
                    # Accept the request
                    accept_data = {
                        "status": "approved",
                        "message": "I accept the partnership request."
                    }
                    
                    response = requests.patch(f"{BASE_URL}/api/partnerships/{request_id}/respond", json=accept_data, headers=adity_headers)
                    print(f"📊 Accept partnership status: {response.status_code}")
                    
                    if response.status_code == 200:
                        print("✅ Partnership accepted successfully")
                        
                        # Step 3: Verify they can now see each other
                        print("\nStep 3: Verifying partnership visibility")
                        
                        # Check Hrushi's partners
                        response = requests.get(f"{BASE_URL}/api/partners/", headers=hrushi_headers)
                        if response.status_code == 200:
                            hrushi_partners = response.json()
                            print(f"✅ Hrushi now sees {len(hrushi_partners)} partners")
                        
                        # Check Adity's partners
                        response = requests.get(f"{BASE_URL}/api/partners/", headers=adity_headers)
                        if response.status_code == 200:
                            adity_partners = response.json()
                            print(f"✅ Adity now sees {len(adity_partners)} partners")
                    else:
                        print(f"❌ Failed to accept partnership: {response.text}")
                else:
                    print("❌ No received requests found")
            else:
                print(f"❌ Failed to get received requests: {response.text}")
        else:
            print(f"❌ Failed to send partnership request: {response.text}")
    else:
        print(f"❌ Failed to get Adity's user info: {response.text}")

if __name__ == "__main__":
    print("🔍 Testing Partnership Status and Workflow")
    print("=" * 60)
    
    test_partnership_status()
    test_partnership_workflow()
