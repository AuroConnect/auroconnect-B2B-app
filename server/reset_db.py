#!/usr/bin/env python3
"""
Database reset script for AuroMart
"""

import os
import sys
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

def reset_database():
    """Reset the database to a clean state"""
    
    # Database configuration
    DB_NAME = "auromart"
    DB_USER = "auromart"
    DB_PASSWORD = "auromart123"
    DB_HOST = "localhost"
    DB_PORT = "5432"
    
    try:
        # Connect to PostgreSQL server
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database="postgres"  # Connect to default database first
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Drop database if it exists
        print("🗑️  Dropping existing database...")
        cursor.execute(f"DROP DATABASE IF EXISTS {DB_NAME}")
        
        # Create new database
        print("📦 Creating new database...")
        cursor.execute(f"CREATE DATABASE {DB_NAME}")
        
        cursor.close()
        conn.close()
        
        # Connect to the new database and run init script
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        cursor = conn.cursor()
        
        # Read and execute init.sql
        print("🔧 Running initialization script...")
        init_sql_path = os.path.join(os.path.dirname(__file__), "..", "init.sql")
        
        with open(init_sql_path, 'r') as f:
            init_sql = f.read()
        
        cursor.execute(init_sql)
        conn.commit()
        
        cursor.close()
        conn.close()
        
        print("✅ Database reset completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Database reset failed: {e}")
        return False

if __name__ == "__main__":
    print("🔄 Resetting AuroMart database...")
    success = reset_database()
    
    if success:
        print("🎉 Database is ready for testing!")
    else:
        print("💥 Database reset failed!")
        sys.exit(1)
