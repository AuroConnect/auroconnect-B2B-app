#!/usr/bin/env python3
"""
Reset database with new schema for AuroMart B2B Platform
"""

import psycopg2
import os
from datetime import datetime

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'auromart',
    'user': 'postgres',
    'password': 'password'
}

def reset_database():
    """Reset the database with new schema"""
    print("🔄 Resetting AuroMart Database...")
    
    try:
        # Connect to database
        conn = psycopg2.connect(**DB_CONFIG)
        conn.autocommit = True
        cursor = conn.cursor()
        
        print("📋 Dropping existing tables...")
        
        # Drop all tables in correct order
        drop_queries = [
            "DROP TABLE IF EXISTS whatsapp_notifications CASCADE",
            "DROP TABLE IF EXISTS invoice_items CASCADE",
            "DROP TABLE IF EXISTS invoices CASCADE",
            "DROP TABLE IF EXISTS order_items CASCADE",
            "DROP TABLE IF EXISTS orders CASCADE",
            "DROP TABLE IF EXISTS partnerships CASCADE",
            "DROP TABLE IF EXISTS inventory CASCADE",
            "DROP TABLE IF EXISTS favorites CASCADE",
            "DROP TABLE IF EXISTS search_history CASCADE",
            "DROP TABLE IF EXISTS products CASCADE",
            "DROP TABLE IF EXISTS categories CASCADE",
            "DROP TABLE IF EXISTS users CASCADE"
        ]
        
        for query in drop_queries:
            cursor.execute(query)
            print(f"   ✅ Dropped table")
        
        print("🏗️ Creating new schema...")
        
        # Read and execute the init.sql file
        with open('init.sql', 'r') as f:
            init_sql = f.read()
        
        # Split by semicolon and execute each statement
        statements = init_sql.split(';')
        for statement in statements:
            statement = statement.strip()
            if statement:
                cursor.execute(statement)
        
        print("✅ Database reset completed successfully!")
        print(f"   Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Close connection
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Database reset failed: {e}")
        return False

if __name__ == "__main__":
    success = reset_database()
    if success:
        print("\n🎯 Database is ready for the new workflow!")
        print("🚀 You can now test the complete manufacturer → distributor → retailer workflow!")
    else:
        print("\n❌ Database reset failed. Please check the error above.")
