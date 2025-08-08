#!/usr/bin/env python3
"""
Script to update database schema to match the User model
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

def update_database_schema():
    """Update database schema"""
    print("Updating database schema...")
    
    try:
        # Connect to database
        conn = pymysql.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Check if the users table has the required columns
        cursor.execute("DESCRIBE users")
        columns = cursor.fetchall()
        column_names = [col[0] for col in columns]
        
        print(f"Existing columns: {column_names}")
        
        # Add 'name' column if it doesn't exist
        if 'name' not in column_names:
            print("Adding 'name' column...")
            cursor.execute("ALTER TABLE users ADD COLUMN name VARCHAR(255) AFTER id")
            
            # Populate name column from first_name and last_name
            cursor.execute("UPDATE users SET name = CONCAT(first_name, ' ', last_name) WHERE name = '' OR name IS NULL")
        
        # Add 'is_active' column if it doesn't exist
        if 'is_active' not in column_names:
            print("Adding 'is_active' column...")
            cursor.execute("ALTER TABLE users ADD COLUMN is_active BOOLEAN DEFAULT TRUE AFTER phone_number")
        
        # Add other missing columns if needed
        if 'role' not in column_names:
            print("Adding 'role' column...")
            cursor.execute("ALTER TABLE users ADD COLUMN role VARCHAR(50) DEFAULT 'retailer' AFTER password_hash")
        
        if 'business_name' not in column_names:
            print("Adding 'business_name' column...")
            cursor.execute("ALTER TABLE users ADD COLUMN business_name TEXT AFTER role")
        
        if 'address' not in column_names:
            print("Adding 'address' column...")
            cursor.execute("ALTER TABLE users ADD COLUMN address TEXT AFTER business_name")
        
        if 'updated_at' not in column_names:
            print("Adding 'updated_at' column...")
            cursor.execute("ALTER TABLE users ADD COLUMN updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP AFTER created_at")
        
        # Make email unique if it isn't already
        # This is more complex and might require recreating the table
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print("Database schema updated successfully!")
        return True
        
    except Exception as e:
        print(f"Database schema update failed: {e}")
        return False

if __name__ == "__main__":
    update_database_schema()