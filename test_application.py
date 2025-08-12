#!/usr/bin/env python3
"""
Comprehensive Application Test Script for AuroMart B2B Platform
Tests all major functionality and endpoints
"""

import requests
import json
import time
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:5000/api"
FRONTEND_URL = "http://localhost:3000"
HEADERS = {"Content-Type": "application/json"}

def test_backend_health():
    """Test backend health endpoint"""
    print("🔍 Testing Backend Health...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ Backend is healthy")
            return True
        else:
            print(f"❌ Backend health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Backend health check error: {e}")
        return False

def test_frontend_access():
    """Test frontend accessibility"""
    print("🔍 Testing Frontend Access...")
    try:
        response = requests.get(FRONTEND_URL)
        if response.status_code == 200:
            print("✅ Frontend is accessible")
            return True
        else:
            print(f"❌ Frontend access failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Frontend access error: {e}")
        return False

def test_authentication():
    """Test user authentication"""
    print("🔍 Testing Authentication...")
    
    # Test login for each demo user
    demo_users = [
        {"email": "m@demo.com", "password": "Demo@123", "role": "Manufacturer"},
        {"email": "d@demo.com", "password": "Demo@123", "role": "Distributor"},
        {"email": "r@demo.com", "password": "Demo@123", "role": "Retailer"}
    ]
    
    tokens = {}
    for user in demo_users:
        try:
            response = requests.post(f"{BASE_URL}/auth/login", json={
                "email": user["email"],
                "password": user["password"]
            }, headers=HEADERS)
            
            if response.status_code == 200:
                data = response.json()
                tokens[user["email"]] = data.get('access_token')
                print(f"✅ {user['role']} login successful")
            else:
                print(f"❌ {user['role']} login failed: {response.text}")
                return False
        except Exception as e:
            print(f"❌ {user['role']} login error: {e}")
            return False
    
    return tokens

def test_products_api(tokens):
    """Test products API for each role"""
    print("🔍 Testing Products API...")
    
    for email, token in tokens.items():
        try:
            headers = {**HEADERS, "Authorization": f"Bearer {token}"}
            response = requests.get(f"{BASE_URL}/products", headers=headers)
            
            if response.status_code == 200:
                products = response.json()
                print(f"✅ {email}: Found {len(products)} products")
            else:
                print(f"❌ {email}: Products API failed: {response.text}")
                return False
        except Exception as e:
            print(f"❌ {email}: Products API error: {e}")
            return False
    
    return True

def test_categories_api():
    """Test categories API"""
    print("🔍 Testing Categories API...")
    try:
        response = requests.get(f"{BASE_URL}/products/categories", headers=HEADERS)
        if response.status_code == 200:
            categories = response.json()
            print(f"✅ Found {len(categories)} categories")
            return True
        else:
            print(f"❌ Categories API failed: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Categories API error: {e}")
        return False

def test_orders_api(tokens):
    """Test orders API for each role"""
    print("🔍 Testing Orders API...")
    
    for email, token in tokens.items():
        try:
            headers = {**HEADERS, "Authorization": f"Bearer {token}"}
            response = requests.get(f"{BASE_URL}/orders", headers=headers)
            
            if response.status_code == 200:
                orders = response.json()
                print(f"✅ {email}: Found {len(orders)} orders")
            else:
                print(f"❌ {email}: Orders API failed: {response.text}")
                return False
        except Exception as e:
            print(f"❌ {email}: Orders API error: {e}")
            return False
    
    return True

def test_partners_api(tokens):
    """Test partners API for each role"""
    print("🔍 Testing Partners API...")
    
    for email, token in tokens.items():
        try:
            headers = {**HEADERS, "Authorization": f"Bearer {token}"}
            response = requests.get(f"{BASE_URL}/partners", headers=headers)
            
            if response.status_code == 200:
                partners = response.json()
                print(f"✅ {email}: Found {len(partners)} partners")
            else:
                print(f"❌ {email}: Partners API failed: {response.text}")
                return False
        except Exception as e:
            print(f"❌ {email}: Partners API error: {e}")
            return False
    
    return True

def test_cart_api(tokens):
    """Test cart API for each role"""
    print("🔍 Testing Cart API...")
    
    for email, token in tokens.items():
        try:
            headers = {**HEADERS, "Authorization": f"Bearer {token}"}
            response = requests.get(f"{BASE_URL}/cart", headers=headers)
            
            if response.status_code == 200:
                cart_items = response.json()
                print(f"✅ {email}: Cart has {len(cart_items)} items")
            else:
                print(f"❌ {email}: Cart API failed: {response.text}")
                return False
        except Exception as e:
            print(f"❌ {email}: Cart API error: {e}")
            return False
    
    return True

def main():
    """Run comprehensive application tests"""
    print("🚀 AuroMart B2B Platform - Comprehensive Test Suite")
    print("=" * 60)
    print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Test results tracking
    tests_passed = 0
    total_tests = 0
    
    # Test 1: Backend Health
    total_tests += 1
    if test_backend_health():
        tests_passed += 1
    print()
    
    # Test 2: Frontend Access
    total_tests += 1
    if test_frontend_access():
        tests_passed += 1
    print()
    
    # Test 3: Authentication
    total_tests += 1
    tokens = test_authentication()
    if tokens:
        tests_passed += 1
    print()
    
    # Test 4: Categories API
    total_tests += 1
    if test_categories_api():
        tests_passed += 1
    print()
    
    # Test 5: Products API (if authentication passed)
    if tokens:
        total_tests += 1
        if test_products_api(tokens):
            tests_passed += 1
        print()
        
        # Test 6: Orders API
        total_tests += 1
        if test_orders_api(tokens):
            tests_passed += 1
        print()
        
        # Test 7: Partners API
        total_tests += 1
        if test_partners_api(tokens):
            tests_passed += 1
        print()
        
        # Test 8: Cart API
        total_tests += 1
        if test_cart_api(tokens):
            tests_passed += 1
        print()
    
    # Final Results
    print("=" * 60)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 60)
    print(f"✅ Tests Passed: {tests_passed}/{total_tests}")
    print(f"❌ Tests Failed: {total_tests - tests_passed}/{total_tests}")
    print(f"📈 Success Rate: {(tests_passed/total_tests)*100:.1f}%")
    print()
    
    if tests_passed == total_tests:
        print("🎉 ALL TESTS PASSED! Application is working correctly.")
        print()
        print("🔗 Application URLs:")
        print(f"   Frontend: {FRONTEND_URL}")
        print(f"   Backend API: {BASE_URL}/health")
        print()
        print("👤 Demo Accounts:")
        print("   Manufacturer: m@demo.com / Demo@123")
        print("   Distributor:  d@demo.com / Demo@123")
        print("   Retailer:     r@demo.com / Demo@123")
        print()
        print("✅ The AuroMart B2B platform is ready for use!")
    else:
        print("⚠️  Some tests failed. Please check the application configuration.")
        print("   Check Docker containers are running: docker ps")
        print("   Check backend logs: docker-compose logs backend")
        print("   Check frontend logs: docker-compose logs frontend")

if __name__ == "__main__":
    main()
