#!/usr/bin/env python3
"""
Create test retailer
"""

import requests
import json

BASE_URL = "http://localhost:5000/api"

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
            print(f"   Password: {retailer_data['password']}")
        else:
            print(f"⚠️  Test retailer might already exist: {response.status_code}")
    except Exception as e:
        print(f"❌ Error creating test retailer: {e}")

if __name__ == "__main__":
    create_retailer()
