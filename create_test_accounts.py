#!/usr/bin/env python3
"""
Create 3 real test accounts for AuroMart
"""

import requests
import json
import sys
import time

# Configuration
API_BASE_URL = "http://localhost:5000"

# Test accounts to create
TEST_ACCOUNTS = [
    {
        "email": "retailer@auromart.com",
        "firstName": "John",
        "lastName": "Retailer",
        "password": "password123",
        "role": "retailer",
        "businessName": "TechMart Electronics",
        "address": "123 Main Street, Mumbai, Maharashtra",
        "phoneNumber": "+91-9876543210",
        "whatsappNumber": "+91-9876543210"
    },
    {
        "email": "distributor@auromart.com",
        "firstName": "Sarah",
        "lastName": "Distributor",
        "password": "password123",
        "role": "distributor",
        "businessName": "Global Distribution Co",
        "address": "456 Business Avenue, Delhi, Delhi",
        "phoneNumber": "+91-9876543211",
        "whatsappNumber": "+91-9876543211"
    },
    {
        "email": "manufacturer@auromart.com",
        "firstName": "Mike",
        "lastName": "Manufacturer",
        "password": "password123",
        "role": "manufacturer",
        "businessName": "AuroMart Manufacturing",
        "address": "789 Industrial Boulevard, Pune, Maharashtra",
        "phoneNumber": "+91-9876543212",
        "whatsappNumber": "+91-9876543212"
    }
]

def wait_for_server():
    """Wait for the server to be ready"""
    print("⏳ Waiting for server to be ready...")
    max_attempts = 30
    for attempt in range(max_attempts):
        try:
            response = requests.get(f"{API_BASE_URL}/api/health", timeout=5)
            if response.status_code == 200:
                print("✅ Server is ready!")
                return True
        except:
            pass
        print(f"⏳ Attempt {attempt + 1}/{max_attempts} - Server not ready yet...")
        time.sleep(2)
    
    print("❌ Server not ready after maximum attempts")
    return False

def create_account(account_data):
    """Create a single account"""
    try:
        print(f"\n🔐 Creating {account_data['role']} account: {account_data['email']}")
        
        response = requests.post(
            f"{API_BASE_URL}/api/auth/register",
            json=account_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        print(f"Response Status: {response.status_code}")
        
        if response.status_code == 201:
            print(f"✅ {account_data['role'].title()} account created successfully!")
            return True
        elif response.status_code == 409:
            print(f"⚠️  {account_data['role'].title()} account already exists")
            return True
        else:
            print(f"❌ Failed to create {account_data['role']} account")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error creating {account_data['role']} account: {e}")
        return False

def test_login(account_data):
    """Test login for an account"""
    try:
        print(f"\n🔑 Testing login for: {account_data['email']}")
        
        login_data = {
            "email": account_data["email"],
            "password": account_data["password"]
        }
        
        response = requests.post(
            f"{API_BASE_URL}/api/auth/login",
            json=login_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        print(f"Login Response Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if "access_token" in data:
                print(f"✅ Login successful for {account_data['email']}")
                print(f"   Role: {data['user']['role']}")
                print(f"   Business: {data['user']['businessName']}")
                return True
            else:
                print(f"❌ Login response missing access token")
                return False
        else:
            print(f"❌ Login failed for {account_data['email']}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing login for {account_data['email']}: {e}")
        return False

def main():
    """Main function to create and test accounts"""
    print("🚀 AuroMart Test Account Creation")
    print("=" * 50)
    print(f"API Base URL: {API_BASE_URL}")
    print()
    
    # Wait for server to be ready
    if not wait_for_server():
        print("\n❌ Cannot connect to server. Please start the backend first:")
        print("   docker-compose up backend")
        sys.exit(1)
    
    # Create accounts
    print("\n📝 Creating Test Accounts...")
    print("=" * 50)
    
    created_count = 0
    for account in TEST_ACCOUNTS:
        if create_account(account):
            created_count += 1
    
    print(f"\n✅ Created/Verified {created_count}/{len(TEST_ACCOUNTS)} accounts")
    
    # Test logins
    print("\n🔑 Testing Account Logins...")
    print("=" * 50)
    
    login_success_count = 0
    for account in TEST_ACCOUNTS:
        if test_login(account):
            login_success_count += 1
    
    print(f"\n✅ Login successful for {login_success_count}/{len(TEST_ACCOUNTS)} accounts")
    
    # Summary
    print("\n" + "=" * 50)
    print("📋 TEST ACCOUNT SUMMARY")
    print("=" * 50)
    
    for account in TEST_ACCOUNTS:
        print(f"👤 {account['role'].title()}:")
        print(f"   Email: {account['email']}")
        print(f"   Password: {account['password']}")
        print(f"   Business: {account['businessName']}")
        print()
    
    print("🌐 Access the application at: http://localhost:3000")
    print("🔗 Backend API at: http://localhost:5000")
    print()
    print("🎉 Test accounts are ready! You can now:")
    print("   1. Go to http://localhost:3000")
    print("   2. Click 'Sign up here' or go to /register")
    print("   3. Use any of the accounts above to login")
    print("   4. Test different user roles and features")

if __name__ == "__main__":
    main()
