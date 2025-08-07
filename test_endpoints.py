import requests
import json

def test_all_endpoints():
    """Test all endpoints that the frontend expects"""
    
    print("🔍 Testing all frontend-expected endpoints...")
    
    # Test 1: Health check
    print("\n1. Testing health endpoint...")
    try:
        response = requests.get("http://localhost:5000/api/health/")
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Backend is running")
            print(f"   Database: {data.get('database', 'Unknown')}")
        else:
            print(f"   ❌ Health check failed: {response.text}")
            return False
    except Exception as e:
        print(f"   ❌ Cannot connect to backend: {e}")
        return False
    
    # Test 2: Register a test user
    print("\n2. Testing user registration...")
    test_user = {
        "firstName": "Test",
        "lastName": "User",
        "email": "testuser@auromart.com",
        "password": "testpass123",
        "businessName": "Test Business",
        "phoneNumber": "1234567890",
        "role": "manufacturer"
    }
    
    try:
        response = requests.post("http://localhost:5000/api/auth/register", json=test_user)
        print(f"   Status: {response.status_code}")
        if response.status_code == 201:
            print("   ✅ Registration successful")
            user_data = response.json()
            token = user_data.get('token')
            user_id = user_data.get('user', {}).get('id')
            print(f"   User ID: {user_id}")
        else:
            print(f"   ❌ Registration failed: {response.text}")
            # Try to login instead
            print("   🔄 Trying login...")
            login_data = {
                "email": "testuser@auromart.com",
                "password": "testpass123"
            }
            response = requests.post("http://localhost:5000/api/auth/login", json=login_data)
            if response.status_code == 200:
                print("   ✅ Login successful")
                user_data = response.json()
                token = user_data.get('access_token')
                user_id = user_data.get('user', {}).get('id')
                print(f"   User ID: {user_id}")
            else:
                print(f"   ❌ Login failed: {response.text}")
                token = None
                user_id = None
    except Exception as e:
        print(f"   ❌ Registration/Login error: {e}")
        token = None
        user_id = None
    
    if not token:
        print("   ⚠️  Skipping authenticated tests due to auth failure")
        return False
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test 3: Categories endpoint
    print("\n3. Testing categories endpoint...")
    try:
        response = requests.get("http://localhost:5000/api/products/categories", headers=headers)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            categories = response.json()
            print(f"   ✅ Categories endpoint working, found {len(categories)} categories")
        else:
            print(f"   ❌ Categories endpoint failed: {response.text}")
    except Exception as e:
        print(f"   ❌ Categories endpoint error: {e}")
    
    # Test 4: Products endpoint
    print("\n4. Testing products endpoint...")
    try:
        response = requests.get("http://localhost:5000/api/products/", headers=headers)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            products = response.json()
            print(f"   ✅ Products endpoint working, found {len(products)} products")
        else:
            print(f"   ❌ Products endpoint failed: {response.text}")
    except Exception as e:
        print(f"   ❌ Products endpoint error: {e}")
    
    # Test 5: Partners endpoints
    print("\n5. Testing partners endpoints...")
    
    # Test distributors endpoint
    try:
        response = requests.get("http://localhost:5000/api/partners/distributors", headers=headers)
        print(f"   Distributors Status: {response.status_code}")
        if response.status_code == 200:
            distributors = response.json()
            print(f"   ✅ Distributors endpoint working, found {len(distributors)} distributors")
        else:
            print(f"   ❌ Distributors endpoint failed: {response.text}")
    except Exception as e:
        print(f"   ❌ Distributors endpoint error: {e}")
    
    # Test retailers endpoint
    try:
        response = requests.get("http://localhost:5000/api/partners/retailers", headers=headers)
        print(f"   Retailers Status: {response.status_code}")
        if response.status_code == 200:
            retailers = response.json()
            print(f"   ✅ Retailers endpoint working, found {len(retailers)} retailers")
        else:
            print(f"   ❌ Retailers endpoint failed: {response.text}")
    except Exception as e:
        print(f"   ❌ Retailers endpoint error: {e}")
    
    # Test manufacturers endpoint
    try:
        response = requests.get("http://localhost:5000/api/partners/manufacturers", headers=headers)
        print(f"   Manufacturers Status: {response.status_code}")
        if response.status_code == 200:
            manufacturers = response.json()
            print(f"   ✅ Manufacturers endpoint working, found {len(manufacturers)} manufacturers")
        else:
            print(f"   ❌ Manufacturers endpoint failed: {response.text}")
    except Exception as e:
        print(f"   ❌ Manufacturers endpoint error: {e}")
    
    # Test 6: User endpoint
    print("\n6. Testing user endpoint...")
    try:
        response = requests.get("http://localhost:5000/api/auth/user", headers=headers)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            user_data = response.json()
            print(f"   ✅ User endpoint working")
            print(f"   User: {user_data.get('firstName')} {user_data.get('lastName')} ({user_data.get('role')})")
        else:
            print(f"   ❌ User endpoint failed: {response.text}")
    except Exception as e:
        print(f"   ❌ User endpoint error: {e}")
    
    print("\n🎯 All endpoint tests completed!")
    return True

if __name__ == "__main__":
    test_all_endpoints()
