import requests
import json

def test_backend():
    """Test if the backend is running and responding"""
    print("🔍 Testing backend connectivity...")
    
    # Test 1: Basic health check
    try:
        response = requests.get("http://localhost:5000/api/health/")
        print(f"Health check status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Backend is running")
            print(f"   Status: {data.get('status')}")
            print(f"   Database: {data.get('database')}")
        else:
            print(f"❌ Health check failed: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to backend: {e}")
        return False
    
    # Test 2: Check if products endpoint exists
    try:
        response = requests.get("http://localhost:5000/api/products/")
        print(f"Products endpoint status: {response.status_code}")
        if response.status_code == 401:
            print("✅ Products endpoint exists (requires auth)")
        elif response.status_code == 200:
            print("✅ Products endpoint working")
        else:
            print(f"❌ Products endpoint failed: {response.text}")
    except Exception as e:
        print(f"❌ Products endpoint error: {e}")
    
    # Test 3: Check if categories endpoint exists
    try:
        response = requests.get("http://localhost:5000/api/products/categories")
        print(f"Categories endpoint status: {response.status_code}")
        if response.status_code == 401:
            print("✅ Categories endpoint exists (requires auth)")
        elif response.status_code == 200:
            print("✅ Categories endpoint working")
        else:
            print(f"❌ Categories endpoint failed: {response.text}")
    except Exception as e:
        print(f"❌ Categories endpoint error: {e}")
    
    # Test 4: Check if partners endpoints exist
    try:
        response = requests.get("http://localhost:5000/api/partners/distributors")
        print(f"Distributors endpoint status: {response.status_code}")
        if response.status_code == 401:
            print("✅ Distributors endpoint exists (requires auth)")
        elif response.status_code == 200:
            print("✅ Distributors endpoint working")
        else:
            print(f"❌ Distributors endpoint failed: {response.text}")
    except Exception as e:
        print(f"❌ Distributors endpoint error: {e}")
    
    print("\n🎯 Backend test completed!")

if __name__ == "__main__":
    test_backend()
