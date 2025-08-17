#!/usr/bin/env python3
"""
Test new EC2 database connectivity
"""

import pymysql
import socket
import sys
import time

def test_new_ec2_database():
    """Test connection to new EC2 database"""
    print("🔍 Testing new EC2 database connection...")
    print("📍 Database: 54.247.8.53:3306")
    print("👤 User: admin")
    print("🗄️  Database: wa")
    
    try:
        # Test network connectivity first
        print("   Testing network connectivity...")
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        result = sock.connect_ex(('54.247.8.53', 3306))
        sock.close()
        
        if result == 0:
            print("   ✅ Port 3306 is reachable")
        else:
            print(f"   ❌ Port 3306 not reachable (error: {result})")
            return False
        
        # Test MySQL connection
        print("   Testing MySQL connection...")
        connection = pymysql.connect(
            host='54.247.8.53',
            port=3306,
            user='admin',
            password='123@Hrushi',
            database='wa',
            charset='utf8mb4',
            connect_timeout=10
        )
        
        print("✅ Successfully connected to new EC2 MySQL database!")
        
        # Test a simple query
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1 as test")
            result = cursor.fetchone()
            print(f"✅ Query test successful: {result}")
        
        connection.close()
        print("✅ Database connection test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        print("\n🔧 Troubleshooting tips:")
        print("1. Check if new EC2 instance is running")
        print("2. Verify security group allows port 3306")
        print("3. Check if MySQL service is running on EC2")
        print("4. Verify credentials are correct")
        return False

if __name__ == "__main__":
    success = test_new_ec2_database()
    sys.exit(0 if success else 1)
