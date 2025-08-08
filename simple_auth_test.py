#!/usr/bin/env python3
"""
Simple test of authentication logic without Flask app context
"""
import sys
import os
from pathlib import Path

# Add server directory to path
server_path = Path(__file__).parent / "server"
sys.path.insert(0, str(server_path))

from werkzeug.security import generate_password_hash, check_password_hash

def test_password_hashing():
    """Test password hashing and verification"""
    print("Testing password hashing and verification...")
    
    # Test password hashing
    password = "testpassword123"
    hashed_password = generate_password_hash(password)
    
    print(f"Original password: {password}")
    print(f"Hashed password: {hashed_password}")
    
    # Test password verification
    is_valid = check_password_hash(hashed_password, password)
    print(f"Password verification result: {is_valid}")
    
    # Test with wrong password
    is_invalid = check_password_hash(hashed_password, "wrongpassword")
    print(f"Wrong password verification result: {is_invalid}")
    
    if is_valid and not is_invalid:
        print("Password hashing and verification working correctly")
        return True
    else:
        print("Password hashing or verification failed")
        return False

def test_user_model():
    """Test user model methods"""
    print("\nTesting user model methods...")
    
    # Import User model
    from server.app.models.user import User
    
    # Create a user instance
    user = User(
        name="Test User",
        email="test@example.com",
        role="retailer",
        business_name="Test Business",
        address="123 Test Street",
        phone_number="1234567890"
    )
    
    # Test setting password
    user.set_password("testpassword123")
    print("Password set successfully")
    
    # Test password verification
    if user.check_password("testpassword123"):
        print("Password verification successful")
    else:
        print("Password verification failed")
        return False
    
    # Test with wrong password
    if not user.check_password("wrongpassword"):
        print("Wrong password correctly rejected")
    else:
        print("Wrong password incorrectly accepted")
        return False
    
    # Test to_dict method
    user_dict = user.to_dict()
    print("User to_dict conversion successful")
    print(f"User dict keys: {list(user_dict.keys())}")
    
    return True

if __name__ == "__main__":
    print("Testing AuroMart Authentication Components")
    print("=" * 50)
    
    # Test password hashing
    password_success = test_password_hashing()
    
    # Test user model
    user_success = test_user_model()
    
    print("\n" + "=" * 50)
    if password_success and user_success:
        print("All tests PASSED! Authentication components are working.")
    else:
        print("Some tests FAILED. Please check the implementation.")