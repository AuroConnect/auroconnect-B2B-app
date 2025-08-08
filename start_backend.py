#!/usr/bin/env python3
"""
Start Flask backend directly (without Docker) connecting to EC2 MySQL
"""

import os
import sys
from pathlib import Path

# Add the server directory to Python path
server_dir = Path(__file__).parent / "server"
sys.path.insert(0, str(server_dir))

# Set environment variables for MySQL connection
# URL encode the password to handle special characters like '@'
os.environ['DATABASE_URL'] = 'mysql+pymysql://admin:123%40Hrushi@3.249.132.231:3306/wa'
os.environ['FLASK_ENV'] = 'development'
os.environ['SECRET_KEY'] = 'auromart-secret-key-2024-super-secure'
os.environ['JWT_SECRET_KEY'] = 'auromart-jwt-secret-key-2024-super-secure'

from app import create_app, db
from app.models.user import User

def init_database():
    """Initialize the database with tables and sample data"""
    print("🔧 Initializing AuroMart MySQL database on EC2...")
    
    try:
        # Create Flask app
        app = create_app()
        
        with app.app_context():
            # Create all tables
            print("📦 Creating database tables...")
            db.create_all()
            
            # Check if we already have users
            existing_users = User.query.count()
            if existing_users > 0:
                print(f"✅ Database already has {existing_users} users")
                return True
            
            # Create sample users
            print("👥 Creating sample users...")
            
            # Sample retailer
            retailer = User(
                email="retailer@example.com",
                first_name="John",
                last_name="Retailer",
                role="retailer",
                business_name="Sample Retail Store",
                address="123 Main St, City",
                phone_number="+1234567890"
            )
            retailer.set_password("password123")
            db.session.add(retailer)
            
            # Sample distributor
            distributor = User(
                email="distributor@example.com",
                first_name="Jane",
                last_name="Distributor",
                role="distributor",
                business_name="Sample Distribution Co",
                address="456 Business Ave, City",
                phone_number="+1234567891"
            )
            distributor.set_password("password123")
            db.session.add(distributor)
            
            # Sample manufacturer
            manufacturer = User(
                email="manufacturer@example.com",
                first_name="Bob",
                last_name="Manufacturer",
                role="manufacturer",
                business_name="Sample Manufacturing Co",
                address="789 Industrial Blvd, City",
                phone_number="+1234567892"
            )
            manufacturer.set_password("password123")
            db.session.add(manufacturer)
            
            # Commit changes
            db.session.commit()
            
            print("✅ Database initialized successfully!")
            print("📋 Sample users created:")
            print("  - retailer@example.com (password: password123)")
            print("  - distributor@example.com (password: password123)")
            print("  - manufacturer@example.com (password: password123)")
            
            return True
            
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        return False

def main():
    """Main function to start the backend"""
    print("🚀 Starting AuroMart Backend...")
    print("📊 Connecting to MySQL database on EC2...")
    
    # Initialize database
    if init_database():
        print("🎉 Database ready!")
    else:
        print("⚠️  Database initialization failed, but continuing...")
    
    # Create and run Flask app
    app = create_app()
    
    print("🌐 Starting Flask server on http://localhost:5000")
    print("📱 Frontend will be available on http://localhost:3000")
    print("🔗 API endpoints available at http://localhost:5000/api")
    
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True
    )

if __name__ == "__main__":
    main()
