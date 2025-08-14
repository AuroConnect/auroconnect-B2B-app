#!/usr/bin/env python3
"""
AuroMart Development Startup Script
This script helps you quickly start the development environment.
"""

import subprocess
import sys
import time
import os
import signal
from pathlib import Path

def run_command(command, description, cwd=None):
    """Run a command and return the process"""
    print(f"🚀 {description}...")
    print(f"   Command: {command}")
    print(f"   Directory: {cwd or 'current'}")
    
    try:
        process = subprocess.Popen(
            command,
            shell=True,
            cwd=cwd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1
        )
        return process
    except Exception as e:
        print(f"❌ Error starting {description}: {e}")
        return None

def check_backend_health():
    """Check if backend is healthy"""
    try:
        import requests
        response = requests.get("http://localhost:5000/api/health", timeout=2)
        return response.status_code == 200
    except:
        return False

def main():
    """Main function to start development environment"""
    print("🚀 AuroMart Development Environment Startup")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not Path("server").exists() or not Path("client").exists():
        print("❌ Error: Please run this script from the AuroMart root directory")
        print("   Make sure you have 'server' and 'client' folders")
        sys.exit(1)
    
    processes = []
    
    try:
        # Start Backend
        print("\n🔧 Starting Backend Server...")
        backend_process = run_command(
            "python run.py",
            "Backend Server",
            cwd="server"
        )
        
        if backend_process:
            processes.append(("Backend", backend_process))
            print("✅ Backend process started")
        else:
            print("❌ Failed to start backend")
            sys.exit(1)
        
        # Wait for backend to be ready
        print("\n⏳ Waiting for backend to be ready...")
        for i in range(30):
            if check_backend_health():
                print("✅ Backend is ready!")
                break
            time.sleep(1)
            if i % 5 == 0:
                print(f"   Still waiting... ({i+1}/30)")
        else:
            print("⚠️  Backend might not be ready, but continuing...")
        
        # Start Frontend
        print("\n🎨 Starting Frontend Development Server...")
        frontend_process = run_command(
            "npm run dev",
            "Frontend Development Server",
            cwd="client"
        )
        
        if frontend_process:
            processes.append(("Frontend", frontend_process))
            print("✅ Frontend process started")
        else:
            print("❌ Failed to start frontend")
            sys.exit(1)
        
        print("\n" + "=" * 50)
        print("🎉 Development Environment Started!")
        print("\n📱 Access your application:")
        print("   Frontend: http://localhost:5173")
        print("   Backend API: http://localhost:5000")
        print("\n🔧 Demo Accounts:")
        print("   Email: hrushikesh@auromart.com")
        print("   Password: password123")
        print("\n⏹️  Press Ctrl+C to stop all servers")
        
        # Keep the script running
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n\n🛑 Stopping development servers...")
        
        # Stop all processes
        for name, process in processes:
            print(f"   Stopping {name}...")
            try:
                process.terminate()
                process.wait(timeout=5)
                print(f"   ✅ {name} stopped")
            except subprocess.TimeoutExpired:
                print(f"   ⚠️  {name} didn't stop gracefully, forcing...")
                process.kill()
            except Exception as e:
                print(f"   ❌ Error stopping {name}: {e}")
        
        print("\n👋 Development environment stopped")
        sys.exit(0)

if __name__ == "__main__":
    main()
