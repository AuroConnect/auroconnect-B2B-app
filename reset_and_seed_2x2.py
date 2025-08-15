#!/usr/bin/env python3
"""
Reset database and seed 2x2 organizations (M1, M2, D1, D2)
"""

import requests
import json
import time

BASE_URL = "http://localhost:5000/api"

def reset_and_seed_2x2():
    """Reset database and create 2x2 organizations"""
    
    print("Resetting Database and Creating 2x2 Organizations...")
    
    # Step 1: Create the 4 organizations
    organizations = [
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
    
    for org in organizations:
        try:
            print(f"Creating {org['role']}: {org['email']}...")
            response = requests.post(f"{BASE_URL}/auth/register", json=org, timeout=10)
            
            if response.status_code == 201:
                print(f"Created {org['role']}: {org['email']}")
                created_users.append(org)
            elif response.status_code == 409:
                print(f"  {org['email']} already exists, skipping...")
                created_users.append(org)
            else:
                print(f"Failed to create {org['email']}: {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data.get('message', 'Unknown error')}")
                except:
                    print(f"   Error: {response.text[:100]}")
                    
        except Exception as e:
            print(f"Error creating {org['email']}: {e}")
    
    print(f"\nSummary:")
    print(f"Created/Found {len(created_users)} organizations")
    print(f"\nLogin Credentials:")
    print("  All accounts use: password123")
    print("  Manufacturers: m1@auromart.com, m2@auromart.com")
    print("  Distributors: d1@auromart.com, d2@auromart.com")
    
    return created_users

if __name__ == "__main__":
    reset_and_seed_2x2()
