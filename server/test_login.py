#!/usr/bin/env python3

from app import create_app, db
from app.models import User
from werkzeug.security import check_password_hash

def test_login():
    app = create_app()
    with app.app_context():
        # Check if users exist
        users = User.query.all()
        print(f"Total users in database: {len(users)}")
        
        # Check specific test user
        test_user = User.query.filter_by(email="retailer1@test.com").first()
        if test_user:
            print(f"Found user: {test_user.email}")
            print(f"Password hash: {test_user.password_hash[:50]}...")
            print(f"Is active: {test_user.is_active}")
            
            # Test password check
            is_valid = test_user.check_password("password123")
            print(f"Password check result: {is_valid}")
            
            # Test with wrong password
            is_invalid = test_user.check_password("wrongpassword")
            print(f"Wrong password check result: {is_invalid}")
        else:
            print("User retailer1@test.com not found!")
            
        # List all users
        print("\nAll users:")
        for user in users:
            print(f"- {user.email} ({user.role}) - Active: {user.is_active}")

if __name__ == "__main__":
    test_login() 