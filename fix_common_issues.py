#!/usr/bin/env python3
"""
Fix common issues that might occur during setup
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

def check_port_availability(port):
    """Check if a port is available"""
    import socket
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('localhost', port))
            return True
    except OSError:
        return False

def kill_process_on_port(port):
    """Kill process using a specific port"""
    try:
        if os.name == 'nt':  # Windows
            result = subprocess.run(f"netstat -ano | findstr :{port}", shell=True, capture_output=True, text=True)
            if result.stdout:
                lines = result.stdout.strip().split('\n')
                for line in lines:
                    if f":{port}" in line:
                        parts = line.split()
                        if len(parts) >= 5:
                            pid = parts[-1]
                            subprocess.run(f"taskkill /PID {pid} /F", shell=True)
                            print(f"✅ Killed process {pid} on port {port}")
        else:  # Linux/Mac
            result = subprocess.run(f"lsof -ti:{port}", shell=True, capture_output=True, text=True)
            if result.stdout.strip():
                pids = result.stdout.strip().split('\n')
                for pid in pids:
                    subprocess.run(f"kill -9 {pid}", shell=True)
                    print(f"✅ Killed process {pid} on port {port}")
    except Exception as e:
        print(f"⚠️  Could not kill process on port {port}: {e}")

def fix_common_issues():
    """Fix common issues"""
    
    print("🔧 Fixing Common Issues...")
    print("=" * 50)
    
    # Check and kill processes on required ports
    ports_to_check = [3000, 5000, 3306, 6379]
    
    for port in ports_to_check:
        if not check_port_availability(port):
            print(f"⚠️  Port {port} is in use, attempting to free it...")
            kill_process_on_port(port)
            time.sleep(2)
    
    # Clean up Docker resources
    print("\n🧹 Cleaning up Docker resources...")
    
    # Stop all containers
    run_command("docker-compose down", "Stopping containers")
    
    # Remove containers
    run_command("docker container prune -f", "Removing stopped containers")
    
    # Remove unused images
    run_command("docker image prune -f", "Removing unused images")
    
    # Remove unused volumes
    run_command("docker volume prune -f", "Removing unused volumes")
    
    # Remove unused networks
    run_command("docker network prune -f", "Removing unused networks")
    
    # Clean npm cache (if exists)
    if os.path.exists("client/node_modules"):
        print("\n🧹 Cleaning npm cache...")
        run_command("cd client && npm cache clean --force", "Cleaning npm cache")
    
    # Clean Python cache
    print("\n🧹 Cleaning Python cache...")
    run_command("find . -type d -name '__pycache__' -exec rm -rf {} +", "Removing Python cache")
    run_command("find . -type f -name '*.pyc' -delete", "Removing Python compiled files")
    
    print("\n✅ Common issues fixed!")
    print("🔄 You can now run the setup script again:")
    print("   python setup_complete_2x2_system.py")

def check_system_requirements():
    """Check if system meets requirements"""
    
    print("🔍 Checking System Requirements...")
    print("=" * 50)
    
    # Check Docker
    try:
        result = subprocess.run("docker --version", shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Docker: {result.stdout.strip()}")
        else:
            print("❌ Docker not found")
            return False
    except Exception as e:
        print(f"❌ Docker check failed: {e}")
        return False
    
    # Check Docker Compose
    try:
        result = subprocess.run("docker-compose --version", shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Docker Compose: {result.stdout.strip()}")
        else:
            print("❌ Docker Compose not found")
            return False
    except Exception as e:
        print(f"❌ Docker Compose check failed: {e}")
        return False
    
    # Check Python
    try:
        result = subprocess.run("python --version", shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Python: {result.stdout.strip()}")
        else:
            print("❌ Python not found")
            return False
    except Exception as e:
        print(f"❌ Python check failed: {e}")
        return False
    
    # Check Node.js (for frontend)
    try:
        result = subprocess.run("node --version", shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Node.js: {result.stdout.strip()}")
        else:
            print("⚠️  Node.js not found (will use Docker)")
    except Exception as e:
        print("⚠️  Node.js check failed (will use Docker)")
    
    # Check available memory
    try:
        if os.name == 'nt':  # Windows
            result = subprocess.run("wmic computersystem get TotalPhysicalMemory", shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                if len(lines) > 1:
                    memory_kb = int(lines[1].strip())
                    memory_gb = memory_kb / (1024**3)
                    print(f"✅ System Memory: {memory_gb:.1f} GB")
                    if memory_gb < 4:
                        print("⚠️  Low memory detected. Consider closing other applications.")
        else:  # Linux/Mac
            result = subprocess.run("free -g", shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                if len(lines) > 1:
                    parts = lines[1].split()
                    if len(parts) >= 2:
                        memory_gb = int(parts[1])
                        print(f"✅ System Memory: {memory_gb} GB")
                        if memory_gb < 4:
                            print("⚠️  Low memory detected. Consider closing other applications.")
    except Exception as e:
        print(f"⚠️  Could not check memory: {e}")
    
    # Check available disk space
    try:
        if os.name == 'nt':  # Windows
            result = subprocess.run("wmic logicaldisk get size,freespace,caption", shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                for line in lines[1:]:
                    if line.strip():
                        parts = line.split()
                        if len(parts) >= 3:
                            drive = parts[0]
                            free_space_gb = int(parts[1]) / (1024**3)
                            print(f"✅ Drive {drive} free space: {free_space_gb:.1f} GB")
                            if free_space_gb < 5:
                                print(f"⚠️  Low disk space on {drive}")
        else:  # Linux/Mac
            result = subprocess.run("df -h .", shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                if len(lines) > 1:
                    parts = lines[1].split()
                    if len(parts) >= 4:
                        free_space = parts[3]
                        print(f"✅ Available disk space: {free_space}")
    except Exception as e:
        print(f"⚠️  Could not check disk space: {e}")
    
    print("\n✅ System requirements check completed!")
    return True

if __name__ == "__main__":
    print("🔧 AuroMart System Issue Fixer")
    print("=" * 50)
    
    # Check system requirements first
    if not check_system_requirements():
        print("\n❌ System requirements not met. Please install missing components.")
        exit(1)
    
    # Fix common issues
    fix_common_issues()
    
    print("\n🎉 Issue fixing completed!")
    print("You can now run: python setup_complete_2x2_system.py")
