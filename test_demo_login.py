import requests
import json

def test_login(email, password):
    url = "http://localhost:5000/api/auth/login"
    data = {
        "email": email,
        "password": password
    }
    
    try:
        response = requests.post(url, json=data, headers={'Content-Type': 'application/json'})
        print(f"Login {email}: {response.status_code}")
        if response.status_code == 200:
            print(f"✅ Successfully logged in as {email}")
            data = response.json()
            print(f"   User: {data.get('user', {}).get('firstName', '')} {data.get('user', {}).get('lastName', '')}")
            print(f"   Role: {data.get('user', {}).get('role', '')}")
        else:
            print(f"❌ Failed: {response.text}")
        return response
    except Exception as e:
        print(f"❌ Error logging in {email}: {e}")
        return None

def main():
    print("Testing demo user logins...")
    
    # Test all demo users
    demo_users = [
        {"email": "m@demo.com", "password": "Demo@123"},
        {"email": "d@demo.com", "password": "Demo@123"},
        {"email": "r@demo.com", "password": "Demo@123"}
    ]
    
    for user in demo_users:
        test_login(user["email"], user["password"])
        print()
    
    print("Demo login tests completed!")

if __name__ == "__main__":
    main()
