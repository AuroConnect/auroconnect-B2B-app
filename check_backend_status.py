#!/usr/bin/env python3
"""
Check backend status and logs
"""

import subprocess
import time
import requests

def run_command(command, description):
    """Run a command and return output"""
    print(f"\n🔧 {description}...")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        return result.stdout.strip()
    except Exception as e:
        print(f"Error: {e}")
        return ""

def check_backend_logs():
    """Check backend container logs"""
    print("📋 BACKEND LOGS")
    print("=" * 50)
    
    logs = run_command("docker logs auroconnect-b2b-app-backend-1 --tail 20", "Getting backend logs")
    print(logs)

def check_container_status():
    """Check container status"""
    print("📦 CONTAINER STATUS")
    print("=" * 50)
    
    status = run_command("docker ps", "Checking running containers")
    print(status)

def check_backend_health():
    """Check backend health endpoint"""
    print("🏥 BACKEND HEALTH CHECK")
    print("=" * 50)
    
    try:
        response = requests.get("http://localhost:5000/api/health", timeout=5)
        print(f"✅ Backend is healthy! Status: {response.status_code}")
        print(f"Response: {response.text}")
        return True
    except requests.exceptions.ConnectionError:
        print("❌ Backend is not accessible")
        return False
    except requests.exceptions.Timeout:
        print("⏰ Backend is taking too long to respond")
        return False
    except Exception as e:
        print(f"❌ Error checking backend: {e}")
        return False

def wait_for_backend():
    """Wait for backend to be ready"""
    print("⏳ WAITING FOR BACKEND TO BE READY")
    print("=" * 50)
    
    for attempt in range(30):
        print(f"⏳ Attempt {attempt + 1}/30...")
        
        if check_backend_health():
            print("✅ Backend is ready!")
            return True
        
        time.sleep(2)
    
    print("❌ Backend failed to start within 60 seconds")
    return False

def main():
    """Main function"""
    print("🔍 BACKEND STATUS CHECKER")
    print("=" * 50)
    
    # Check container status
    check_container_status()
    
    # Check backend logs
    check_backend_logs()
    
    # Check backend health
    if check_backend_health():
        print("\n🎉 Backend is working!")
    else:
        print("\n🔍 Backend is not ready, waiting...")
        if wait_for_backend():
            print("\n🎉 Backend is now ready!")
        else:
            print("\n❌ Backend failed to start")

if __name__ == "__main__":
    main()
