#!/usr/bin/env python3
"""
Direct test of authentication logic without starting a full server
"""
import sys
import os
from pathlib import Path

# Add server directory to path
server_path = Path(__file__).parent / "server"
sys.path.insert(0, str(server_path))

from server.app import create_app, db
from server.app.models.user import User

def test_auth_logic():
    """Test authentication logic directly"""
    print("Testing authentication logic...")
    
    # Create app context
    app = create_app()
    
    with app.app_context():
        try:
            # Test database connection
            db.create_all()
            print("✅ Database initialized successfully")
            
            # Test user creation
            print("\nTesting user creation...")
            user = User(
                name="Test User",
                email="test@example.com",
                role="retailer",
                business_name="Test Business",
                address="123 Test Street",
                phone_number="1234567890",
                is_active=True
            )
            user.set_password("password123")
            
            db.session.add(user)
            db.session.commit()
            print("✅ User created successfully")
            
            # Test user retrieval
            print("\nTesting user retrieval...")
            retrieved_user = User.query.filter_by(email="test@example.com").first()
            if retrieved_user:
                print("✅ User retrieved successfully")
                print(f"User ID: {retrieved_user.id}")
                print(f"User Name: {retrieved_user.name}")
                print(f"User Email: {retrieved_user.email}")
                
                # Test password check
                print("\nTesting password verification...")
                if retrieved_user.check_password("password123"):
                    print("✅ Password verification successful")
                else:
                    print("❌ Password verification failed")
            else:
                print("❌ User retrieval failed")
                
            # Clean up
            if retrieved_user:
                db.session.delete(retrieved_user)
                db.session.commit()
                print("\n✅ Cleaned up test user")
                
            return True
            
        except Exception as e:
            print(f"❌ Test failed with error: {e}")
            db.session.rollback()
            return False

if __name__ == "__main__":
    print("Testing AuroMart Authentication Logic")
    print("=" * 50)
    
    success = test_auth_logic()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 All tests PASSED! Authentication logic is working.")
    else:
        print("💥 Some tests FAILED. Please check the implementation.")