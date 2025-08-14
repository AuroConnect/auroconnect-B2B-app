#!/usr/bin/env python3
"""
Simple test to check backend accessibility
"""
import requests
import time

def test_backend():
    """Test if backend is accessible"""
    print("🔍 Testing Backend Accessibility")
    print("=" * 40)
    
    # Test health endpoint
    try:
        response = requests.get("http://localhost:5000/api/health", timeout=5)
        if response.status_code == 200:
            print("✅ Backend is accessible")
            print(f"   Response: {response.json()}")
            return True
        else:
            print(f"❌ Backend responded with status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Backend is not accessible (ConnectionError)")
        return False
    except requests.exceptions.Timeout:
        print("❌ Backend is not accessible (Timeout)")
        return False
    except Exception as e:
        print(f"❌ Backend test failed: {e}")
        return False

def test_my_products_endpoint():
    """Test my-products endpoint"""
    print("\n📦 Testing My Products Endpoint")
    print("=" * 40)
    
    try:
        # Test without authentication (should return 401)
        response = requests.get("http://localhost:5000/api/my-products", timeout=5)
        if response.status_code == 401:
            print("✅ My Products endpoint exists (requires authentication)")
            return True
        else:
            print(f"❌ Unexpected response: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ My Products endpoint not accessible")
        return False
    except Exception as e:
        print(f"❌ My Products test failed: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 Simple Backend Test")
    print("=" * 50)
    
    # Wait a bit for backend to start
    print("⏳ Waiting for backend to start...")
    time.sleep(3)
    
    tests = [
        test_backend,
        test_my_products_endpoint
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test failed with error: {e}")
            results.append(False)
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)
    
    passed = sum(results)
    total = len(results)
    
    print(f"✅ Passed: {passed}/{total}")
    print(f"❌ Failed: {total - passed}/{total}")
    
    if passed == total:
        print("\n🎉 Backend is working correctly!")
        print("\n✅ Ready to test the full functionality:")
        print("  1. Open browser and go to http://localhost:3000")
        print("  2. Login as manufacturer: m@demo.com / Demo@123")
        print("  3. Check My Products vs Catalog tabs")
        print("  4. Test all role-based functionality")
    else:
        print("\n⚠️ Backend has issues. Please check:")
        print("  1. Docker containers are running: docker ps")
        print("  2. Backend logs: docker-compose logs backend")
        print("  3. Restart backend: docker-compose restart backend")
    
    return passed == total

if __name__ == "__main__":
    main()
