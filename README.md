# AuroMart B2B Platform

A comprehensive B2B platform for retailers, distributors, and manufacturers to streamline their operations.

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- MySQL (External server at 3.249.132.231)
- npm or yarn

### Database Setup
The application is configured to use an external MySQL server at `3.249.132.231` with the following credentials:
- **Host**: 3.249.132.231
- **Port**: 3306
- **Database**: wa
- **Username**: admin
- **Password**: 123@Hrushi

### Backend Setup
```bash
cd server
pip install -r requirements.txt
python reset_db.py  # Reset database to clean state
python run.py       # Start backend server
```

### Frontend Setup
```bash
cd client
npm install
npm run dev
```

### Quick Development Start

#### Option 1: Local Development
```bash
python start_dev.py  # Starts both frontend and backend
```

#### Option 2: Docker Compose (Recommended)
```bash
python start_docker.py  # Starts everything with Docker
```

Or manually:
```bash
docker-compose up -d --build
```

## 🔧 Fixed Issues

### Authentication System
- ✅ Fixed API URL configuration (port 5000)
- ✅ Fixed database schema issues
- ✅ Enhanced error handling and messages
- ✅ Improved CORS configuration
- ✅ Fixed user registration and login flows
- ✅ Added proper JWT token handling

### Backend Fixes
- ✅ Fixed User model UUID handling
- ✅ Enhanced auth endpoints with better error messages
- ✅ Added comprehensive logging
- ✅ Fixed database schema with password_hash column
- ✅ Improved CORS configuration for development

### Frontend Fixes
- ✅ Fixed API request configuration
- ✅ Enhanced error handling in forms
- ✅ Improved user authentication flow
- ✅ Fixed registration form validation
- ✅ Added better network error handling

## 🧪 Testing

### API Testing
```bash
cd server
python test_api.py
```

### Manual Testing
1. Start the backend: `cd server && python run.py`
2. Start the frontend: `cd client && npm run dev`
3. Visit http://localhost:3000
4. Test registration and login flows

## 📁 Project Structure

```
auroconnect-B2B-app/
├── client/                 # React frontend
│   ├── src/
│   │   ├── components/    # UI components
│   │   ├── hooks/        # Custom hooks
│   │   ├── pages/        # Page components
│   │   └── lib/          # Utilities
├── server/                # Flask backend
│   ├── app/
│   │   ├── api/          # API endpoints
│   │   ├── models/       # Database models
│   │   └── utils/        # Utilities
├── shared/               # Shared schemas
└── init.sql             # Database schema
```

## 🔐 Authentication Flow

1. **Registration**: Users can register as retailer, distributor, or manufacturer
2. **Login**: Email/password authentication with JWT tokens
3. **Authorization**: Role-based access control
4. **Session Management**: Automatic token refresh

## 🌐 API Endpoints

- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `GET /api/auth/user` - Get current user info
- `GET /api/health` - Health check

## 🛠️ Development

### Environment Variables
- `VITE_API_URL` - Frontend API URL (default: http://localhost:5000)
- `DATABASE_URL` - Backend database URL (default: mysql+pymysql://admin:123@Hrushi@3.249.132.231:3306/wa)
- `SECRET_KEY` - Flask secret key
- `JWT_SECRET_KEY` - JWT secret key

### MySQL Configuration
The application is configured to use an external MySQL server with the following settings:
```python
# Database configuration
MYSQL_HOST = '3.249.132.231'
MYSQL_PORT = '3306'
MYSQL_USER = 'admin'
MYSQL_PASSWORD = '123@Hrushi'
MYSQL_DATABASE = 'wa'

# Connection string
DATABASE_URL = f'mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}?charset=utf8mb4'
```

### Database Reset

#### Local Development
```bash
cd server
python reset_db.py
```

#### Docker Development
```bash
docker-compose down -v  # Remove volumes
docker-compose up -d --build  # Rebuild and start
```

## 🐛 Troubleshooting

### Common Issues
1. **Database Connection**: Ensure MySQL server at 3.249.132.231 is accessible and credentials are correct
2. **Port Conflicts**: Check if ports 3000 (frontend) and 5000 (backend) are available
3. **CORS Issues**: Backend CORS is configured for development (*)
4. **MySQL Connection**: Verify MySQL server is running and accessible from your network

### MySQL Connection Issues
If you encounter MySQL connection issues:
1. Verify the MySQL server is running at 3.249.132.231:3306
2. Check that the credentials (admin/123@Hrushi) are correct
3. Ensure your network allows connections to the MySQL port
4. Verify the database 'wa' exists or can be created

## 🔄 Migration from PostgreSQL to MySQL

This project has been successfully migrated from PostgreSQL to MySQL with the following changes:

### Backend Changes
- ✅ Updated `requirements.txt` to use PyMySQL instead of psycopg2
- ✅ Modified database configuration to use MySQL connection strings
- ✅ Updated database models to be MySQL compatible
- ✅ Changed database initialization scripts for MySQL
- ✅ Updated Docker configurations to use MySQL

### Frontend Changes
- ✅ Updated package.json to use mysql2 instead of PostgreSQL dependencies
- ✅ Modified shared schema to use MySQL-compatible Drizzle ORM
- ✅ Updated drizzle.config.ts for MySQL dialect

### Database Schema Changes
- ✅ Converted PostgreSQL-specific SQL to MySQL syntax
- ✅ Updated UUID generation to use MySQL's UUID() function
- ✅ Modified foreign key constraints for MySQL compatibility
- ✅ Updated timestamp fields to use MySQL's ON UPDATE CURRENT_TIMESTAMP

### Configuration Updates
- ✅ Environment variables now point to external MySQL server
- ✅ Database credentials updated to match Django settings
- ✅ Connection strings include MySQL-specific options
- ✅ Added MySQL-specific engine options for better compatibility 