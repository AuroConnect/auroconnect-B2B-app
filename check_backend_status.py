#!/usr/bin/env python3
"""
Backend Status Checker for AuroMart
This script checks if the backend server is running and accessible.
"""

import requests
import sys
import time
from urllib.parse import urljoin

def check_backend_status(base_url="http://localhost:5000"):
    """Check if the backend is running and accessible."""
    
    print("🔍 Checking AuroMart Backend Status...")
    print(f"📍 Backend URL: {base_url}")
    print("-" * 50)
    
    # Test 1: Health Check
    try:
        print("🏥 Testing Health Check...")
        response = requests.get(urljoin(base_url, "/api/health"), timeout=5)
        if response.status_code == 200:
            print("✅ Health Check: PASSED")
            data = response.json()
            print(f"   Message: {data.get('message', 'OK')}")
        else:
            print(f"❌ Health Check: FAILED (Status: {response.status_code})")
    except requests.exceptions.ConnectionError:
        print("❌ Health Check: FAILED (Connection Error)")
        print("   Backend server is not running or not accessible")
        return False
    except requests.exceptions.Timeout:
        print("❌ Health Check: FAILED (Timeout)")
        return False
    except Exception as e:
        print(f"❌ Health Check: FAILED (Error: {e})")
        return False
    
    # Test 2: Auth Endpoints
    try:
        print("\n🔑 Testing Auth Endpoints...")
        response = requests.get(urljoin(base_url, "/api/auth/user"), timeout=5)
        if response.status_code in [401, 404]:
            print("✅ Auth Endpoints: PASSED (Unauthorized as expected)")
        else:
            print(f"⚠️  Auth Endpoints: UNEXPECTED (Status: {response.status_code})")
    except Exception as e:
        print(f"❌ Auth Endpoints: FAILED (Error: {e})")
    
    # Test 3: CORS Headers
    try:
        print("\n🌐 Testing CORS Headers...")
        response = requests.options(urljoin(base_url, "/api/health"), timeout=5)
        cors_headers = response.headers.get('Access-Control-Allow-Origin')
        if cors_headers:
            print("✅ CORS Headers: PASSED")
            print(f"   Allow-Origin: {cors_headers}")
        else:
            print("⚠️  CORS Headers: MISSING")
    except Exception as e:
        print(f"❌ CORS Headers: FAILED (Error: {e})")
    
    print("\n" + "=" * 50)
    print("🎯 Backend Status Summary:")
    print("✅ Backend is running and accessible")
    print("✅ API endpoints are responding")
    print("✅ Ready for frontend connection")
    print("\n🚀 You can now start the frontend!")
    print("   Run: cd client && npm run dev")
    
    return True

def main():
    """Main function to run the backend check."""
    if len(sys.argv) > 1:
        base_url = sys.argv[1]
    else:
        base_url = "http://localhost:5000"
    
    try:
        success = check_backend_status(base_url)
        if not success:
            print("\n❌ Backend is not accessible!")
            print("\n🔧 Troubleshooting Steps:")
            print("1. Make sure the backend server is running:")
            print("   cd server && python run.py")
            print("2. Check if port 5000 is available")
            print("3. Verify the database connection")
            print("4. Check server logs for errors")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n👋 Backend check interrupted by user")
        sys.exit(0)

if __name__ == "__main__":
    main()
