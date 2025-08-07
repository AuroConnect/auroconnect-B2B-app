#!/usr/bin/env python3
"""
Docker Compose startup script for AuroMart
"""

import os
import sys
import subprocess
import time
from pathlib import Path

def run_command(command, cwd=None):
    """Run a command and return the result"""
    try:
        result = subprocess.run(
            command,
            cwd=cwd,
            shell=True,
            capture_output=True,
            text=True
        )
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def check_docker():
    """Check if Docker is available"""
    success, stdout, stderr = run_command("docker --version")
    if not success:
        print("❌ Docker is not installed or not running")
        print("Please install Docker Desktop and try again")
        return False
    
    print(f"✅ Docker found: {stdout.strip()}")
    return True

def check_docker_compose():
    """Check if Docker Compose is available"""
    success, stdout, stderr = run_command("docker-compose --version")
    if not success:
        # Try with 'docker compose' (newer versions)
        success, stdout, stderr = run_command("docker compose version")
        if not success:
            print("❌ Docker Compose is not available")
            print("Please install Docker Compose and try again")
            return False
    
    print(f"✅ Docker Compose found: {stdout.strip()}")
    return True

def start_services():
    """Start all Docker services"""
    print("🚀 Starting AuroMart with Docker Compose...")
    print("=" * 60)
    
    # Build and start services
    success, stdout, stderr = run_command("docker-compose up -d --build")
    if not success:
        print("❌ Failed to start services")
        print(f"Error: {stderr}")
        return False
    
    print("✅ Services started successfully!")
    return True

def wait_for_services():
    """Wait for services to be ready"""
    print("⏳ Waiting for services to be ready...")
    
    # Wait for backend health check
    max_attempts = 60
    attempt = 0
    
    while attempt < max_attempts:
        success, stdout, stderr = run_command("curl -f http://localhost:5000/api/health")
        if success:
            print("✅ Backend is ready!")
            break
        
        attempt += 1
        print(f"⏳ Waiting for backend... (attempt {attempt}/{max_attempts})")
        time.sleep(5)
    
    if attempt >= max_attempts:
        print("❌ Backend failed to start")
        return False
    
    # Wait for frontend
    max_attempts = 30
    attempt = 0
    
    while attempt < max_attempts:
        success, stdout, stderr = run_command("curl -f http://localhost:3000")
        if success:
            print("✅ Frontend is ready!")
            break
        
        attempt += 1
        print(f"⏳ Waiting for frontend... (attempt {attempt}/{max_attempts})")
        time.sleep(2)
    
    if attempt >= max_attempts:
        print("❌ Frontend failed to start")
        return False
    
    return True

def show_status():
    """Show service status"""
    print("\n" + "=" * 60)
    print("🎉 AuroMart is running!")
    print("=" * 60)
    print("🌐 Frontend: http://localhost:3000")
    print("🔧 Backend API: http://localhost:5000")
    print("📊 Health Check: http://localhost:5000/api/health")
    print("🗄️  Database: PostgreSQL (Docker)")
    print("=" * 60)
    print("📋 Test Credentials:")
    print("  - retailer@example.com (password: password123)")
    print("  - distributor@example.com (password: password123)")
    print("  - manufacturer@example.com (password: password123)")
    print("=" * 60)
    print("🛑 To stop services: docker-compose down")
    print("📝 To view logs: docker-compose logs -f")
    print("=" * 60)

def main():
    """Main function"""
    print("🎯 Starting AuroMart with Docker Compose...")
    
    # Check prerequisites
    if not check_docker():
        return
    
    if not check_docker_compose():
        return
    
    # Start services
    if not start_services():
        return
    
    # Wait for services to be ready
    if not wait_for_services():
        print("❌ Services failed to start properly")
        print("Check logs with: docker-compose logs")
        return
    
    # Show status
    show_status()

if __name__ == "__main__":
    main()
