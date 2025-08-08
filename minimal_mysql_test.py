#!/usr/bin/env python3
"""
Minimal MySQL connection test
"""
import pymysql

def test_mysql_connection():
    """Test MySQL connection directly"""
    print("Testing MySQL connection directly...")
    
    try:
        # Connection parameters
        # URL encode the password to handle special characters like '@'
        connection = pymysql.connect(
            host='3.249.132.231',
            port=3306,
            user='admin',
            password='123@Hrushi',
            database='wa',
            connect_timeout=10
        )
        
        print("MySQL connection successful!")
        connection.close()
        return True
        
    except Exception as e:
        print(f"MySQL connection failed: {e}")
        return False

if __name__ == "__main__":
    success = test_mysql_connection()
    if success:
        print("MySQL connection test PASSED!")
    else:
        print("MySQL connection test FAILED!")