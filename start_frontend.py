#!/usr/bin/env python3
"""
Start React frontend directly (without Docker)
"""

import os
import subprocess
import sys
from pathlib import Path

def main():
    """Main function to start the frontend"""
    print("Starting AuroMart Frontend...")
    
    # Set environment variable for API URL
    os.environ['REACT_APP_API_URL'] = 'http://localhost:5000'
    
    # Change to client directory
    client_dir = Path(__file__).parent / "client"
    os.chdir(client_dir)
    
    print("Starting React development server...")
    print("Frontend will be available on http://localhost:3000")
    print("Backend API should be running on http://localhost:5000")
    
    # Start the React development server
    try:
        subprocess.run(["npm", "run", "dev"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Failed to start frontend: {e}")
        print("Make sure you have Node.js and npm installed")
        sys.exit(1)
    except FileNotFoundError:
        print("npm not found. Please install Node.js and npm")
        sys.exit(1)

if __name__ == "__main__":
    main()
