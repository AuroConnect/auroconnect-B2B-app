#!/usr/bin/env python3
"""
Force cleanup script - completely remove everything and check what's running
"""

import subprocess
import sys
import time

def run_command(command, description, check_output=False):
    """Run a command and handle errors"""
    print(f"\n🔧 {description}...")
    print(f"Command: {command}")
    
    try:
        if check_output:
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            return result.stdout.strip()
        else:
            result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
            print(f"✅ {description} completed successfully")
            if result.stdout:
                print(f"Output: {result.stdout}")
            return True
    except subprocess.CalledProcessError as e:
        print(f"⚠️  {description} - some items may not exist (this is normal)")
        if e.stderr:
            print(f"Note: {e.stderr}")
        return True

def check_whats_running():
    """Check what containers and processes are still running"""
    print("\n🔍 CHECKING WHAT'S STILL RUNNING")
    print("=" * 50)
    
    # Check Docker containers
    print("\n📦 Docker Containers:")
    containers = run_command("docker ps -a", "Checking all containers", check_output=True)
    if containers:
        print(containers)
    else:
        print("No containers found")
    
    # Check Docker images
    print("\n🖼️  Docker Images:")
    images = run_command("docker images", "Checking all images", check_output=True)
    if images:
        print(images)
    else:
        print("No images found")
    
    # Check Docker volumes
    print("\n💾 Docker Volumes:")
    volumes = run_command("docker volume ls", "Checking all volumes", check_output=True)
    if volumes:
        print(volumes)
    else:
        print("No volumes found")
    
    # Check what's using port 3000
    print("\n🌐 Port 3000 Usage:")
    port3000 = run_command("netstat -tulpn 2>/dev/null | grep :3000 || echo 'No process on port 3000'", "Checking port 3000", check_output=True)
    print(port3000)
    
    # Check what's using port 5000
    print("\n🔗 Port 5000 Usage:")
    port5000 = run_command("netstat -tulpn 2>/dev/null | grep :5000 || echo 'No process on port 5000'", "Checking port 5000", check_output=True)
    print(port5000)
    
    # Check Docker networks
    print("\n🌐 Docker Networks:")
    networks = run_command("docker network ls", "Checking all networks", check_output=True)
    if networks:
        print(networks)
    else:
        print("No networks found")

def force_cleanup():
    """Force cleanup everything"""
    print("🧹 FORCE CLEANUP - REMOVING EVERYTHING")
    print("=" * 50)
    
    # Force stop all containers
    run_command("docker kill $(docker ps -q) 2>/dev/null || true", "Force stopping all containers")
    
    # Remove all containers
    run_command("docker rm -f $(docker ps -aq) 2>/dev/null || true", "Force removing all containers")
    
    # Remove all images
    run_command("docker rmi -f $(docker images -q) 2>/dev/null || true", "Force removing all images")
    
    # Remove all volumes
    run_command("docker volume rm $(docker volume ls -q) 2>/dev/null || true", "Removing all volumes")
    
    # Remove all networks (except default ones)
    run_command("docker network prune -f", "Cleaning up networks")
    
    # Clean up system completely
    run_command("docker system prune -af --volumes", "Complete system cleanup")
    
    # Kill any processes on ports 3000 and 5000
    print("\n🔫 Killing processes on ports 3000 and 5000...")
    run_command("sudo fuser -k 3000/tcp 2>/dev/null || true", "Killing port 3000")
    run_command("sudo fuser -k 5000/tcp 2>/dev/null || true", "Killing port 5000")
    
    # Alternative method for Windows
    run_command("netstat -ano | findstr :3000 | findstr LISTENING", "Checking Windows port 3000", check_output=True)
    run_command("netstat -ano | findstr :5000 | findstr LISTENING", "Checking Windows port 5000", check_output=True)

def main():
    """Main cleanup function"""
    print("🚨 FORCE CLEANUP SCRIPT")
    print("=" * 50)
    print("This will completely remove ALL Docker containers, images, and volumes")
    print("And kill any processes using ports 3000 and 5000")
    print()
    
    # First check what's running
    check_whats_running()
    
    # Ask for confirmation
    response = input("\n❓ Do you want to proceed with force cleanup? (yes/no): ")
    if response.lower() != 'yes':
        print("❌ Cleanup cancelled")
        return
    
    # Force cleanup
    force_cleanup()
    
    # Wait a moment
    time.sleep(2)
    
    # Check again what's running
    print("\n" + "=" * 50)
    print("✅ CLEANUP COMPLETED - CHECKING RESULTS")
    print("=" * 50)
    check_whats_running()
    
    print("\n🎯 If you can still access the website, it might be:")
    print("   1. Cached in your browser (try Ctrl+F5 or incognito mode)")
    print("   2. Running on a different port")
    print("   3. Running on a different machine/VM")
    print("   4. A different service using the same ports")

if __name__ == "__main__":
    main()
