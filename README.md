# AuroMart B2B Platform

A comprehensive B2B platform for retailers, distributors, and manufacturers to streamline their operations.

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- PostgreSQL
- npm or yarn

### Database Setup
1. Install PostgreSQL
2. Create a database user:
```sql
CREATE USER auromart WITH PASSWORD 'auromart123';
CREATE DATABASE auromart OWNER auromart;
```

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
```bash
python start_dev.py  # Starts both frontend and backend
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
- `DATABASE_URL` - Backend database URL
- `SECRET_KEY` - Flask secret key
- `JWT_SECRET_KEY` - JWT secret key

### Database Reset
```bash
cd server
python reset_db.py
```

## 🐛 Troubleshooting

### Common Issues
1. **Database Connection**: Ensure PostgreSQL is running and credentials are correct
2. **Port Conflicts**: Check if ports 3000 (frontend) and 5000 (backend) are available
3. **CORS Issues**: Backend CORS is configured for development (*)
4. **API Errors**: Check browser console and server logs for detailed error messages

### Logs
- Backend logs: Check server console output
- Frontend logs: Check browser developer tools console
- Network errors: Check browser Network tab

## 📝 Recent Fixes

### Authentication Issues Fixed
- Fixed API URL mismatch (5001 → 5000)
- Enhanced error handling in registration/login
- Fixed database schema issues
- Improved CORS configuration
- Added comprehensive logging
- Fixed UUID handling in User model

### UI/UX Improvements
- Better error messages for users
- Improved form validation
- Enhanced network error handling
- Fixed callback patterns in auth hooks

## 🚀 Deployment

### Backend Deployment
```bash
cd server
pip install -r requirements.txt
gunicorn -w 4 -b 0.0.0.0:5000 run:app
```

### Frontend Deployment
```bash
cd client
npm run build
# Serve dist/ directory
```

## 📞 Support

For issues or questions:
1. Check the troubleshooting section
2. Review server logs for backend issues
3. Check browser console for frontend issues
4. Test API endpoints directly with curl/Postman 