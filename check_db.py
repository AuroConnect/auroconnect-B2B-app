import requests
import json

def check_database():
    """Check if the database is properly set up"""
    print("🔍 Checking database setup...")
    
    # Test health endpoint to see if backend is running
    try:
        response = requests.get("http://localhost:5000/api/health/")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Backend is running")
            print(f"   Database status: {data.get('database', 'Unknown')}")
        else:
            print(f"❌ Backend health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to backend: {e}")
        return False
    
    # Test if we can create a user (this will test database tables)
    print("\n👤 Testing database tables with user creation...")
    
    test_user = {
        "firstName": "DBTest",
        "lastName": "User",
        "email": "dbtest@auromart.com",
        "password": "testpass123",
        "businessName": "DB Test Business",
        "phoneNumber": "1234567890",
        "role": "manufacturer"
    }
    
    try:
        response = requests.post("http://localhost:5000/api/auth/register", json=test_user)
        if response.status_code == 201:
            print("✅ Database tables are working - user created successfully")
            user_data = response.json()
            print(f"   User ID: {user_data.get('user', {}).get('id')}")
            return True
        else:
            print(f"❌ Database table test failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Database test error: {e}")
        return False

if __name__ == "__main__":
    check_database()
