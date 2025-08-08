#!/usr/bin/env python3
"""
Comprehensive fix for backend issues
"""

import os
import subprocess
import time
import sys

def update_requirements():
    """Update requirements.txt with missing dependencies"""
    print("📦 Updating requirements.txt...")
    
    requirements_content = """Flask==2.3.3
Flask-SQLAlchemy==3.0.5
Flask-Migrate==4.0.5
Flask-Login==0.6.3
Flask-CORS==4.0.0
Flask-JWT-Extended==4.5.3
Flask-Bcrypt==1.0.1
psycopg2-binary==2.9.7
redis==5.0.1
pandas==2.1.1
openpyxl==3.1.2
Werkzeug==2.3.7
python-dotenv==1.0.0
marshmallow==3.20.1
marshmallow-sqlalchemy==0.29.0
requests==2.31.0
"""
    
    with open("server/requirements.txt", "w") as f:
        f.write(requirements_content)
    
    print("✅ Requirements.txt updated!")

def update_user_model():
    """Update User model to match initialization script"""
    print("👤 Updating User model...")
    
    user_model_content = '''from app import db
from datetime import datetime
import uuid
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    first_name = db.Column(db.String(255), nullable=False)
    last_name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), nullable=False, default='retailer')  # manufacturer, distributor, retailer
    business_name = db.Column(db.Text, nullable=True)
    address = db.Column(db.Text, nullable=True)
    phone_number = db.Column(db.String(50), nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __init__(self, **kwargs):
        password = kwargs.pop('password', None)
        super(User, self).__init__(**kwargs)
        if password:
            self.set_password(password)
    
    @property
    def name(self):
        """Get full name"""
        return f"{self.first_name} {self.last_name}"
    
    def set_password(self, password):
        """Set password hash"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check password hash"""
        if not self.password_hash:
            return False
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'firstName': self.first_name,
            'lastName': self.last_name,
            'name': self.name,
            'email': self.email,
            'role': self.role,
            'businessName': self.business_name,
            'address': self.address,
            'phoneNumber': self.phone_number,
            'isActive': self.is_active,
            'createdAt': self.created_at.isoformat() if self.created_at else None,
            'updatedAt': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def to_public_dict(self):
        """Convert to public dictionary (without sensitive info)"""
        return {
            'id': self.id,
            'firstName': self.first_name,
            'lastName': self.last_name,
            'name': self.name,
            'role': self.role,
            'businessName': self.business_name,
            'address': self.address,
            'phoneNumber': self.phone_number
        }
    
    def get_dashboard_url(self):
        """Get dashboard URL based on role"""
        if self.role == 'manufacturer':
            return '/manufacturer/dashboard'
        elif self.role == 'distributor':
            return '/distributor/dashboard'
        elif self.role == 'retailer':
            return '/retailer/dashboard'
        return '/dashboard'
    
    def __repr__(self):
        return f'<User {self.email}>'
'''
    
    with open("server/app/models/user.py", "w") as f:
        f.write(user_model_content)
    
    print("✅ User model updated!")

def update_dockerfile():
    """Update Dockerfile with better startup script"""
    print("🐳 Updating Dockerfile...")
    
    dockerfile_content = '''FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    gcc \\
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies first
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \\
    CMD python -c "import requests; requests.get('http://localhost:5000/api/health')" || exit 1

# Create startup script
RUN echo '#!/bin/bash\\n\\
set -e\\n\\
echo "🔧 Initializing database..."\\n\\
python init_db_docker.py\\n\\
echo "🚀 Starting server..."\\n\\
python run.py' > /app/start.sh && chmod +x /app/start.sh

# Run the startup script
CMD ["/app/start.sh"]
'''
    
    with open("server/Dockerfile", "w") as f:
        f.write(dockerfile_content)
    
    print("✅ Dockerfile updated!")

def restart_services():
    """Restart Docker services"""
    print("🔄 Restarting Docker services...")
    
    # Stop all services
    subprocess.run(["docker-compose", "down"], check=True)
    
    # Rebuild and start
    subprocess.run(["docker-compose", "up", "-d", "--build"], check=True)
    
    print("✅ Services restarted!")

def wait_for_backend():
    """Wait for backend to be ready"""
    print("⏳ Waiting for backend to be ready...")
    
    max_attempts = 60
    attempt = 0
    
    while attempt < max_attempts:
        try:
            import requests
            response = requests.get("http://localhost:5000/api/health", timeout=5)
            if response.status_code == 200:
                print("✅ Backend is ready!")
                return True
        except:
            pass
        
        attempt += 1
        print(f"⏳ Waiting for backend... (attempt {attempt}/{max_attempts})")
        time.sleep(5)
    
    print("❌ Backend failed to start")
    return False

def main():
    """Main function"""
    print("🔧 Fixing AuroMart Backend Issues")
    print("=" * 50)
    
    try:
        # Update files
        update_requirements()
        update_user_model()
        update_dockerfile()
        
        # Restart services
        restart_services()
        
        # Wait for backend
        if wait_for_backend():
            print("\n🎉 Backend issues fixed successfully!")
            print("✅ All services are running!")
            print("\n📋 Test URLs:")
            print("  - Frontend: http://localhost:3000")
            print("  - Backend: http://localhost:5000")
            print("  - Health: http://localhost:5000/api/health")
        else:
            print("\n❌ Backend still has issues")
            print("Check logs with: docker-compose logs backend")
            return False
            
    except Exception as e:
        print(f"❌ Error during fix: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
