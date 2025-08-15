# AuroMart Development Setup

## 🚀 Hot Reload Development Environment

This setup provides automatic hot reloading for both frontend and backend, so you don't need to clear browser cache or restart containers for every change!

## Quick Start

### Option 1: Using Scripts (Recommended)
```bash
# Windows Batch
dev-start.bat

# PowerShell
.\dev-start.ps1
```

### Option 2: Manual Commands
```bash
# Stop existing containers
docker-compose -f docker-compose.dev.yml down

# Build with no cache
docker-compose -f docker-compose.dev.yml build --no-cache

# Start development environment
docker-compose -f docker-compose.dev.yml up -d
```

## 🔥 Features

### Frontend (React + Vite)
- ✅ **Hot Module Replacement (HMR)**: Changes reflect instantly
- ✅ **No Cache Issues**: Automatic cache busting
- ✅ **Live Reload**: Browser updates automatically
- ✅ **Source Maps**: Better debugging experience

### Backend (Flask)
- ✅ **Auto Restart**: Flask restarts on code changes
- ✅ **Debug Mode**: Detailed error messages
- ✅ **Live Reload**: No manual restart needed

### Database
- ✅ **EC2 MySQL**: Using your remote database
- ✅ **Persistent Data**: No data loss on restarts

## 📁 File Structure
```
├── docker-compose.dev.yml    # Development configuration
├── server/Dockerfile.dev     # Backend development container
├── client/Dockerfile.dev     # Frontend development container
├── dev-start.bat            # Windows startup script
├── dev-start.ps1            # PowerShell startup script
└── DEVELOPMENT.md           # This file
```

## 🌐 Access Points
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:5000
- **Test Accounts**: 
  - Manufacturer: `m@demo.com` / `Demo@123`
  - Distributor: `d@demo.com` / `Demo@123`
  - Retailer: `r@demo.com` / `Demo@123`

## 🔧 How It Works

### Volume Mounting
- `./server:/app` - Backend code is mounted live
- `./client:/app` - Frontend code is mounted live
- Changes to your local files immediately reflect in containers

### Hot Reload
- **Frontend**: Vite HMR automatically updates browser
- **Backend**: Flask debug mode restarts on file changes
- **No Cache**: Development mode bypasses all caching

## 🛠️ Making Changes

### Frontend Changes
1. Edit any file in `client/src/`
2. Save the file
3. Changes appear instantly in browser (no refresh needed!)

### Backend Changes
1. Edit any file in `server/`
2. Save the file
3. Flask automatically restarts and loads changes

### Database Changes
- All data is stored in your EC2 MySQL server
- No local database to worry about
- Data persists across container restarts

## 🚨 Troubleshooting

### If changes don't reflect:
1. Check container logs: `docker logs auroconnect-b2b-app-frontend-1`
2. Restart development environment: `.\dev-start.ps1`
3. Clear browser cache (shouldn't be needed anymore)

### If containers won't start:
1. Check if ports 3000 and 5000 are free
2. Stop any existing containers: `docker-compose down`
3. Rebuild: `docker-compose -f docker-compose.dev.yml build --no-cache`

## 🎯 Benefits

✅ **No More Cache Clearing**: Changes reflect automatically  
✅ **Faster Development**: No waiting for rebuilds  
✅ **Better Debugging**: Source maps and live reload  
✅ **Consistent Environment**: Same setup for all developers  
✅ **EC2 Database**: Production-like data environment  

## 📝 Notes

- This is for **development only**
- Use `docker-compose.yml` for production builds
- All changes are live and immediate
- Database uses your EC2 server (3.249.132.231:3306)

Happy coding! 🎉
