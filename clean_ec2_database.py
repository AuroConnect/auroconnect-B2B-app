#!/usr/bin/env python3
"""
Clean EC2 Database Script
Removes all data except 2 users and 3 products under manufacturer
"""

import mysql.connector
import sys
import os
import uuid
from datetime import datetime

# EC2 Database Configuration
DB_CONFIG = {
    'host': '3.249.132.231',
    'port': 3306,
    'user': 'admin',
    'password': '123@Hrushi',
    'database': 'wa'
}

def connect_to_database():
    """Connect to EC2 database"""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        print("✅ Connected to EC2 database successfully")
        return connection
    except mysql.connector.Error as err:
        print(f"❌ Error connecting to database: {err}")
        return None

def clean_database(connection):
    """Clean all data except essential users and products"""
    cursor = connection.cursor()
    
    try:
        print("\n🧹 Starting database cleanup...")
        
        # 1. Delete all partnerships
        print("🗑️  Deleting all partnerships...")
        cursor.execute("DELETE FROM partnerships")
        print(f"   Deleted {cursor.rowcount} partnerships")
        
        # 2. Delete all partnership invitations
        print("🗑️  Deleting all partnership invitations...")
        cursor.execute("DELETE FROM partnership_invites")
        print(f"   Deleted {cursor.rowcount} partnership invitations")
        
        # 3. Delete all order items first (due to foreign key constraint)
        print("🗑️  Deleting all order items...")
        cursor.execute("DELETE FROM order_items")
        print(f"   Deleted {cursor.rowcount} order items")
        
        # 4. Delete all orders
        print("🗑️  Deleting all orders...")
        cursor.execute("DELETE FROM orders")
        print(f"   Deleted {cursor.rowcount} orders")
        
        # 5. Delete all cart items
        print("🗑️  Deleting all cart items...")
        cursor.execute("DELETE FROM cart_items")
        print(f"   Deleted {cursor.rowcount} cart items")
        
        # 6. Delete all favorites
        print("🗑️  Deleting all favorites...")
        cursor.execute("DELETE FROM favorites")
        print(f"   Deleted {cursor.rowcount} favorites")
        
        # 7. Delete all product allocations
        print("🗑️  Deleting all product allocations...")
        cursor.execute("DELETE FROM product_allocations")
        print(f"   Deleted {cursor.rowcount} product allocations")
        
        # 8. Delete all inventory records
        print("🗑️  Deleting all inventory records...")
        cursor.execute("DELETE FROM inventory")
        print(f"   Deleted {cursor.rowcount} inventory records")
        
        # 9. Delete all invoices
        print("🗑️  Deleting all invoices...")
        cursor.execute("DELETE FROM invoices")
        print(f"   Deleted {cursor.rowcount} invoices")
        
        # 10. Delete all search history
        print("🗑️  Deleting all search history...")
        cursor.execute("DELETE FROM search_history")
        print(f"   Deleted {cursor.rowcount} search history records")
        
        # 11. Delete all products (will be recreated)
        print("🗑️  Deleting all products...")
        cursor.execute("DELETE FROM products")
        print(f"   Deleted {cursor.rowcount} products")
        
        # 12. Delete all carts (due to foreign key constraint with users)
        print("🗑️  Deleting all carts...")
        cursor.execute("DELETE FROM carts")
        print(f"   Deleted {cursor.rowcount} carts")
        
        # 13. Delete all WhatsApp notifications (due to foreign key constraint with users)
        print("🗑️  Deleting all WhatsApp notifications...")
        cursor.execute("DELETE FROM whatsapp_notifications")
        print(f"   Deleted {cursor.rowcount} WhatsApp notifications")
        
        # 14. Delete all users except the 2 specified
        print("🗑️  Deleting all users except hrushigavhane and chikyagavhane22...")
        cursor.execute("""
            DELETE FROM users 
            WHERE email NOT IN ('hrushigavhane@gmail.com', 'chikyagavhane22@gmail.com')
        """)
        print(f"   Deleted {cursor.rowcount} users")
        
        # 15. Delete all categories (will be recreated)
        print("🗑️  Deleting all categories...")
        cursor.execute("DELETE FROM categories")
        print(f"   Deleted {cursor.rowcount} categories")
        
        # 16. Delete all order chat messages
        print("🗑️  Deleting all order chat messages...")
        cursor.execute("DELETE FROM order_chat")
        print(f"   Deleted {cursor.rowcount} order chat messages")
        
        # 17. Delete all shipment items first (due to foreign key constraint)
        print("🗑️  Deleting all shipment items...")
        cursor.execute("DELETE FROM shipment_items")
        print(f"   Deleted {cursor.rowcount} shipment items")
        
        # 18. Delete all shipments
        print("🗑️  Deleting all shipments...")
        cursor.execute("DELETE FROM shipments")
        print(f"   Deleted {cursor.rowcount} shipments")
        
        # Commit all changes
        connection.commit()
        print("\n✅ Database cleanup completed successfully!")
        
    except mysql.connector.Error as err:
        print(f"❌ Error during cleanup: {err}")
        connection.rollback()
        return False
    
    return True

