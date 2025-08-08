#!/usr/bin/env python3
"""
Create users table in MySQL database
"""

import os
import sys
from pathlib import Path

# Add the server directory to Python path
server_dir = Path(__file__).parent / "server"
sys.path.insert(0, str(server_dir))

# Set environment variables for EC2 MySQL connection
os.environ['DATABASE_URL'] = 'mysql+pymysql://admin:123%40Hrushi@3.249.132.231:3306/wa'

def main():
    """Create users table"""
    print("🔧 Creating users table in MySQL database...")
    
    try:
        from flask import Flask
        from flask_sqlalchemy import SQLAlchemy
        
        # Create a simple Flask app
        app = Flask(__name__)
        
        # Configure database
        app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        
        # Initialize extensions
        db = SQLAlchemy(app)
        
        with app.app_context():
            # Create users table
            db.session.execute(db.text("""
                CREATE TABLE IF NOT EXISTS users (
                    id VARCHAR(36) PRIMARY KEY,
                    email VARCHAR(255) UNIQUE NOT NULL,
                    password_hash VARCHAR(255) NOT NULL,
                    first_name VARCHAR(100) NOT NULL,
                    last_name VARCHAR(100) NOT NULL,
                    role VARCHAR(50) NOT NULL,
                    business_name VARCHAR(255),
                    address TEXT,
                    phone_number VARCHAR(20),
                    whatsapp_number VARCHAR(20),
                    created_at DATETIME NOT NULL,
                    updated_at DATETIME NOT NULL,
                    INDEX idx_email (email),
                    INDEX idx_role (role)
                )
            """))
            
            db.session.commit()
            print("✅ Users table created successfully!")
            
    except Exception as e:
        print(f"❌ Error creating users table: {e}")
        return False
    
    return True

if __name__ == "__main__":
    main()
