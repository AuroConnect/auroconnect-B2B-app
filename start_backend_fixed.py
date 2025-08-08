#!/usr/bin/env python3
"""
Start Flask backend connecting to EC2 MySQL database (Fixed version)
"""

import os
import sys
from pathlib import Path

# Add the server directory to Python path
server_dir = Path(__file__).parent / "server"
sys.path.insert(0, str(server_dir))

# Set environment variables for EC2 MySQL connection
os.environ['DATABASE_URL'] = 'mysql+pymysql://admin:123@Hrushi@3.249.132.231:3306/wa'
os.environ['FLASK_ENV'] = 'development'
os.environ['SECRET_KEY'] = 'auromart-secret-key-2024-super-secure'
os.environ['JWT_SECRET_KEY'] = 'auromart-jwt-secret-key-2024-super-secure'
os.environ['REDIS_URL'] = 'redis://localhost:6379'

def main():
    """Main function to start the backend"""
    print("🚀 Starting AuroMart Backend...")
    print("📊 Connecting to MySQL database on EC2 (3.249.132.231)...")
    
    try:
        from app import create_app
        
        # Create Flask app
        app = create_app()
        
        print("🌐 Starting Flask server on http://localhost:5000")
        print("📱 Frontend will be available on http://localhost:3000")
        print("🔗 API endpoints available at http://localhost:5000/api")
        print("💡 Database tables will be created automatically on first request")
        
        # Start the Flask server
        app.run(
            host='0.0.0.0',
            port=5000,
            debug=True,
            use_reloader=False  # Disable reloader to avoid context issues
        )
        
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("💡 Please install dependencies: pip install PyMySQL cryptography")
    except Exception as e:
        print(f"❌ Error starting backend: {e}")
        print("💡 Make sure your EC2 MySQL server is accessible")

if __name__ == "__main__":
    main()
