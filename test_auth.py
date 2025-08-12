import requests
import json

# Test the login endpoint
def test_login():
    url = "http://localhost:5000/api/auth/login"
    data = {
        "email": "m@demo.com",
        "password": "Demo@123"
    }
    
    try:
        response = requests.post(url, json=data, headers={'Content-Type': 'application/json'})
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        return response
    except Exception as e:
        print(f"Error: {e}")
        return None

# Test the register endpoint
def test_register():
    url = "http://localhost:5000/api/auth/register"
    data = {
        "firstName": "Test",
        "lastName": "User",
        "email": "test@example.com",
        "password": "Test123!",
        "role": "manufacturer",
        "businessName": "Test Business"
    }
    
    try:
        response = requests.post(url, json=data, headers={'Content-Type': 'application/json'})
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        return response
    except Exception as e:
        print(f"Error: {e}")
        return None

if __name__ == "__main__":
    print("Testing Login...")
    test_login()
    print("\nTesting Register...")
    test_register()
