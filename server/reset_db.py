#!/usr/bin/env python3
"""
Database reset script for AuroMart (MySQL)
"""

import os
import sys
import pymysql
from pymysql.constants import CLIENT

def reset_database():
    """Reset the database to a clean state"""
    
    # Database configuration - Use external MySQL server with Django settings
    DB_NAME = os.environ.get('MYSQL_DATABASE', 'wa')
    DB_USER = os.environ.get('MYSQL_USER', 'admin')
    DB_PASSWORD = os.environ.get('MYSQL_PASSWORD', '123@Hrushi')
    DB_HOST = os.environ.get('MYSQL_HOST', '3.249.132.231')
    DB_PORT = int(os.environ.get('MYSQL_PORT', '3306'))
    
    try:
        # Connect to MySQL server
        conn = pymysql.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            charset='utf8mb4',
            client_flag=CLIENT.MULTI_STATEMENTS
        )
        cursor = conn.cursor()
        
        # Drop database if it exists
        print("🗑️  Dropping existing database...")
        cursor.execute(f"DROP DATABASE IF EXISTS {DB_NAME}")
        
        # Create new database
        print("📦 Creating new database...")
        cursor.execute(f"CREATE DATABASE {DB_NAME} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        
        cursor.close()
        conn.close()
        
        # Connect to the new database and run init script
        conn = pymysql.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            charset='utf8mb4',
            client_flag=CLIENT.MULTI_STATEMENTS
        )
        cursor = conn.cursor()
        
        # Read and execute init.sql
        print("🔧 Running initialization script...")
        init_sql_path = os.path.join(os.path.dirname(__file__), "..", "init.sql")
        
        with open(init_sql_path, 'r') as f:
            init_sql = f.read()
        
        # Split the SQL into individual statements and execute them
        statements = init_sql.split(';')
        for statement in statements:
            statement = statement.strip()
            if statement and not statement.startswith('--'):
                try:
                    cursor.execute(statement)
                except Exception as e:
                    print(f"Warning: Could not execute statement: {e}")
                    continue
        
        conn.commit()
        
        cursor.close()
        conn.close()
        
        print("✅ Database reset completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Database reset failed: {e}")
        return False

if __name__ == "__main__":
    reset_database()
