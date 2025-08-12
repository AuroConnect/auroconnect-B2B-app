#!/usr/bin/env python3
"""
Simple Seed Data Script for AuroMart B2B Platform
"""

import requests
import json
import time

BASE_URL = "http://localhost:5000/api"
HEADERS = {"Content-Type": "application/json"}

def create_user(user_data):
    try:
        response = requests.post(f"{BASE_URL}/auth/register", json=user_data, headers=HEADERS)
        if response.status_code == 201:
            print(f"✅ Created user: {user_data['email']}")
            return response.json()
        else:
            print(f"❌ Failed to create user {user_data['email']}: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error creating user {user_data['email']}: {e}")
        return None

def login_user(email, password):
    try:
        response = requests.post(f"{BASE_URL}/auth/login", json={
            "email": email,
            "password": password
        }, headers=HEADERS)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Logged in: {email}")
            return data.get('access_token')
        else:
            print(f"❌ Failed to login {email}: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error logging in {email}: {e}")
        return None

def main():
    print("🚀 Creating Demo Users for AuroMart B2B Platform")
    print("=" * 50)
    
    # Create demo users
    demo_users = [
        {
            "firstName": "Auro",
            "lastName": "Manufacturer",
            "email": "m@demo.com",
            "password": "Demo@123",
            "role": "manufacturer",
            "businessName": "Auro Manufacturing Co.",
            "phoneNumber": "+91-9876543210",
            "address": "123 Industrial Area, Mumbai, Maharashtra",
            "gstNumber": "27AABCA1234A1Z5"
        },
        {
            "firstName": "Auro",
            "lastName": "Distributor", 
            "email": "d@demo.com",
            "password": "Demo@123",
            "role": "distributor",
            "businessName": "Auro Distribution Ltd.",
            "phoneNumber": "+91-9876543211",
            "address": "456 Business Park, Delhi, NCR",
            "gstNumber": "07AABCA5678B2Z6"
        },
        {
            "firstName": "Auro",
            "lastName": "Retailer",
            "email": "r@demo.com", 
            "password": "Demo@123",
            "role": "retailer",
            "businessName": "Auro Retail Store",
            "phoneNumber": "+91-9876543212",
            "address": "789 Shopping Center, Bangalore, Karnataka",
            "gstNumber": "29AABCA9012C3Z7"
        }
    ]
    
    for user_data in demo_users:
        create_user(user_data)
        time.sleep(1)
    
    print("\n🎉 Demo Users Created!")
    print("=" * 50)
    print("\n📋 Demo Account Details:")
    print("Manufacturer: m@demo.com / Demo@123")
    print("Distributor:  d@demo.com / Demo@123") 
    print("Retailer:     r@demo.com / Demo@123")
    print("\n🔗 Test URLs:")
    print("Frontend: http://localhost:3000")
    print("Backend API: http://localhost:5000/api/health")

if __name__ == "__main__":
    main()
