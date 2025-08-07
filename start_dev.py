#!/usr/bin/env python3
"""
Development startup script for AuroMart
"""

import os
import sys
import subprocess
import time
import signal
import threading
from pathlib import Path

def run_command(command, cwd, name):
    """Run a command in a subprocess"""
    try:
        print(f"🚀 Starting {name}...")
        process = subprocess.Popen(
            command,
            cwd=cwd,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1
        )
        
        # Print output in real-time
        for line in process.stdout:
            print(f"[{name}] {line.rstrip()}")
        
        return process
    except Exception as e:
        print(f"❌ Failed to start {name}: {e}")
        return None

def main():
    """Start both frontend and backend"""
    print("🎯 Starting AuroMart Development Environment...")
    print("=" * 60)
    
    # Get the project root directory
    project_root = Path(__file__).parent
    server_dir = project_root / "server"
    client_dir = project_root / "client"
    
    # Check if directories exist
    if not server_dir.exists():
        print(f"❌ Server directory not found: {server_dir}")
        return
    
    if not client_dir.exists():
        print(f"❌ Client directory not found: {client_dir}")
        return
    
    processes = []
    
    try:
        # Start backend server
        backend_process = run_command(
            "python run.py",
            server_dir,
            "Backend Server"
        )
        
        if backend_process:
            processes.append(backend_process)
            print("⏳ Waiting for backend to start...")
            time.sleep(3)  # Give backend time to start
        
        # Start frontend
        frontend_process = run_command(
            "npm run dev",
            client_dir,
            "Frontend"
        )
        
        if frontend_process:
            processes.append(frontend_process)
        
        print("✅ Both servers started!")
        print("🌐 Frontend: http://localhost:3000")
        print("🔧 Backend: http://localhost:5000")
        print("📊 Health Check: http://localhost:5000/api/health")
        print("=" * 60)
        print("Press Ctrl+C to stop all servers")
        
        # Wait for processes
        for process in processes:
            process.wait()
            
    except KeyboardInterrupt:
        print("\n🛑 Stopping servers...")
        for process in processes:
            if process:
                process.terminate()
                process.wait()
        print("✅ All servers stopped")

if __name__ == "__main__":
    main()
