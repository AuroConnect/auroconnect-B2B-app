#!/usr/bin/env python3
"""
Test EC2 MySQL connection and check database tables
"""

import pymysql
import os

def test_mysql_connection():
    """Test connection to EC2 MySQL server"""
    print("🔍 TESTING EC2 MYSQL CONNECTION")
    print("=" * 50)
    
    # Database configuration
    DB_HOST = '3.249.132.231'
    DB_PORT = 3306
    DB_USER = 'admin'
    DB_PASSWORD = '123@Hrushi'
    DB_NAME = 'wa'
    
    try:
        print(f"Connecting to MySQL at {DB_HOST}:{DB_PORT}...")
        print(f"Database: {DB_NAME}")
        print(f"User: {DB_USER}")
        
        # Connect to MySQL
        connection = pymysql.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            charset='utf8mb4'
        )
        
        print("✅ Successfully connected to EC2 MySQL server!")
        
        # Check if tables exist
        cursor = connection.cursor()
        
        # Get list of tables
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        
        print(f"\n📋 Tables in database '{DB_NAME}':")
        print("=" * 30)
        
        if tables:
            for table in tables:
                table_name = table[0]
                print(f"✅ {table_name}")
                
                # Check table structure
                cursor.execute(f"DESCRIBE {table_name}")
                columns = cursor.fetchall()
                print(f"   Columns: {len(columns)}")
                for col in columns:
                    print(f"     - {col[0]} ({col[1]})")
                print()
        else:
            print("❌ No tables found in database")
        
        # Check users table specifically
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        print(f"👥 Users in database: {user_count}")
        
        cursor.close()
        connection.close()
        
        print("\n🎉 EC2 MySQL connection test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Failed to connect to EC2 MySQL: {e}")
        return False

if __name__ == "__main__":
    test_mysql_connection()
