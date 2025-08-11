#!/usr/bin/env python3
"""
Check backend logs to diagnose connection issues
"""

import subprocess
import time

def run_command(command, description):
    """Run a command and return output"""
    print(f"\n🔧 {description}...")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, encoding='utf-8', errors='ignore')
        return result.stdout.strip()
    except Exception as e:
        print(f"Error: {e}")
        return ""

def check_container_status():
    """Check if backend container is running"""
    print("📦 CONTAINER STATUS")
    print("=" * 50)
    
    status = run_command("docker ps -a | grep backend", "Checking backend container status")
    print(status)

def check_backend_logs():
    """Check backend logs"""
    print("📋 BACKEND LOGS")
    print("=" * 50)
    
    logs = run_command("docker logs auroconnect-b2b-app-backend-1 --tail 30", "Getting backend logs")
    print(logs)

def check_backend_processes():
    """Check what's running inside the backend container"""
    print("🔍 BACKEND PROCESSES")
    print("=" * 50)
    
    processes = run_command("docker exec auroconnect-b2b-app-backend-1 ps aux", "Checking processes in backend container")
    print(processes)

def check_backend_network():
    """Check network connectivity from backend container"""
    print("🌐 NETWORK CONNECTIVITY")
    print("=" * 50)
    
    # Check if backend can reach the database
    ping_db = run_command("docker exec auroconnect-b2b-app-backend-1 ping -c 3 3.249.132.231", "Pinging database server")
    print("Database server ping:")
    print(ping_db)
    
    # Check if backend can reach port 3306
    telnet_db = run_command("docker exec auroconnect-b2b-app-backend-1 timeout 5 bash -c 'echo > /dev/tcp/3.249.132.231/3306' && echo 'Port 3306 is reachable' || echo 'Port 3306 is not reachable'", "Testing database port connectivity")
    print("Database port test:")
    print(telnet_db)

def check_backend_environment():
    """Check environment variables in backend container"""
    print("🔧 ENVIRONMENT VARIABLES")
    print("=" * 50)
    
    env = run_command("docker exec auroconnect-b2b-app-backend-1 env | grep -E '(DATABASE|MYSQL)'", "Checking database environment variables")
    print(env)

def main():
    """Main function"""
    print("🔍 BACKEND DIAGNOSTICS")
    print("=" * 50)
    
    # Check container status
    check_container_status()
    
    # Check backend logs
    check_backend_logs()
    
    # Check environment variables
    check_backend_environment()
    
    # Check network connectivity
    check_backend_network()
    
    # Check processes
    check_backend_processes()
    
    print("\n" + "=" * 50)
    print("📋 DIAGNOSIS COMPLETE")
    print("=" * 50)
    print("Check the logs above to see what's causing the connection issues.")

if __name__ == "__main__":
    main()
