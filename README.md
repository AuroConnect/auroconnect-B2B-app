# AuroMart - B2B Marketplace Platform

A production-ready B2B marketplace platform built with Flask backend and React frontend, featuring role-based access control, partner management, and order processing.

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose installed
- At least 4GB RAM available

### Running the Application

1. **Clone and navigate to the project:**
```bash
cd AuroMart
```

2. **Start all services:**
```bash
docker-compose up -d --build
```

3. **Access the application:**
- Frontend: http://localhost:80
- Backend API: http://localhost:5000
- Health Check: http://localhost:5000/api/health

4. **View logs:**
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend
```

## 🏗️ Architecture

### Services
- **Frontend**: React + TypeScript + Vite (Nginx)
- **Backend**: Flask + SQLAlchemy + JWT (Python)
- **Database**: PostgreSQL
- **Cache**: Redis (optional)

### Features
- ✅ **Multi-role Platform**: Retailers, Distributors, Manufacturers
- ✅ **Partner Management**: Browse by distributor/manufacturer
- ✅ **Favorites System**: Add partners to favorites
- ✅ **Role-based Visibility**: Secure access control
- ✅ **Global Search**: Search products and partners
- ✅ **Order Management**: Complete order workflow
- ✅ **JWT Authentication**: Secure API access
- ✅ **Docker Containerization**: Production-ready deployment

## 🔧 Development

### Backend (Flask)
```bash
cd server
pip install -r requirements.txt
python run.py
```

### Frontend (React)
```bash
cd client
npm install
npm run dev
```

## 📊 API Endpoints

### Authentication
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `GET /api/auth/user` - Get current user

### Partners
- `GET /api/partners/distributors` - Get distributors
- `GET /api/partners/manufacturers` - Get manufacturers
- `GET /api/partners/available` - Get available partners

### Favorites
- `GET /api/favorites` - Get user favorites
- `POST /api/favorites` - Add to favorites
- `DELETE /api/favorites/<id>` - Remove from favorites

### Products
- `GET /api/products` - Get products
- `GET /api/products/categories` - Get categories
- `GET /api/products/search` - Search products

### Orders
- `GET /api/orders` - Get user orders
- `POST /api/orders` - Create order
- `PATCH /api/orders/<id>/status` - Update order status

## 🐳 Docker Commands

```bash
# Start all services
docker-compose up -d

# Rebuild and start
docker-compose up -d --build

# Stop all services
docker-compose down

# View logs
docker-compose logs -f

# Access database
docker-compose exec postgres psql -U auromart -d auromart

# Access backend shell
docker-compose exec backend python

# Access frontend container
docker-compose exec frontend sh
```

## 🔍 Troubleshooting

### Common Issues

1. **Port conflicts**: Make sure ports 80 and 5000 are available
2. **Database connection**: Wait for PostgreSQL to be ready (health check)
3. **Build failures**: Clear Docker cache: `docker system prune -a`

### Health Checks
- Backend: http://localhost:5000/api/health
- Frontend: http://localhost:80/health
- Database: `docker-compose exec postgres pg_isready -U auromart`

### Logs
```bash
# Backend logs
docker-compose logs backend

# Frontend logs
docker-compose logs frontend

# Database logs
docker-compose logs postgres
```

## 📝 Environment Variables

### Backend (.env)
```env
FLASK_ENV=docker
DATABASE_URL=postgresql://auromart:auromart123@postgres:5432/auromart
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-key-here
```

### Frontend (.env)
```env
VITE_API_URL=http://localhost:5000
```

## 🚀 Production Deployment

For production deployment, consider:
- Using environment-specific Docker Compose files
- Setting up SSL/TLS certificates
- Configuring proper logging and monitoring
- Setting up database backups
- Using a reverse proxy (Nginx/Traefik)

## 📄 License

This project is licensed under the MIT License. 