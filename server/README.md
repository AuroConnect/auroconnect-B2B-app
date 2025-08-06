# AuroMart Flask Backend

A production-ready, modular Flask backend for the AuroMart B2B marketplace platform.

## Architecture

```
server/
├── app/
│   ├── __init__.py          # Application factory
│   ├── config.py            # Configuration management
│   ├── models/              # Database models
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── product.py
│   │   ├── category.py
│   │   ├── inventory.py
│   │   ├── order.py
│   │   ├── partnership.py
│   │   ├── favorite.py
│   │   └── search_history.py
│   ├── api/
│   │   └── v1/             # API version 1
│   │       ├── __init__.py
│   │       ├── auth.py
│   │       ├── partners.py
│   │       ├── products.py
│   │       ├── orders.py
│   │       ├── favorites.py
│   │       ├── partnerships.py
│   │       ├── search.py
│   │       └── health.py
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── decorators.py
│   │   └── validators.py
│   ├── errors.py            # Error handlers
│   └── cli.py              # CLI commands
├── run.py                   # Development server
├── wsgi.py                  # Production WSGI
├── requirements.txt
├── Dockerfile
└── README.md
```

## Features

### 🔐 **Authentication & Authorization**
- JWT-based authentication
- Role-based access control
- Password hashing with Werkzeug
- Token refresh mechanism

### 📊 **Database Models**
- **User**: Multi-role support (retailer, distributor, manufacturer)
- **Product**: Product catalog with categories
- **Inventory**: Distributor inventory management
- **Order**: Order processing with items
- **Partnership**: Business partnership management
- **Favorite**: User favorite partners
- **SearchHistory**: Search tracking

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
DATABASE_URL=postgresql://user:pass@localhost:5432/auromart

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
export DATABASE_URL=postgresql://auromart:auromart123@localhost:5432/auromart
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
  -e DATABASE_URL=postgresql://user:pass@host:5432/auromart \
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
- `409` - Conflict
- `500` - Internal Server Error

## Security Features

### Input Validation
- Marshmallow schemas for request validation
- SQL injection prevention with SQLAlchemy
- XSS protection with proper escaping

### Authentication
- JWT tokens with configurable expiration
- Password hashing with bcrypt
- Role-based access control

### CORS
- Configurable CORS origins
- Preflight request handling
- Secure headers

## Monitoring & Health Checks

### Health Check Endpoint
```bash
curl http://localhost:5000/api/health
```

### Docker Health Check
The Docker container includes a health check that verifies:
- Application is running
- Database connection is active
- API endpoints are responding

## Testing

### Unit Tests
```bash
# Run tests
python -m pytest tests/

# Run with coverage
python -m pytest --cov=app tests/
```

### API Tests
```bash
# Test API endpoints
python -m pytest tests/test_api/
```

## Logging

### Configuration
Logging is configured based on environment:
- **Development**: Debug level, console output
- **Production**: Warning level, structured logging

### Log Levels
- `DEBUG`: Detailed information
- `INFO`: General information
- `WARNING`: Warning messages
- `ERROR`: Error messages
- `CRITICAL`: Critical errors

## Performance

### Database Optimization
- Proper indexing on frequently queried fields
- Connection pooling with SQLAlchemy
- Query optimization with eager loading

### Caching
- Redis integration for session storage
- Query result caching
- Rate limiting with Redis

### Scalability
- Stateless application design
- Horizontal scaling support
- Load balancer ready

## Contributing

1. Follow PEP 8 style guidelines
2. Add tests for new features
3. Update documentation
4. Use conventional commit messages
5. Submit pull requests

## License

This project is licensed under the MIT License. 