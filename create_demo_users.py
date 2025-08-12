import requests
import json

def create_demo_user(email, password, role, business_name, first_name, last_name):
    url = "http://localhost:5000/api/auth/register"
    data = {
        "firstName": first_name,
        "lastName": last_name,
        "email": email,
        "password": password,
        "role": role,
        "businessName": business_name
    }
    
    try:
        response = requests.post(url, json=data, headers={'Content-Type': 'application/json'})
        print(f"Creating {role} user {email}: {response.status_code}")
        if response.status_code == 201:
            print(f"✅ Successfully created {role} user")
        elif response.status_code == 409:
            print(f"⚠️  User {email} already exists")
        else:
            print(f"❌ Failed: {response.text}")
        return response
    except Exception as e:
        print(f"❌ Error creating {email}: {e}")
        return None

def main():
    print("Creating demo users...")
    
    # Create demo users
    demo_users = [
        {
            "email": "m@demo.com",
            "password": "Demo@123",
            "role": "manufacturer",
            "business_name": "Auro Manufacturer",
            "first_name": "Manufacturer",
            "last_name": "Demo"
        },
        {
            "email": "d@demo.com",
            "password": "Demo@123",
            "role": "distributor",
            "business_name": "Auro Distributor",
            "first_name": "Distributor",
            "last_name": "Demo"
        },
        {
            "email": "r@demo.com",
            "password": "Demo@123",
            "role": "retailer",
            "business_name": "Auro Retailer",
            "first_name": "Retailer",
            "last_name": "Demo"
        }
    ]
    
    for user in demo_users:
        create_demo_user(**user)
        print()
    
    print("Demo users creation completed!")

if __name__ == "__main__":
    main()
