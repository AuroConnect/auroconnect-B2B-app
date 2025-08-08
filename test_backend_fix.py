#!/usr/bin/env python3
"""
Test script to verify backend is working after fixes
"""

import requests
import time
import sys

def test_backend():
    """Test if backend is responding"""
    print("�� Testing backend...")
    
    try:
        # Test health endpoint
        response = requests.get("http://localhost:5000/api/health", timeout=10)
        if response.status_code == 200:
            print("✅ Backend health check passed!")
            data = response.json()
            print(f"   Status: {data.get('status')}")
            print(f"   Database: {data.get('database')}")
            return True
        else:
            print(f"❌ Backend health check failed with status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Backend is not running (Connection refused)")
        return False
    except Exception as e:
        print(f"❌ Error testing backend: {e}")
        return False

def test_auth_endpoint():
    """Test authentication endpoint"""
    print("\n🔐 Testing authentication endpoint...")
    
    try:
        response = requests.get("http://localhost:5000/api/auth/user", timeout=10)
        if response.status_code in [401, 200]:  # 401 is expected for unauthenticated
            print("✅ Authentication endpoint is working!")
            return True
        else:
            print(f"❌ Authentication endpoint failed with status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error testing auth endpoint: {e}")
        return False

def main():
    """Main function"""
    print("🚀 Testing AuroMart Backend After Fixes")
    print("=" * 50)
    
    # Wait a bit for backend to start
    print("⏳ Waiting for backend to start...")
    time.sleep(5)
    
    if test_backend():
        if test_auth_endpoint():
            print("\n�� Backend is working correctly!")
            print("✅ All tests passed!")
            return True
        else:
            print("\n❌ Authentication endpoint has issues")
            return False
    else:
        print("\n❌ Backend is not working")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
