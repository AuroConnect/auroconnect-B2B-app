# AuroMart Backend API

Flask-based REST API for the AuroMart B2B platform.

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- MySQL (External server at 3.249.132.231)
- Redis (optional, for caching)

### Database Setup
The application is configured to use an external MySQL server at `3.249.132.231` with the following credentials:
- **Host**: 3.249.132.231
- **Port**: 3306
- **Database**: wa
- **Username**: admin
- **Password**: 123@Hrushi

### Installation
```bash
pip install -r requirements.txt
```

### Environment Variables
Create a `.env` file in the server directory:
```bash
# Database Configuration (MySQL)
MYSQL_HOST=3.249.132.231
MYSQL_PORT=3306
MYSQL_USER=admin
MYSQL_PASSWORD=123@Hrushi
MYSQL_DATABASE=wa

# Flask Configuration
FLASK_ENV=development
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-key-here

# Redis Configuration
REDIS_URL=redis://localhost:6379

# CORS Configuration
CORS_ORIGINS=http://localhost:3000,http://localhost:3001,http://localhost:80
```

### Database Initialization
```bash
# Reset database to clean state
python reset_db.py

# Or use Flask CLI
flask init-db
flask seed-db
```

### Running the Server
```bash
python run.py
```

The server will start on http://localhost:5000

## 📊 Database Models

### Core Models
- **User**: Multi-role users (retailer, distributor, manufacturer, admin)
- **Category**: Product categories
- **Product**: Products with manufacturer association
- **Inventory**: Distributor inventory management
- **Order**: Order management with status tracking
- **OrderItem**: Individual items in orders
- **Partnership**: Business partnerships between users
- **Favorite**: User favorite partners
- **SearchHistory**: Search tracking
- **Invoice**: Invoice management
- **WhatsAppNotification**: WhatsApp integration

### 🚀 **API Endpoints**

#### Authentication
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `GET /api/auth/user` - Get current user
- `POST /api/auth/refresh` - Refresh JWT token

#### Partners
- `GET /api/partners/distributors` - Get distributors
- `GET /api/partners/manufacturers` - Get manufacturers (distributors only)
- `GET /api/partners/available` - Get available partners
- `GET /api/partners/search` - Search partners globally

#### Favorites
- `GET /api/favorites` - Get user favorites
- `POST /api/favorites` - Add to favorites
- `DELETE /api/favorites/<id>` - Remove from favorites
- `GET /api/favorites/<id>/check` - Check favorite status

#### Products
- `GET /api/products` - Get products
- `GET /api/products/<id>` - Get specific product
- `POST /api/products` - Create product (manufacturers only)
- `GET /api/products/categories` - Get categories
- `GET /api/products/search` - Search products

#### Orders
- `GET /api/orders` - Get user orders
- `GET /api/orders/<id>` - Get specific order
- `POST /api/orders` - Create order (retailers only)
- `PATCH /api/orders/<id>/status` - Update order status (distributors only)

#### Partnerships
- `GET /api/partnerships` - Get user partnerships
- `POST /api/partnerships/request` - Send partnership request
- `PATCH /api/partnerships/<id>/respond` - Respond to partnership request
- `GET /api/partnerships/received` - Get received requests

#### Search
- `GET /api/search/history` - Get search history
- `POST /api/search/history` - Add search to history

#### Health
- `GET /api/health` - Health check endpoint

## Configuration

### Environment Variables
```env
# Database
DATABASE_URL=mysql+pymysql://admin:123@Hrushi@3.249.132.231:3306/wa?charset=utf8mb4

# Security
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret

# Redis
REDIS_URL=redis://localhost:6379

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:80

# Environment
FLASK_ENV=production
```

### Configuration Classes
- **DevelopmentConfig**: Debug mode, verbose logging
- **TestingConfig**: Test database, no CSRF
- **ProductionConfig**: Optimized for production
- **DockerConfig**: Docker-specific settings

## Development Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Set Environment Variables
```bash
export FLASK_ENV=development
export DATABASE_URL=mysql+pymysql://admin:123@Hrushi@3.249.132.231:3306/wa?charset=utf8mb4
export SECRET_KEY=your-secret-key
```

### 3. Initialize Database
```bash
flask init-db
flask seed-db
```

### 4. Run Development Server
```bash
python run.py
```

## Production Deployment

### Using Docker
```bash
# Build image
docker build -t auromart-backend .

# Run container
docker run -d \
  --name auromart-backend \
  -p 5000:5000 \
  -e DATABASE_URL=mysql+pymysql://admin:123@Hrushi@3.249.132.231:3306/wa \
  -e SECRET_KEY=your-secret-key \
  auromart-backend
```

### Using Gunicorn
```bash
gunicorn -w 4 -b 0.0.0.0:5000 wsgi:app
```

## CLI Commands

### Database Management
```bash
# Initialize database
flask init-db

# Seed with sample data
flask seed-db

# Reset database
flask reset-db
```

### User Management
```bash
# Create admin user
flask create-admin

# List all users
flask list-users
```

## API Documentation

### Authentication
All protected endpoints require a valid JWT token in the Authorization header:
```
Authorization: Bearer <your-jwt-token>
```

### Request/Response Format
All API endpoints return JSON responses:
```json
{
  "message": "Success message",
  "data": {...},
  "error": "Error message (if applicable)"
}
```

### Error Handling
Standard HTTP status codes:
- `200` - Success
- `201` - Created
- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found

## 🔄 MySQL Migration

This backend has been successfully migrated from PostgreSQL to MySQL with the following changes:

### Database Changes
- ✅ Updated connection strings to use MySQL format
- ✅ Modified database models for MySQL compatibility
- ✅ Updated initialization scripts for MySQL
- ✅ Changed UUID generation to use MySQL's UUID() function
- ✅ Updated timestamp fields with MySQL-specific options

### Configuration Updates
- ✅ Environment variables point to external MySQL server
- ✅ Added MySQL-specific engine options
- ✅ Updated connection parameters for better MySQL compatibility
- ✅ Added charset and sql_mode configurations

### Dependencies
- ✅ Replaced psycopg2-binary with PyMySQL
- ✅ Updated requirements.txt for MySQL support
- ✅ Added MySQL-specific connection options 