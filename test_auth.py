import requests
import json

# API Base URL - using the correct port 5001
API_BASE_URL = 'http://localhost:5001'

def test_signup():
    """Test signup for different user types"""
    print("🔧 Testing Signup Functionality...")
    
    # Test users data
    test_users = [
        {
            "email": "retailer@test.com",
            "password": "Test@123",
            "firstName": "John",
            "lastName": "Retailer",
            "role": "retailer",
            "businessName": "Test Retail Store",
            "phoneNumber": "+91-9876543210",
            "address": "123 Retail Street, Mumbai"
        },
        {
            "email": "distributor@test.com",
            "password": "Test@123",
            "firstName": "Jane",
            "lastName": "Distributor",
            "role": "distributor",
            "businessName": "Test Distribution Co",
            "phoneNumber": "+91-9876543211",
            "address": "456 Distribution Ave, Delhi"
        },
        {
            "email": "manufacturer@test.com",
            "password": "Test@123",
            "firstName": "Bob",
            "lastName": "Manufacturer",
            "role": "manufacturer",
            "businessName": "Test Manufacturing Ltd",
            "phoneNumber": "+91-9876543212",
            "address": "789 Manufacturing Hub, Pune"
        }
    ]
    
    for user_data in test_users:
        try:
            print(f"\n📝 Testing signup for {user_data['role']}: {user_data['email']}")
            
            response = requests.post(
                f"{API_BASE_URL}/api/auth/register",
                json=user_data,
                headers={'Content-Type': 'application/json'}
            )
            
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 201:
                print(f"✅ {user_data['role'].title()} signup successful!")
                result = response.json()
                print(f"User ID: {result.get('user', {}).get('id', 'N/A')}")
            else:
                print(f"❌ {user_data['role'].title()} signup failed!")
                print(f"Response: {response.text}")
                
        except requests.exceptions.ConnectionError:
            print(f"❌ Connection error: Cannot connect to {API_BASE_URL}")
            print("Make sure the backend server is running on port 5001")
            return False
        except Exception as e:
            print(f"❌ Error during signup: {str(e)}")
    
    return True

def test_login():
    """Test login for different user types"""
    print("\n🔐 Testing Login Functionality...")
    
    # Test login credentials
    test_credentials = [
        {"email": "retailer@test.com", "password": "Test@123", "role": "retailer"},
        {"email": "distributor@test.com", "password": "Test@123", "role": "distributor"},
        {"email": "manufacturer@test.com", "password": "Test@123", "role": "manufacturer"}
    ]
    
    for creds in test_credentials:
        try:
            print(f"\n🔑 Testing login for {creds['role']}: {creds['email']}")
            
            response = requests.post(
                f"{API_BASE_URL}/api/auth/login",
                json={"email": creds['email'], "password": creds['password']},
                headers={'Content-Type': 'application/json'}
            )
            
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                print(f"✅ {creds['role'].title()} login successful!")
                result = response.json()
                print(f"Token: {result.get('token', 'N/A')[:20]}...")
                print(f"User Role: {result.get('user', {}).get('role', 'N/A')}")
            else:
                print(f"❌ {creds['role'].title()} login failed!")
                print(f"Response: {response.text}")
                
        except requests.exceptions.ConnectionError:
            print(f"❌ Connection error: Cannot connect to {API_BASE_URL}")
            print("Make sure the backend server is running on port 5001")
            return False
        except Exception as e:
            print(f"❌ Error during login: {str(e)}")
    
    return True

def test_health_check():
    """Test if the backend is running"""
    print("🏥 Testing Backend Health...")
    
    try:
        response = requests.get(f"{API_BASE_URL}/api/health")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Backend is healthy and running!")
            return True
        else:
            print(f"❌ Backend health check failed: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"❌ Connection error: Cannot connect to {API_BASE_URL}")
        print("Make sure the backend server is running on port 5001")
        return False
    except Exception as e:
        print(f"❌ Error during health check: {str(e)}")
        return False

def main():
    print("🚀 AuroMart B2B Platform - Authentication Test")
    print("=" * 50)
    
    # First check if backend is running
    if not test_health_check():
        print("\n❌ Backend is not accessible. Please start the application first:")
        print("   docker-compose up -d")
        return
    
    print("\n" + "=" * 50)
    
    # Test signup
    signup_success = test_signup()
    
    print("\n" + "=" * 50)
    
    # Test login
    login_success = test_login()
    
    print("\n" + "=" * 50)
    
    if signup_success and login_success:
        print("🎉 All authentication tests completed!")
        print("\n📋 Test Summary:")
        print("- Backend health: ✅")
        print("- Signup functionality: ✅")
        print("- Login functionality: ✅")
        print("\n🔗 You can now test the frontend at: http://localhost:3001")
    else:
        print("❌ Some tests failed. Please check the errors above.")

if __name__ == "__main__":
    main()
