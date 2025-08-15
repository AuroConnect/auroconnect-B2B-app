#!/usr/bin/env python3
"""
Clean up database - keep only 4 test users (M1, M2, D1, D2) + 1 retailer
"""

import requests
import json
import time

BASE_URL = "http://localhost:5000/api"

def cleanup_database():
    """Clean up database to keep only test users"""
    
    print("🧹 Cleaning up database...")
    
    # Test users to keep
    users_to_keep = [
        "m1@auromart.com",
        "m2@auromart.com", 
        "d1@auromart.com",
        "d2@auromart.com"
    ]
    
    # First, let's create a test retailer if it doesn't exist
    retailer_data = {
        "email": "retailer1@auromart.com",
        "password": "password123",
        "firstName": "Test",
        "lastName": "Retailer",
        "businessName": "Test Retail Store",
        "phone": "+91-9876543214",
        "role": "retailer"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/register", json=retailer_data)
        if response.status_code == 201:
            print(f"✅ Created test retailer: {retailer_data['email']}")
            users_to_keep.append(retailer_data['email'])
        else:
            print(f"⚠️  Test retailer might already exist: {response.status_code}")
    except Exception as e:
        print(f"❌ Error creating test retailer: {e}")
    
    print(f"\n📋 Users to keep: {users_to_keep}")
    
    # Now we need to clean up the database directly
    # Since we can't easily do this via API, let's provide instructions
    print("\n🔧 Database cleanup instructions:")
    print("1. Stop the containers: docker-compose down")
    print("2. Remove the database volume: docker volume rm auroconnect-b2b-app_mysql_data")
    print("3. Start containers: docker-compose up -d")
    print("4. Run the test data script: python create_2x2_test_data.py")
    print("5. Create the retailer: python create_retailer.py")
    
    return users_to_keep

def create_retailer():
    """Create a test retailer"""
    retailer_data = {
        "email": "retailer1@auromart.com",
        "password": "password123",
        "firstName": "Test",
        "lastName": "Retailer",
        "businessName": "Test Retail Store",
        "phone": "+91-9876543214",
        "role": "retailer"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/register", json=retailer_data)
        if response.status_code == 201:
            print(f"✅ Created test retailer: {retailer_data['email']}")
        else:
            print(f"⚠️  Test retailer might already exist: {response.status_code}")
    except Exception as e:
        print(f"❌ Error creating test retailer: {e}")

if __name__ == "__main__":
    cleanup_database()
