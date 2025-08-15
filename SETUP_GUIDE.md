# AuroMart B2B System Setup Guide

## 🚀 Quick Start (Recommended)

### Automated Setup
```bash
# Run the complete automated setup
python setup_complete_2x2_system.py
```

### Manual Setup (if automated fails)
```bash
# 1. Stop all containers and clean up
docker-compose -f docker-compose-local.yml down
docker volume rm auroconnect-b2b-app_mysql_data

# 2. Build and start containers
docker-compose -f docker-compose-local.yml up -d --build

# 3. Create test accounts
python reset_and_seed_2x2.py

# 4. Test the complete flow
python test_complete_flow.py
```

## 🔧 Troubleshooting

### If you encounter issues, run the fix script:
```bash
python fix_common_issues.py
```

### Common Issues and Solutions

#### 1. Port Already in Use
- **Error**: `Address already in use`
- **Solution**: Run `python fix_common_issues.py` to free ports

#### 2. Docker Not Running
- **Error**: `Cannot connect to the Docker daemon`
- **Solution**: Start Docker Desktop or Docker service

#### 3. Database Connection Issues
- **Error**: `Can't connect to MySQL server`
- **Solution**: Wait for MySQL to fully start (can take 30-60 seconds)

#### 4. Frontend Blank Page
- **Error**: White/blank page at localhost:3000
- **Solution**: Check browser console for errors, ensure backend is running

#### 5. Build Failures
- **Error**: `npm install` or `pip install` failures
- **Solution**: Run `python fix_common_issues.py` to clean caches

## 📋 System Requirements

### Minimum Requirements
- **Docker**: Version 20.10 or higher
- **Docker Compose**: Version 2.0 or higher
- **Python**: Version 3.8 or higher
- **Memory**: 4GB RAM minimum (8GB recommended)
- **Disk Space**: 5GB free space

### Recommended
- **Node.js**: Version 16 or higher (for local development)
- **Memory**: 8GB RAM
- **Disk Space**: 10GB free space

## 🏗️ Architecture

The system consists of:

### Backend (Flask)
- **Port**: 5000
- **Database**: MySQL 8.0
- **Cache**: Redis
- **Features**: REST API, JWT Authentication, File Uploads

### Frontend (React + TypeScript)
- **Port**: 3000
- **Framework**: React 18 + Vite
- **UI**: Radix UI + Tailwind CSS
- **Routing**: Wouter

### Database (MySQL)
- **Port**: 3306
- **Data**: Persistent volume storage
- **Initialization**: Automatic schema creation

### Cache (Redis)
- **Port**: 6379
- **Purpose**: Session storage, caching

## 👥 Test Accounts

After setup, you'll have these test accounts:

### Manufacturers
- **M1**: m1@auromart.com / password123
- **M2**: m2@auromart.com / password123

### Distributors
- **D1**: d1@auromart.com / password123
- **D2**: d2@auromart.com / password123

## 🔄 Complete Flow Test

The system tests this complete B2B flow:

1. **M1 (Manufacturer)** logs in
2. **M1** creates products and assigns to **D1**
3. **D1 (Distributor)** logs in
4. **D1** sees only assigned products
5. **D1** adds products to cart
6. **D1** places order
7. **M1** sees the order
8. **M1** approves/declines the order
9. Order status updates automatically

## 🛠️ Development Commands

### View Logs
```bash
# All services
docker-compose -f docker-compose-local.yml logs

# Specific service
docker-compose -f docker-compose-local.yml logs backend
docker-compose -f docker-compose-local.yml logs frontend
docker-compose -f docker-compose-local.yml logs mysql
```

### Restart Services
```bash
# Restart all
docker-compose -f docker-compose-local.yml restart

# Restart specific service
docker-compose -f docker-compose-local.yml restart backend
```

### Stop System
```bash
docker-compose -f docker-compose-local.yml down
```

### Reset Database
```bash
docker-compose -f docker-compose-local.yml down
docker volume rm auroconnect-b2b-app_mysql_data
docker-compose -f docker-compose-local.yml up -d
python reset_and_seed_2x2.py
```

## 🔍 Health Checks

### Backend Health
```bash
curl http://localhost:5000/api/health
```

### Frontend Health
```bash
curl http://localhost:3000/health
```

### Database Health
```bash
docker-compose -f docker-compose-local.yml exec mysql mysqladmin ping -h localhost -u admin -p123@Hrushi
```

## 📁 Project Structure

```
auroconnect-B2B-app/
├── client/                 # Frontend React app
├── server/                 # Backend Flask app
├── docker-compose-local.yml # Local development setup
├── setup_complete_2x2_system.py # Automated setup
├── fix_common_issues.py    # Issue fixing script
├── reset_and_seed_2x2.py   # Database seeding
└── test_complete_flow.py   # End-to-end testing
```

## 🆘 Getting Help

### If setup fails:
1. Run `python fix_common_issues.py`
2. Check the logs: `docker-compose -f docker-compose-local.yml logs`
3. Ensure Docker is running
4. Check system requirements
5. Try manual setup steps

### Common Error Messages:
- **"Connection refused"**: Service not started, check logs
- **"Permission denied"**: Docker not running or insufficient permissions
- **"Port already in use"**: Run fix script to free ports
- **"Build failed"**: Check internet connection and Docker resources

## 🎯 Success Indicators

Setup is successful when:
- ✅ Backend responds at http://localhost:5000/api/health
- ✅ Frontend loads at http://localhost:3000
- ✅ Test accounts are created
- ✅ Complete flow test passes
- ✅ No error messages in logs

## 🚀 Next Steps

After successful setup:
1. Open http://localhost:3000 in your browser
2. Login with test accounts
3. Explore the B2B features
4. Test the complete manufacturer-distributor flow
5. Check out the dashboard and reports

---

**Need help?** Check the logs and run the fix script first!
