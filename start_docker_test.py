#!/usr/bin/env python3
"""
Build and start Docker containers for AuroMart testing
"""

import subprocess
import sys
import time
import os

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
        print(f"Error: {e.stderr}")
        return False

def check_docker():
    """Check if Docker is running"""
    print("🔍 Checking Docker...")
    try:
        result = subprocess.run("docker --version", shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Docker is available")
            return True
        else:
            print("❌ Docker is not available")
            return False
    except:
        print("❌ Docker is not available")
        return False

def check_docker_compose():
    """Check if Docker Compose is available"""
    print("🔍 Checking Docker Compose...")
    try:
        result = subprocess.run("docker-compose --version", shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Docker Compose is available")
            return True
        else:
            print("❌ Docker Compose is not available")
            return False
    except:
        print("❌ Docker Compose is not available")
        return False

def main():
    """Main function to build and start containers"""
    print("🚀 AuroMart Docker Setup")
    print("=" * 50)
    
    # Check prerequisites
    if not check_docker():
        print("\n❌ Docker is required but not available")
        print("Please install Docker and try again")
        sys.exit(1)
    
    if not check_docker_compose():
        print("\n❌ Docker Compose is required but not available")
        print("Please install Docker Compose and try again")
        sys.exit(1)
    
    # Stop any existing containers
    print("\n🛑 Stopping existing containers...")
    subprocess.run("docker-compose down", shell=True)
    
    # Build containers with no cache
    if not run_command("docker-compose build --no-cache", "Building containers (no cache)"):
        print("\n❌ Container build failed")
        sys.exit(1)
    
    # Start containers
    if not run_command("docker-compose up -d", "Starting containers"):
        print("\n❌ Container startup failed")
        sys.exit(1)
    
    # Wait for containers to be ready
    print("\n⏳ Waiting for containers to be ready...")
    time.sleep(10)
    
    # Check container status
    print("\n📊 Container Status:")
    subprocess.run("docker-compose ps", shell=True)
    
    print("\n" + "=" * 50)
    print("🎉 Docker containers are ready!")
    print("=" * 50)
    print("🌐 Frontend: http://localhost:3000")
    print("🔗 Backend API: http://localhost:5000")
    print("📊 Container status: docker-compose ps")
    print("📋 Logs: docker-compose logs -f")
    print()
    print("📝 Next steps:")
    print("   1. Run: python create_test_accounts.py")
    print("   2. Go to http://localhost:3000")
    print("   3. Test the application with the created accounts")
    print()
    print("🔧 Useful commands:")
    print("   docker-compose logs -f backend    # View backend logs")
    print("   docker-compose logs -f frontend   # View frontend logs")
    print("   docker-compose down               # Stop containers")
    print("   docker-compose restart            # Restart containers")

if __name__ == "__main__":
    main()
