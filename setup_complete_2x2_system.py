#!/usr/bin/env python3
"""
Master setup script for complete 2x2 system
Resets database and initializes everything using EC2 MySQL server
"""

import subprocess
import time
import requests
import json
import os

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"\n🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        if result.stdout.strip():
            print(f"   Output: {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        print(f"   Error: {e.stderr}")
        if e.stdout.strip():
            print(f"   Output: {e.stdout.strip()}")
        return False

def wait_for_service(url, service_name, max_attempts=60):
    """Wait for a service to be ready"""
    print(f"\n⏳ Waiting for {service_name} to be ready...")
    for attempt in range(max_attempts):
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                print(f"✅ {service_name} is ready!")
                return True
        except requests.exceptions.RequestException as e:
            pass
        
        print(f"   Attempt {attempt + 1}/{max_attempts} - {service_name} not ready yet...")
        time.sleep(3)
    
    print(f"❌ {service_name} failed to start after {max_attempts} attempts")
    return False

def check_docker_status():
    """Check if Docker is running"""
    print("\n🔍 Checking Docker status...")
    try:
        result = subprocess.run("docker --version", shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Docker is available")
            return True
        else:
            print("❌ Docker is not available")
            return False
    except Exception as e:
        print(f"❌ Error checking Docker: {e}")
        return False

def check_docker_compose_status():
    """Check if Docker Compose is running"""
    print("\n🔍 Checking Docker Compose status...")
    try:
        result = subprocess.run("docker-compose --version", shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Docker Compose is available")
            return True
        else:
            print("❌ Docker Compose is not available")
            return False
    except Exception as e:
        print(f"❌ Error checking Docker Compose: {e}")
        return False

def setup_complete_system():
    """Setup the complete 2x2 system using EC2 MySQL"""
    
    print("🚀 Setting up Complete 2x2 AuroMart System with EC2 MySQL")
    print("=" * 70)
    
    # Check prerequisites
    if not check_docker_status():
        print("❌ Docker is required but not available. Please install Docker first.")
        return False
    
    if not check_docker_compose_status():
        print("❌ Docker Compose is required but not available. Please install Docker Compose first.")
        return False
    
    # Step 1: Stop all containers
    if not run_command("docker-compose down", "Stopping all containers"):
        print("   ⚠️  Some containers might not have been running")
    
    # Step 2: Build and start containers (using EC2 MySQL)
    if not run_command("docker-compose up -d --build", "Building and starting containers"):
        return False
    
    # Step 3: Wait for Redis to be ready
    print("\n⏳ Waiting for Redis to be ready...")
    for attempt in range(30):
        try:
            result = subprocess.run(
                "docker-compose exec redis redis-cli ping",
                shell=True, capture_output=True, text=True
            )
            if result.returncode == 0 and "PONG" in result.stdout:
                print("✅ Redis is ready!")
                break
        except:
            pass
        
        print(f"   Attempt {attempt + 1}/30 - Redis not ready yet...")
        time.sleep(2)
    else:
        print("❌ Redis failed to start")
        return False
    
    # Step 4: Wait for backend to be ready
    if not wait_for_service("http://localhost:5000/api/health", "Backend API"):
        print("❌ Backend failed to start. Checking logs...")
        subprocess.run("docker-compose logs backend", shell=True)
        return False
    
    # Step 5: Wait for frontend to be ready
    if not wait_for_service("http://localhost:3000", "Frontend"):
        print("❌ Frontend failed to start. Checking logs...")
        subprocess.run("docker-compose logs frontend", shell=True)
        return False
    
    # Step 6: Create 2x2 organizations
    print("\n👥 Creating 2x2 organizations...")
    try:
        result = subprocess.run(["python", "reset_and_seed_2x2.py"], 
                              capture_output=True, text=True, check=True)
        print(result.stdout)
        print("✅ 2x2 organizations created successfully")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to create organizations: {e.stderr}")
        print(f"   Output: {e.stdout}")
        return False
    
    # Step 7: Test the complete flow
    print("\n🧪 Testing complete flow...")
    try:
        result = subprocess.run(["python", "test_complete_flow.py"], 
                              capture_output=True, text=True, check=True)
        print(result.stdout)
        print("✅ Complete flow test passed")
    except subprocess.CalledProcessError as e:
        print(f"❌ Flow test failed: {e.stderr}")
        print(f"   Output: {e.stdout}")
        return False
    
    print("\n" + "=" * 70)
    print("🎉 Complete 2x2 System Setup Successful!")
    print("=" * 70)
    print("\n📋 System Information:")
    print("   • Backend: http://localhost:5000")
    print("   • Frontend: http://localhost:3000")
    print("   • Database: MySQL (EC2 Server: 3.249.132.231)")
    print("   • Redis: localhost:6379")
    print("\n👥 Test Accounts:")
    print("   • M1 (Manufacturer): m1@auromart.com / password123")
    print("   • M2 (Manufacturer): m2@auromart.com / password123")
    print("   • D1 (Distributor): d1@auromart.com / password123")
    print("   • D2 (Distributor): d2@auromart.com / password123")
    print("\n🔄 Complete Flow:")
    print("   1. M1 logs in → Creates products → Assigns to D1")
    print("   2. D1 logs in → Sees assigned products → Adds to cart → Places order")
    print("   3. M1 logs in → Sees order → Approves/Declines")
    print("   4. Order status updates → Notifications sent")
    print("\n✨ Ready to test the complete end-to-end flow!")
    print("\n🔧 Useful Commands:")
    print("   • View logs: docker-compose logs")
    print("   • Stop system: docker-compose down")
    print("   • Restart: docker-compose restart")

if __name__ == "__main__":
    setup_complete_system()
