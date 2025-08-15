#!/usr/bin/env python3
"""
Create 2x2 Manufacturer-Distributor test data
"""

import requests
import json
import time

BASE_URL = "http://localhost:5000/api"

def create_test_data():
    """Create test manufacturers and distributors"""
    
    print("🔧 Creating 2x2 Manufacturer-Distributor test data...")
    
    # Test data
    test_users = [
        # Manufacturers
        {
            "email": "m1@auromart.com",
            "password": "password123",
            "firstName": "Tech",
            "lastName": "Manufacturer", 
            "businessName": "TechCorp Industries",
            "phone": "+91-9876543210",
            "role": "manufacturer"
        },
        {
            "email": "m2@auromart.com",
            "password": "password123",
            "firstName": "Fashion",
            "lastName": "Manufacturer",
            "businessName": "FashionHub Ltd", 
            "phone": "+91-9876543211",
            "role": "manufacturer"
        },
        # Distributors
        {
            "email": "d1@auromart.com",
            "password": "password123",
            "firstName": "Tech",
            "lastName": "Distributor",
            "businessName": "TechDist Solutions",
            "phone": "+91-9876543212", 
            "role": "distributor"
        },
        {
            "email": "d2@auromart.com",
            "password": "password123",
            "firstName": "Fashion",
            "lastName": "Distributor",
            "businessName": "FashionDist Pro",
            "phone": "+91-9876543213",
            "role": "distributor"
        }
    ]
    
    created_users = []
    
    for user_data in test_users:
        try:
            response = requests.post(f"{BASE_URL}/auth/register", json=user_data)
            if response.status_code == 201:
                print(f"✅ Created {user_data['role']}: {user_data['email']}")
                created_users.append(user_data)
            else:
                print(f"⚠️  User {user_data['email']} might already exist: {response.status_code}")
        except Exception as e:
            print(f"❌ Error creating {user_data['email']}: {e}")
    
    print(f"\n📋 Created {len(created_users)} test users")
    print("\n🔐 Login Credentials:")
    print("  All accounts use: password123")
    print("  Manufacturers: m1@auromart.com, m2@auromart.com")
    print("  Distributors: d1@auromart.com, d2@auromart.com")
    
    return created_users

if __name__ == "__main__":
    create_test_data()
