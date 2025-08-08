#!/usr/bin/env python3
"""
Script to update existing users in the database
"""
import pymysql
from werkzeug.security import generate_password_hash

# Database configuration
DB_CONFIG = {
    'host': '3.249.132.231',
    'port': 3306,
    'user': 'admin',
    'password': '123@Hrushi',
    'database': 'wa'
}

def update_existing_users():
    """Update existing users"""
    print("Updating existing users...")
    
    try:
        # Connect to database
        conn = pymysql.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Update sample users with correct password hash and is_active flag
        sample_users = [
            {
                'email': 'retailer@example.com',
                'password': 'password123',
                'name': 'John Retailer',
                'role': 'retailer'
            },
            {
                'email': 'distributor@example.com',
                'password': 'password123',
                'name': 'Jane Distributor',
                'role': 'distributor'
            },
            {
                'email': 'manufacturer@example.com',
                'password': 'password123',
                'name': 'Bob Manufacturer',
                'role': 'manufacturer'
            }
        ]
        
        for user in sample_users:
            print(f"Updating user: {user['email']}")
            
            # Generate password hash
            password_hash = generate_password_hash(user['password'])
            
            # Update user
            cursor.execute("""
                UPDATE users 
                SET password_hash = %s, name = %s, role = %s, is_active = 1
                WHERE email = %s
            """, (password_hash, user['name'], user['role'], user['email']))
            
            # If user doesn't exist, create it
            if cursor.rowcount == 0:
                print(f"User {user['email']} not found, creating...")
                cursor.execute("""
                    INSERT INTO users (id, name, email, password_hash, role, is_active, created_at, updated_at)
                    VALUES (UUID(), %s, %s, %s, %s, 1, NOW(), NOW())
                """, (user['name'], user['email'], password_hash, user['role']))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print("Existing users updated successfully!")
        return True
        
    except Exception as e:
        print(f"Failed to update existing users: {e}")
        return False

if __name__ == "__main__":
    update_existing_users()