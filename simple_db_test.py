#!/usr/bin/env python3
"""
Simple test script to verify database connection without emojis
"""
import sys
import os
from pathlib import Path

# Add the server directory to Python path
server_dir = Path(__file__).parent / "server"
sys.path.insert(0, str(server_dir))

# Set environment variables for MySQL connection
os.environ['DATABASE_URL'] = 'mysql+pymysql://admin:123@Hrushi@3.249.132.231:3306/wa'
os.environ['FLASK_ENV'] = 'development'

from app import create_app, db

def test_db_connection():
    """Test the database connection"""
    print("Testing database connection...")
    
    try:
        # Create Flask app
        app = create_app()
        
        with app.app_context():
            # Test database connection
            try:
                with db.engine.connect() as connection:
                    result = connection.execute(db.text("SELECT 1"))
                    print("Database connection successful!")
                    return True
            except Exception as e:
                print(f"Database connection failed: {e}")
                return False
                
    except Exception as e:
        print(f"Failed to create app: {e}")
        return False

if __name__ == "__main__":
    success = test_db_connection()
    if success:
        print("Database connection test PASSED!")
    else:
        print("Database connection test FAILED!")
    sys.exit(0 if success else 1)