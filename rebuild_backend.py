#!/usr/bin/env python3
"""
Rebuild backend with fixed database connection
"""

import subprocess
import time
import requests

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"\n🔧 {description}...")
    print(f"Command: {command}")
    
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        if result.stdout:
            print(f"Output: {result.stdout}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed")
        if e.stderr:
            print(f"Error: {e.stderr}")
        return False

def check_backend_health():
    """Check if backend is healthy"""
    try:
        response = requests.get("http://localhost:5000/api/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get("database") == "connected":
                print("✅ Backend is healthy and database is connected!")
                return True
            else:
                print(f"⚠️ Backend is running but database issue: {data}")
                return False
        else:
            print(f"❌ Backend health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to backend: {e}")
        return False

def wait_for_backend():
    """Wait for backend to be ready"""
    print("⏳ Waiting for backend to be ready...")
    
    for attempt in range(30):
        print(f"⏳ Attempt {attempt + 1}/30...")
        
        if check_backend_health():
            return True
        
        time.sleep(2)
    
    print("❌ Backend failed to start within 60 seconds")
    return False

def main():
    """Main function"""
    print("🔧 REBUILDING BACKEND WITH FIXED DATABASE CONNECTION")
    print("=" * 60)
    
    # Stop backend container
    run_command("docker stop auroconnect-b2b-app-backend-1", "Stopping backend container")
    
    # Remove backend container
    run_command("docker rm auroconnect-b2b-app-backend-1", "Removing backend container")
    
    # Remove backend image
    run_command("docker rmi auroconnect-b2b-app-backend", "Removing backend image")
    
    # Rebuild backend
    run_command("docker-compose build --no-cache backend", "Rebuilding backend")
    
    # Start backend
    run_command("docker-compose up -d backend", "Starting backend")
    
    # Wait for backend to be ready
    print("\n⏳ Waiting for backend to start...")
    if wait_for_backend():
        print("\n🎉 Backend is ready! Database connection fixed!")
        print("\n📋 Next steps:")
        print("   1. Run: python create_test_accounts.py")
        print("   2. Access the app at: http://localhost:3000")
    else:
        print("\n❌ Backend failed to start properly")
        print("Check logs with: docker logs auroconnect-b2b-app-backend-1")

if __name__ == "__main__":
    main()
