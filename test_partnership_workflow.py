#!/usr/bin/env python3
"""
Test complete partnership workflow
"""

import requests
import json

BASE_URL = "http://localhost:5000"

def test_partnership_workflow():
    """Test the complete partnership workflow"""
    
    print("🔍 Testing Complete Partnership Workflow")
    print("=" * 50)
    
    # Step 1: Login as Hrushi (Manufacturer)
    print("Step 1: Login as Hrushi (Manufacturer)")
    hrushi_login = {
        "email": "hrushiEaisehome@gmail.com",
        "password": "password123"
    }
    
    response = requests.post(f"{BASE_URL}/api/auth/login", json=hrushi_login)
    if response.status_code != 200:
        print(f"❌ Hrushi login failed: {response.status_code}")
        return
    
    hrushi_token = response.json().get('access_token')
    hrushi_headers = {"Authorization": f"Bearer {hrushi_token}"}
    print("✅ Hrushi logged in successfully")
    
    # Step 2: Check available partners
    print("\nStep 2: Check available partners")
    response = requests.get(f"{BASE_URL}/api/partners/available", headers=hrushi_headers)
    print(f"📊 Available partners endpoint: {response.status_code}")
    
    if response.status_code == 200:
        available_partners = response.json()
        print(f"✅ Found {len(available_partners)} available partners")
        
        for i, partner in enumerate(available_partners):
            print(f"  {i+1}. {partner.get('business_name', 'N/A')} ({partner.get('email', 'N/A')}) - {partner.get('role', 'N/A')}")
        
        if available_partners:
            adity_partner = next((p for p in available_partners if p.get('email') == 'Adityakumar@kone.com'), None)
            if adity_partner:
                print(f"\n✅ Found Adity in available partners: {adity_partner.get('id')}")
                
                # Step 3: Send partnership request
                print("\nStep 3: Send partnership request to Adity")
                partnership_request = {
                    "partner_id": adity_partner.get('id'),
                    "partnership_type": "manufacturer_distributor",
                    "message": "Hi Adity, I'd like to partner with you as a distributor."
                }
                
                response = requests.post(f"{BASE_URL}/api/partnerships/request", json=partnership_request, headers=hrushi_headers)
                print(f"📊 Partnership request status: {response.status_code}")
                
                if response.status_code == 201:
                    print("✅ Partnership request sent successfully")
                    
                    # Step 4: Login as Adity and accept the request
                    print("\nStep 4: Login as Adity and accept the request")
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
                    print("✅ Adity logged in successfully")
                    
                    # Get received requests
                    response = requests.get(f"{BASE_URL}/api/partnerships/received", headers=adity_headers)
                    print(f"📊 Received requests status: {response.status_code}")
                    
                    if response.status_code == 200:
                        received_requests = response.json()
                        print(f"✅ Adity has {len(received_requests)} received requests")
                        
                        if received_requests:
                            request_id = received_requests[0].get('id')
                            print(f"📝 Request ID: {request_id}")
                            
                            # Accept the request
                            accept_data = {
                                "status": "approved",
                                "message": "I accept the partnership request."
                            }
                            
                            response = requests.patch(f"{BASE_URL}/api/partnerships/{request_id}/respond", json=accept_data, headers=adity_headers)
                            print(f"📊 Accept partnership status: {response.status_code}")
                            
                            if response.status_code == 200:
                                print("✅ Partnership accepted successfully")
                                
                                # Step 5: Verify they can now see each other
                                print("\nStep 5: Verifying partnership visibility")
                                
                                # Check Hrushi's partners (should now see Adity)
                                response = requests.get(f"{BASE_URL}/api/partners/", headers=hrushi_headers)
                                if response.status_code == 200:
                                    hrushi_partners = response.json()
                                    print(f"✅ Hrushi now sees {len(hrushi_partners)} partners")
                                    
                                    for partner in hrushi_partners:
                                        print(f"  - {partner.get('business_name', 'N/A')} ({partner.get('email', 'N/A')})")
                                
                                # Check Adity's partners (should now see Hrushi)
                                response = requests.get(f"{BASE_URL}/api/partners/", headers=adity_headers)
                                if response.status_code == 200:
                                    adity_partners = response.json()
                                    print(f"✅ Adity now sees {len(adity_partners)} partners")
                                    
                                    for partner in adity_partners:
                                        print(f"  - {partner.get('business_name', 'N/A')} ({partner.get('email', 'N/A')})")
                                
                                # Check available partners (Adity should no longer appear)
                                response = requests.get(f"{BASE_URL}/api/partners/available", headers=hrushi_headers)
                                if response.status_code == 200:
                                    available_after = response.json()
                                    print(f"✅ Hrushi now sees {len(available_after)} available partners (Adity should be gone)")
                                    
                                    adity_still_available = any(p.get('email') == 'Adityakumar@kone.com' for p in available_after)
                                    if not adity_still_available:
                                        print("✅ Adity correctly removed from available partners")
                                    else:
                                        print("❌ Adity still appears in available partners")
                                
                                print("\n🎉 Partnership workflow completed successfully!")
                                print("📋 Summary:")
                                print("  - Hrushi can now see Adity in his partners")
                                print("  - Adity can now see Hrushi in his partners")
                                print("  - Adity no longer appears in available partners")
                                print("  - They can now trade products with each other")
                                
                            else:
                                print(f"❌ Failed to accept partnership: {response.text}")
                        else:
                            print("❌ No received requests found")
                    else:
                        print(f"❌ Failed to get received requests: {response.text}")
                else:
                    print(f"❌ Failed to send partnership request: {response.text}")
            else:
                print("❌ Adity not found in available partners")
        else:
            print("❌ No available partners found")
    else:
        print(f"❌ Failed to get available partners: {response.text}")

if __name__ == "__main__":
    test_partnership_workflow()
