#!/usr/bin/env python3
"""
Initialize MySQL database for AuroMart in Docker
"""

import os
import sys
import time
from pathlib import Path

# Add the server directory to Python path
server_dir = Path(__file__).parent
sys.path.insert(0, str(server_dir))

from app import create_app, db
from app.models.user import User
import uuid

def wait_for_database():
    """Wait for database to be ready"""
    print("⏳ Waiting for database to be ready...")
    max_attempts = 30
    attempt = 0
    
    while attempt < max_attempts:
        try:
            app = create_app()
            with app.app_context():
                with db.engine.connect() as connection:
                    connection.execute(db.text("SELECT 1"))
                print("✅ Database is ready!")
                return True
        except Exception as e:
            attempt += 1
            print(f"⏳ Database not ready yet (attempt {attempt}/{max_attempts}): {e}")
            time.sleep(2)
    
    print("❌ Database connection failed after maximum attempts")
    return False

def init_database():
    """Initialize the database"""
    try:
        app = create_app()
        
        with app.app_context():
            # Create all tables
            print("🔧 Creating database tables...")
            db.create_all()
            
            # Check if we need to seed the database
            user_count = User.query.count()
            if user_count == 0:
                print("🌱 Seeding database with sample data...")
                from app.cli import seed
                seed()
            else:
                print(f"📊 Database already has {user_count} users, skipping seed")
            
            print("✅ Database initialization completed!")
            return True
            
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting AuroMart MySQL database initialization...")
    
    # Wait for database to be ready
    if not wait_for_database():
        sys.exit(1)
    
    # Initialize database
    if not init_database():
        sys.exit(1)
    
    print("🎉 AuroMart MySQL database is ready!")
