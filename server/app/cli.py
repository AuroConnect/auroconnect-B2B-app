import click
from flask.cli import with_appcontext
from app import db
from app.models import User, Category
import uuid

def register_commands(app):
    """Register CLI commands"""
    
    @app.cli.command()
    @with_appcontext
    def init_db():
        """Initialize the database"""
        db.create_all()
        click.echo('Database initialized!')
    
    @app.cli.command()
    @with_appcontext
    def seed_db():
        """Seed the database with sample data"""
        # Create sample categories
        categories = [
            {'name': 'Electronics', 'description': 'Electronic devices and accessories'},
            {'name': 'Clothing', 'description': 'Apparel and fashion items'},
            {'name': 'Home & Garden', 'description': 'Home improvement and garden supplies'},
            {'name': 'Sports', 'description': 'Sports equipment and accessories'},
            {'name': 'Books', 'description': 'Books and educational materials'}
        ]
        
        for cat_data in categories:
            category = Category.query.filter_by(name=cat_data['name']).first()
            if not category:
                category = Category(
                    id=uuid.uuid4(),
                    name=cat_data['name'],
                    description=cat_data['description']
                )
                db.session.add(category)
        
        # Create sample users
        users = [
            {
                'email': 'retailer1@example.com',
                'firstName': 'John',
                'lastName': 'Retailer',
                'role': 'retailer',
                'businessName': 'Retail Store 1',
                'address': '123 Main St, City',
                'phoneNumber': '+1234567890'
            },
            {
                'email': 'distributor1@example.com',
                'firstName': 'Jane',
                'lastName': 'Distributor',
                'role': 'distributor',
                'businessName': 'Distribution Co 1',
                'address': '456 Business Ave, City',
                'phoneNumber': '+1234567891'
            },
            {
                'email': 'manufacturer1@example.com',
                'firstName': 'Bob',
                'lastName': 'Manufacturer',
                'role': 'manufacturer',
                'businessName': 'Manufacturing Co 1',
                'address': '789 Industrial Blvd, City',
                'phoneNumber': '+1234567892'
            }
        ]
        
        for user_data in users:
            user = User.query.filter_by(email=user_data['email']).first()
            if not user:
                user = User(
                    id=uuid.uuid4(),
                    email=user_data['email'],
                    first_name=user_data['firstName'],
                    last_name=user_data['lastName'],
                    role=user_data['role'],
                    business_name=user_data['businessName'],
                    address=user_data['address'],
                    phone_number=user_data['phoneNumber'],
                    is_active=True
                )
                user.set_password('password123')
                db.session.add(user)
        
        db.session.commit()
        click.echo('Database seeded with sample data!')
    
    @app.cli.command()
    @with_appcontext
    def create_admin():
        """Create an admin user"""
        email = click.prompt('Admin email')
        password = click.prompt('Admin password', hide_input=True)
        first_name = click.prompt('First name')
        last_name = click.prompt('Last name')
        
        user = User(
            id=uuid.uuid4(),
            email=email,
            first_name=first_name,
            last_name=last_name,
            role='admin',
            is_active=True
        )
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        click.echo(f'Admin user {email} created successfully!')
    
    @app.cli.command()
    @with_appcontext
    def list_users():
        """List all users"""
        users = User.query.all()
        for user in users:
            click.echo(f'{user.email} - {user.role} - {user.full_name}')
    
    @app.cli.command()
    @with_appcontext
    def reset_db():
        """Reset the database"""
        if click.confirm('Are you sure you want to drop all tables?'):
            db.drop_all()
            db.create_all()
            click.echo('Database reset!') 