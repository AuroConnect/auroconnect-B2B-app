import requests
import subprocess
import time
import sys

def check_backend():
    """Check if the backend is running and provide fixes"""
    
    print("🔍 Checking backend status...")
    
    try:
        response = requests.get("http://localhost:5000/api/health/", timeout=5)
        if response.status_code == 200:
            print("✅ Backend is running!")
            data = response.json()
            print(f"   Database: {data.get('database', 'Unknown')}")
            return True
        else:
            print(f"❌ Backend responded with status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Backend is not running (Connection refused)")
        return False
    except Exception as e:
        print(f"❌ Error checking backend: {e}")
        return False

def provide_fixes():
    """Provide instructions to fix backend issues"""
    
    print("\n🔧 Backend Fix Instructions:")
    print("=" * 50)
    
    print("\n1. If using Docker Compose:")
    print("   docker-compose down")
    print("   docker-compose up -d")
    print("   docker-compose logs backend")
    
    print("\n2. If running locally:")
    print("   cd server")
    print("   python run.py")
    
    print("\n3. If database issues:")
    print("   cd server")
    print("   python init_db_docker.py")
    
    print("\n4. Check if all required files exist:")
    print("   - server/run.py")
    print("   - server/app/__init__.py")
    print("   - server/app/api/v1/products.py")
    print("   - server/app/api/v1/partners.py")
    print("   - server/app/api/v1/auth.py")
    
    print("\n5. Check if all models are imported:")
    print("   - server/app/models/__init__.py")
    print("   - server/app/models/user.py")
    print("   - server/app/models/product.py")
    print("   - server/app/models/partnership.py")
    
    print("\n6. Test endpoints after restart:")
    print("   python test_endpoints.py")

def main():
    """Main function"""
    
    print("🚀 AuroMart Backend Health Check")
    print("=" * 40)
    
    if check_backend():
        print("\n✅ Backend is healthy!")
        print("🎯 You can now test the frontend")
    else:
        print("\n❌ Backend is not running or has issues")
        provide_fixes()

if __name__ == "__main__":
    main()
