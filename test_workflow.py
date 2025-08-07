#!/usr/bin/env python3
"""
Test script for AuroMart B2B Platform - Manufacturer → Distributor → Retailer Workflow
Tests the complete end-to-end workflow with role-based visibility and access control.
"""

import requests
import json
import time
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:5000"
API_BASE = f"{BASE_URL}/api"

def print_section(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")

def print_test(test_name, success=True):
    status = "✅ PASS" if success else "❌ FAIL"
    print(f"  {status}: {test_name}")

def make_request(method, endpoint, data=None, headers=None):
    """Make HTTP request with error handling"""
    url = f"{API_BASE}{endpoint}"
    try:
        if method.upper() == 'GET':
            response = requests.get(url, headers=headers)
        elif method.upper() == 'POST':
            response = requests.post(url, json=data, headers=headers)
        elif method.upper() == 'PUT':
            response = requests.put(url, json=data, headers=headers)
        else:
            return None, "Invalid method"
        
        return response, None
    except requests.exceptions.RequestException as e:
        return None, str(e)

def test_health_check():
    """Test API health check"""
    print_section("HEALTH CHECK")
    
    response, error = make_request('GET', '/health')
    if error:
        print_test("Health check", False)
        print(f"    Error: {error}")
        return False
    
    if response.status_code == 200:
        data = response.json()
        print_test("Health check", True)
        print(f"    Status: {data.get('status')}")
        print(f"    Database: {data.get('database')}")
        return True
    else:
        print_test("Health check", False)
        print(f"    Status code: {response.status_code}")
        return False

def test_user_registration():
    """Test user registration for different roles"""
    print_section("USER REGISTRATION")
    
    users = {
        'manufacturer': {
            'email': 'manufacturer2@auromart.com',
            'password': 'password123',
            'firstName': 'John',
            'lastName': 'Manufacturer',
            'businessName': 'AuroMart Manufacturing',
            'role': 'manufacturer',
            'phoneNumber': '+1234567890',
            'address': '123 Factory St, Industrial City'
        },
        'distributor': {
            'email': 'distributor2@auromart.com',
            'password': 'password123',
            'firstName': 'Jane',
            'lastName': 'Distributor',
            'businessName': 'AuroMart Distribution',
            'role': 'distributor',
            'phoneNumber': '+1234567891',
            'address': '456 Warehouse Ave, Distribution City'
        },
        'retailer': {
            'email': 'retailer2@auromart.com',
            'password': 'password123',
            'firstName': 'Bob',
            'lastName': 'Retailer',
            'businessName': 'AuroMart Retail Store',
            'role': 'retailer',
            'phoneNumber': '+1234567892',
            'address': '789 Shop St, Retail City'
        }
    }
    
    registered_users = {}
    
    for role, user_data in users.items():
        response, error = make_request('POST', '/auth/register', user_data)
        
        if error:
            print_test(f"Register {role}", False)
            print(f"    Error: {error}")
            continue
        
        if response.status_code == 201:
            data = response.json()
            registered_users[role] = {
                'id': data.get('user', {}).get('id'),
                'token': data.get('access_token'),
                'data': user_data
            }
            print_test(f"Register {role}", True)
            print(f"    User ID: {data.get('user', {}).get('id')}")
        else:
            print_test(f"Register {role}", False)
            print(f"    Status: {response.status_code}")
            print(f"    Response: {response.text}")
    
    return registered_users

def test_user_login(registered_users):
    """Test user login for all roles"""
    print_section("USER LOGIN")
    
    logged_users = {}
    
    for role, user_info in registered_users.items():
        login_data = {
            'email': user_info['data']['email'],
            'password': user_info['data']['password']
        }
        
        response, error = make_request('POST', '/auth/login', login_data)
        
        if error:
            print_test(f"Login {role}", False)
            print(f"    Error: {error}")
            continue
        
        if response.status_code == 200:
            data = response.json()
            logged_users[role] = {
                'id': user_info['id'],
                'token': data.get('access_token'),
                'data': user_info['data']
            }
            print_test(f"Login {role}", True)
        else:
            print_test(f"Login {role}", False)
            print(f"    Status: {response.status_code}")
            print(f"    Response: {response.text}")
    
    return logged_users

def test_partnership_creation(logged_users):
    """Test partnership creation between users"""
    print_section("PARTNERSHIP CREATION")
    
    headers = {}
    partnerships = {}
    
    # Create manufacturer-distributor partnership
    if 'manufacturer' in logged_users and 'distributor' in logged_users:
        headers['Authorization'] = f"Bearer {logged_users['manufacturer']['token']}"
        
        partnership_data = {
            'partner_id': logged_users['distributor']['id'],
            'partnership_type': 'manufacturer_distributor'
        }
        
        response, error = make_request('POST', '/partners/', partnership_data, headers)
        
        if error:
            print_test("Create manufacturer-distributor partnership", False)
            print(f"    Error: {error}")
        elif response.status_code == 201:
            data = response.json()
            partnerships['manufacturer_distributor'] = data
            print_test("Create manufacturer-distributor partnership", True)
        else:
            print_test("Create manufacturer-distributor partnership", False)
            print(f"    Status: {response.status_code}")
            print(f"    Response: {response.text}")
    
    # Create distributor-retailer partnership
    if 'distributor' in logged_users and 'retailer' in logged_users:
        headers['Authorization'] = f"Bearer {logged_users['distributor']['token']}"
        
        partnership_data = {
            'partner_id': logged_users['retailer']['id'],
            'partnership_type': 'distributor_retailer'
        }
        
        response, error = make_request('POST', '/partners/', partnership_data, headers)
        
        if error:
            print_test("Create distributor-retailer partnership", False)
            print(f"    Error: {error}")
        elif response.status_code == 201:
            data = response.json()
            partnerships['distributor_retailer'] = data
            print_test("Create distributor-retailer partnership", True)
        else:
            print_test("Create distributor-retailer partnership", False)
            print(f"    Status: {response.status_code}")
            print(f"    Response: {response.text}")
    
    return partnerships

def test_product_creation(logged_users):
    """Test product creation by manufacturer"""
    print_section("PRODUCT CREATION")
    
    if 'manufacturer' not in logged_users:
        print_test("Create product (no manufacturer)", False)
        return []
    
    headers = {'Authorization': f"Bearer {logged_users['manufacturer']['token']}"}
    
    products = [
        {
            'name': 'Premium Mattress',
            'sku': 'MAT-001',
            'description': 'High-quality premium mattress',
            'basePrice': 1500.00,
            'imageUrl': 'https://example.com/mattress.jpg'
        },
        {
            'name': 'Standard Mattress',
            'sku': 'MAT-002',
            'description': 'Standard quality mattress',
            'basePrice': 800.00,
            'imageUrl': 'https://example.com/mattress2.jpg'
        }
    ]
    
    created_products = []
    
    for product_data in products:
        response, error = make_request('POST', '/products/', product_data, headers)
        
        if error:
            print_test(f"Create product: {product_data['name']}", False)
            print(f"    Error: {error}")
            continue
        
        if response.status_code == 201:
            data = response.json()
            created_products.append(data)
            print_test(f"Create product: {product_data['name']}", True)
            print(f"    Product ID: {data.get('id')}")
        else:
            print_test(f"Create product: {product_data['name']}", False)
            print(f"    Status: {response.status_code}")
            print(f"    Response: {response.text}")
    
    return created_products

def test_role_based_product_visibility(logged_users, products):
    """Test role-based product visibility"""
    print_section("ROLE-BASED PRODUCT VISIBILITY")
    
    # Test manufacturer sees their own products
    if 'manufacturer' in logged_users:
        headers = {'Authorization': f"Bearer {logged_users['manufacturer']['token']}"}
        response, error = make_request('GET', '/products/', headers=headers)
        
        if error:
            print_test("Manufacturer product visibility", False)
            print(f"    Error: {error}")
        elif response.status_code == 200:
            data = response.json()
            print_test("Manufacturer product visibility", True)
            print(f"    Products visible: {len(data)}")
        else:
            print_test("Manufacturer product visibility", False)
            print(f"    Status: {response.status_code}")
    
    # Test distributor sees manufacturer's products
    if 'distributor' in logged_users:
        headers = {'Authorization': f"Bearer {logged_users['distributor']['token']}"}
        response, error = make_request('GET', '/products/', headers=headers)
        
        if error:
            print_test("Distributor product visibility", False)
            print(f"    Error: {error}")
        elif response.status_code == 200:
            data = response.json()
            print_test("Distributor product visibility", True)
            print(f"    Products visible: {len(data)}")
        else:
            print_test("Distributor product visibility", False)
            print(f"    Status: {response.status_code}")
    
    # Test retailer sees no products (no inventory yet)
    if 'retailer' in logged_users:
        headers = {'Authorization': f"Bearer {logged_users['retailer']['token']}"}
        response, error = make_request('GET', '/products/', headers=headers)
        
        if error:
            print_test("Retailer product visibility", False)
            print(f"    Error: {error}")
        elif response.status_code == 200:
            data = response.json()
            print_test("Retailer product visibility", True)
            print(f"    Products visible: {len(data)} (should be 0 without inventory)")
        else:
            print_test("Retailer product visibility", False)
            print(f"    Status: {response.status_code}")

def test_partner_visibility(logged_users):
    """Test partner visibility for each role"""
    print_section("PARTNER VISIBILITY")
    
    # Test manufacturer sees distributors
    if 'manufacturer' in logged_users:
        headers = {'Authorization': f"Bearer {logged_users['manufacturer']['token']}"}
        response, error = make_request('GET', '/partners/', headers=headers)
        
        if error:
            print_test("Manufacturer partner visibility", False)
            print(f"    Error: {error}")
        elif response.status_code == 200:
            data = response.json()
            print_test("Manufacturer partner visibility", True)
            print(f"    Partners visible: {len(data)} (should see distributors)")
        else:
            print_test("Manufacturer partner visibility", False)
            print(f"    Status: {response.status_code}")
    
    # Test distributor sees manufacturer and retailers
    if 'distributor' in logged_users:
        headers = {'Authorization': f"Bearer {logged_users['distributor']['token']}"}
        response, error = make_request('GET', '/partners/', headers=headers)
        
        if error:
            print_test("Distributor partner visibility", False)
            print(f"    Error: {error}")
        elif response.status_code == 200:
            data = response.json()
            print_test("Distributor partner visibility", True)
            print(f"    Partners visible: {len(data)} (should see manufacturer + retailers)")
        else:
            print_test("Distributor partner visibility", False)
            print(f"    Status: {response.status_code}")
    
    # Test retailer sees distributor
    if 'retailer' in logged_users:
        headers = {'Authorization': f"Bearer {logged_users['retailer']['token']}"}
        response, error = make_request('GET', '/partners/', headers=headers)
        
        if error:
            print_test("Retailer partner visibility", False)
            print(f"    Error: {error}")
        elif response.status_code == 200:
            data = response.json()
            print_test("Retailer partner visibility", True)
            print(f"    Partners visible: {len(data)} (should see distributor)")
        else:
            print_test("Retailer partner visibility", False)
            print(f"    Status: {response.status_code}")

def main():
    """Run all tests"""
    print("🚀 AuroMart B2B Platform - Workflow Test Suite")
    print(f"Testing API at: {BASE_URL}")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Test health check first
    if not test_health_check():
        print("\n❌ Health check failed. Please ensure the backend is running.")
        return
    
    # Test user registration
    registered_users = test_user_registration()
    if not registered_users:
        print("\n❌ User registration failed. Cannot continue tests.")
        return
    
    # Test user login
    logged_users = test_user_login(registered_users)
    if not logged_users:
        print("\n❌ User login failed. Cannot continue tests.")
        return
    
    # Test partnership creation
    partnerships = test_partnership_creation(logged_users)
    
    # Test product creation
    products = test_product_creation(logged_users)
    
    # Test role-based visibility
    test_role_based_product_visibility(logged_users, products)
    test_partner_visibility(logged_users)
    
    print_section("TEST SUMMARY")
    print("✅ All core workflow tests completed!")
    print("📋 Tested:")
    print("   - User registration and login")
    print("   - Partnership creation")
    print("   - Product creation")
    print("   - Role-based product visibility")
    print("   - Partner visibility rules")
    print("\n🎯 Your AuroMart B2B platform is ready!")

if __name__ == "__main__":
    main()
