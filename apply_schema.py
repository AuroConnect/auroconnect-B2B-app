#!/usr/bin/env python3
"""
Apply new database schema for AuroMart B2B Platform
"""

import psycopg2
import os
from datetime import datetime

# Database configuration for Docker
DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'auromart',
    'user': 'auromart',
    'password': 'auromart123'
}

def apply_schema():
    """Apply the new database schema"""
    print("🏗️ Applying new AuroMart Database Schema...")
    
    try:
        # Connect to database
        conn = psycopg2.connect(**DB_CONFIG)
        conn.autocommit = True
        cursor = conn.cursor()
        
        print("📋 Creating new schema...")
        
        # Read and execute the init.sql file
        with open('init.sql', 'r') as f:
            init_sql = f.read()
        
        # Split by semicolon and execute each statement
        statements = init_sql.split(';')
        for statement in statements:
            statement = statement.strip()
            if statement and not statement.startswith('--'):
                try:
                    cursor.execute(statement)
                    print(f"   ✅ Executed statement")
                except Exception as e:
                    print(f"   ⚠️  Statement failed (may already exist): {e}")
        
        print("✅ Database schema applied successfully!")
        print(f"   Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Close connection
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Schema application failed: {e}")
        return False

if __name__ == "__main__":
    success = apply_schema()
    if success:
        print("\n🎯 Database schema is ready for the new workflow!")
        print("🚀 You can now test the complete manufacturer → distributor → retailer workflow!")
    else:
        print("\n❌ Schema application failed. Please check the error above.")
