# AuroMart Setup with EC2 MySQL Database

This setup uses your external MySQL database on EC2 instead of Docker containers.

## 🗄️ Database Configuration
- **Host**: 3.249.132.231:3306
- **Database**: wa
- **User**: admin
- **Password**: 123@Hrushi

## 🚀 Quick Start

### 1. Install Dependencies

#### Backend Dependencies
```bash
cd server
pip install -r requirements.txt
```

#### Frontend Dependencies
```bash
cd client
npm install
```

### 2. Start Backend (Flask)
```bash
# From the root directory
python start_backend.py
```

This will:
- Connect to your EC2 MySQL database
- Create all tables automatically
- Add sample users
- Start Flask server on http://localhost:5000

### 3. Start Frontend (React)
```bash
# From the root directory (in a new terminal)
python start_frontend.py
```

This will:
- Start React development server
- Available on http://localhost:3000

## 📋 Sample Users
- `retailer@example.com` (password: password123)
- `distributor@example.com` (password: password123)
- `manufacturer@example.com` (password: password123)

## 🔗 URLs
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:5000
- **Health Check**: http://localhost:5000/api/health

## 🛠️ Alternative: Using Docker for Frontend Only

If you want to use Docker for the frontend:

```bash
# Start only frontend and Redis with Docker
docker-compose up frontend redis -d

# Start backend separately
python start_backend.py
```

## 🔧 Troubleshooting

### Database Connection Issues
1. Make sure your EC2 MySQL server allows connections from your IP
2. Check if the `wa` database exists
3. Verify the `admin` user has proper permissions

### Backend Issues
1. Make sure all Python dependencies are installed
2. Check if port 5000 is available
3. Verify the MySQL connection string

### Frontend Issues
1. Make sure Node.js and npm are installed
2. Check if port 3000 is available
3. Verify the API URL in the frontend configuration

## 📊 Benefits of This Setup
- ✅ No Docker container for backend (simpler)
- ✅ Direct connection to your EC2 MySQL database
- ✅ Faster development and debugging
- ✅ Easy to modify and test
- ✅ Uses your existing MySQL infrastructure