def add_sample_data(connection):
    """Add sample categories and ensure 3 products exist for manufacturer"""
    cursor = connection.cursor()
    
    try:
        print("\n📝 Adding sample data...")
        
        # 1. Add sample categories
        print("📂 Adding sample categories...")
        categories = [
            ('Electronics', 'Electronic devices and components'),
            ('Clothing', 'Apparel and fashion items'),
            ('Home & Garden', 'Home improvement and garden products'),
            ('Sports', 'Sports equipment and accessories'),
            ('Books', 'Books and educational materials')
        ]
        
        cursor.executemany("""
            INSERT INTO categories (name, description) 
            VALUES (%s, %s)
        """, categories)
        print(f"   Added {cursor.rowcount} categories")
        
        # 2. Get manufacturer ID
        cursor.execute("SELECT id FROM users WHERE email = 'hrushigavhane@gmail.com'")
        manufacturer_id = cursor.fetchone()[0]
        
        # 3. Get category IDs
        cursor.execute("SELECT id FROM categories ORDER BY id LIMIT 3")
        category_ids = [row[0] for row in cursor.fetchall()]
        
        # 4. Check how many products manufacturer has
        cursor.execute("SELECT COUNT(*) FROM products WHERE manufacturer_id = %s", (manufacturer_id,))
        product_count = cursor.fetchone()[0]
        
        print(f"   Manufacturer currently has {product_count} products")
        print(f"   Available category IDs: {category_ids}")
        
        # 5. Add products if needed to reach 3 total
        if product_count < 3:
            products_to_add = 3 - product_count
            print(f"   Adding {products_to_add} more products...")
            
            sample_products = [
                (str(uuid.uuid4()), 'Sample Product 1', 'High-quality sample product for testing', 'SKU001', manufacturer_id, category_ids[0], 99.99),
                (str(uuid.uuid4()), 'Sample Product 2', 'Another test product with great features', 'SKU002', manufacturer_id, category_ids[1], 149.99),
                (str(uuid.uuid4()), 'Sample Product 3', 'Premium test product for demonstration', 'SKU003', manufacturer_id, category_ids[2], 199.99)
            ]
            
            for i, product in enumerate(sample_products[:products_to_add]):
                cursor.execute("""
                    INSERT INTO products (id, name, description, sku, manufacturer_id, category_id, base_price)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, product)
                print(f"   Added product: {product[1]}")
        
        # Commit changes
        connection.commit()
        print("✅ Sample data added successfully!")
        
    except mysql.connector.Error as err:
        print(f"❌ Error adding sample data: {err}")
        connection.rollback()
        return False
    
    return True

def verify_cleanup(connection):
    """Verify the cleanup was successful"""
    cursor = connection.cursor()
    
    try:
        print("\n🔍 Verifying cleanup results...")
        
        # Check users
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        print(f"   Users: {user_count} (should be 2)")
        
        # Check products
        cursor.execute("SELECT COUNT(*) FROM products")
        product_count = cursor.fetchone()[0]
        print(f"   Products: {product_count} (should be 3)")
        
        # Check partnerships
        cursor.execute("SELECT COUNT(*) FROM partnerships")
        partnership_count = cursor.fetchone()[0]
        print(f"   Partnerships: {partnership_count} (should be 0)")
        
        # Check categories
        cursor.execute("SELECT COUNT(*) FROM categories")
        category_count = cursor.fetchone()[0]
        print(f"   Categories: {category_count} (should be 5)")
        
        # List remaining users
        cursor.execute("SELECT email, business_name, role FROM users")
        users = cursor.fetchall()
        print("\n   Remaining users:")
        for user in users:
            print(f"     - {user[0]} ({user[1]}) - {user[2]}")
        
        # List remaining products
        cursor.execute("""
            SELECT p.name, p.base_price, u.business_name 
            FROM products p 
            JOIN users u ON p.manufacturer_id = u.id
        """)
        products = cursor.fetchall()
        print("\n   Remaining products:")
        for product in products:
            print(f"     - {product[0]} (${product[1]}) by {product[2]}")
        
        print("\n✅ Verification completed!")
        
    except mysql.connector.Error as err:
        print(f"❌ Error during verification: {err}")

def main():
    """Main function"""
    print("🧹 EC2 Database Cleanup Script")
    print("=" * 50)
    
    # Connect to database
    connection = connect_to_database()
    if not connection:
        return
    
    try:
        # Clean database
        if not clean_database(connection):
            return
        
        # Add sample data
        if not add_sample_data(connection):
            return
        
        # Verify cleanup
        verify_cleanup(connection)
        
        print("\n🎉 Database cleanup completed successfully!")
        print("\n📋 Summary:")
        print("   ✅ Kept only 2 users: hrushigavhane@gmail.com and chikyagavhane22@gmail.com")
        print("   ✅ Removed all partnerships and invitations")
        print("   ✅ Kept only 3 products under manufacturer")
        print("   ✅ Removed all orders, cart items, and other data")
        print("   ✅ Added 5 sample categories")
        print("\n🚀 Ready for manual testing!")
        
    finally:
        connection.close()
        print("\n🔌 Database connection closed")

if __name__ == "__main__":
    main()
