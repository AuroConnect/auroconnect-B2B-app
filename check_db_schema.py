#!/usr/bin/env python3
"""
Script to check database schema
"""
import pymysql

# Database configuration
DB_CONFIG = {
    'host': '3.249.132.231',
    'port': 3306,
    'user': 'admin',
    'password': '123@Hrushi',
    'database': 'wa'
}

def check_database_schema():
    """Check database schema"""
    print("Checking database schema...")
    
    try:
        # Connect to database
        conn = pymysql.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Get list of tables
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        
        print("Tables in database:")
        for table in tables:
            print(f"  - {table[0]}")
            
            # Get table structure
            cursor.execute(f"DESCRIBE {table[0]}")
            columns = cursor.fetchall()
            
            print(f"    Columns:")
            for column in columns:
                print(f"      - {column[0]} ({column[1]}) {'PRIMARY KEY' if column[3] == 'PRI' else ''}")
            print()
        
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"Database schema check failed: {e}")
        return False

if __name__ == "__main__":
    check_database_schema()