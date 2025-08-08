#!/usr/bin/env python3
"""
Initialize database for AuroMart when running with Docker or direct execution
"""

import os
import sys
from pathlib import Path

# Add the server directory to Python path
server_dir = Path(__file__).parent
sys.path.insert(0, str(server_dir))

# Set environment variables for MySQL connection if not already set
if not os.environ.get('DATABASE_URL'):
    os.environ['DATABASE_URL'] = 'mysql+pymysql://admin:123%40Hrushi@3.249.132.231:3306/wa'

if not os.environ.get('FLASK_ENV'):
    os.environ['FLASK_ENV'] = 'development'

from app import create_app, db
from app.models.user import User

def init_database():
    """Initialize the database with tables and sample data"""
    print("🔧 Initializing AuroMart database...")
    
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
                firstName="John",
                lastName="Retailer",
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
                firstName="Jane",
                lastName="Distributor",
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
                firstName="Bob",
                lastName="Manufacturer",
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

if __name__ == "__main__":
    success = init_database()
    
    if success:
        print("🎉 Database is ready for testing!")
    else:
        print("💥 Database initialization failed!")
        sys.exit(1)
