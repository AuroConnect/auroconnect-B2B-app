# AuroMart B2B Platform

A comprehensive B2B platform connecting Manufacturers, Distributors, and Retailers with a complete end-to-end workflow.

## 🏗️ Architecture

### Roles & Workflow
- **Manufacturer**: Creates products, receives orders from distributors, manages inventory
- **Distributor**: Views manufacturer products, places orders, manages retailer relationships
- **Retailer**: Views distributor products, places orders, tracks deliveries

### Complete Workflow
1. Manufacturer adds products
2. Distributor places order to Manufacturer
3. Manufacturer accepts, packs, and ships
4. Distributor receives and manages inventory
5. Retailer places order to Distributor
6. Distributor fulfills and delivers to Retailer
7. Invoices generated at each stage

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- Docker & Docker Compose
- PostgreSQL

### 1. Clone and Setup
```bash
git clone <repository-url>
cd auroconnect-B2B-app
```

### 2. Start with Docker (Recommended)
```bash
# Start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f backend
```

### 3. Manual Setup

#### Backend Setup
```bash
cd server
pip install -r requirements.txt

# Set environment variables
export FLASK_APP=run.py
export FLASK_ENV=development

# Initialize database
python init_db_docker.py

# Start backend
python run.py
```

#### Frontend Setup
```bash
cd client
npm install
npm run dev
```

## 📋 API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login user
- `POST /api/auth/logout` - Logout user
- `GET /api/auth/user` - Get current user
- `GET /api/auth/dashboard` - Get dashboard URL

### Manufacturer Endpoints
- `GET /api/manufacturer/dashboard` - Manufacturer dashboard
- `GET /api/manufacturer/products` - Get manufacturer's products
- `POST /api/manufacturer/products` - Add new product
- `PUT /api/manufacturer/products/<id>` - Update product
- `DELETE /api/manufacturer/products/<id>` - Delete product
- `POST /api/manufacturer/products/upload` - Upload products via Excel
- `GET /api/manufacturer/orders` - Get manufacturer's orders
- `PUT /api/manufacturer/orders/<id>/status` - Update order status
- `GET /api/manufacturer/distributors` - Get manufacturer's distributors

### Distributor Endpoints
- `GET /api/distributor/dashboard` - Distributor dashboard
- `GET /api/distributor/products` - Get manufacturer's products
- `POST /api/distributor/orders` - Place order to manufacturer
- `GET /api/distributor/orders` - Get distributor's orders
- `PUT /api/distributor/orders/<id>/status` - Update order status
- `GET /api/distributor/retailers` - Get distributor's retailers
- `GET /api/distributor/manufacturer` - Get distributor's manufacturer

### Retailer Endpoints
- `GET /api/retailer/dashboard` - Retailer dashboard
- `GET /api/retailer/products` - Get distributor's products
- `POST /api/retailer/orders` - Place order to distributor
- `GET /api/retailer/orders` - Get retailer's orders
- `GET /api/retailer/orders/<id>` - Get specific order
- `PUT /api/retailer/orders/<id>/delivered` - Mark order as delivered
- `GET /api/retailer/distributor` - Get retailer's distributor
- `GET /api/retailer/reports/monthly` - Generate monthly report

### Invoice Endpoints
- `POST /api/invoices/generate/<order_id>` - Generate invoice
- `GET /api/invoices/<id>` - Get invoice details
- `GET /api/invoices/<id>/download` - Download invoice PDF
- `GET /api/invoices/order/<order_id>` - Get invoice for order

## 🔐 Authentication & Authorization

### User Roles
- **Manufacturer**: Can create products, manage orders from distributors
- **Distributor**: Can view manufacturer products, place orders, manage retailers
- **Retailer**: Can view distributor products, place orders, track deliveries

### Access Control
- Each role has specific dashboard and functionality
- Role-based API access control
- Partner-based visibility (manufacturers see only their distributors, etc.)

## 📊 Database Schema

### Core Tables
- `users` - User accounts with roles
- `products` - Product catalog with manufacturer ownership
- `partner_links` - Manufacturer-distributor and distributor-retailer relationships
- `orders` - Order management with buyer/seller relationships
- `invoices` - Invoice generation and management

### Key Relationships
- Products belong to manufacturers
- Orders have buyer and seller relationships
- Partner links define visibility and access control
- Invoices are linked to orders

## 🧪 Testing

### Run Complete Workflow Test
```bash
python test_complete_flow.py
```

This test verifies:
- User registration and authentication
- Product creation and management
- Order placement and status updates
- Invoice generation
- Monthly reporting

### Test Individual Components
```bash
# Test basic API functionality
python quick_test.py

# Test all endpoints
python test_endpoints.py

# Check backend health
python check_and_fix_backend.py
```

## 🚀 Deployment

### Production Setup
```bash
# Use production Docker Compose
docker-compose -f docker-compose.prod.yml up -d

# Set production environment variables
export FLASK_ENV=production
export DATABASE_URL=postgresql://user:pass@host:5432/db
```

### Environment Variables
```bash
# Backend
FLASK_ENV=development
DATABASE_URL=postgresql://auromart:auromart123@postgres:5432/auromart
SECRET_KEY=your-secret-key
CORS_ORIGINS=*

# Frontend
VITE_API_BASE_URL=http://localhost:5000/api
```

## 📁 Project Structure

```
auroconnect-B2B-app/
├── client/                 # React frontend
│   ├── src/
│   │   ├── pages/         # Page components
│   │   ├── hooks/         # Custom hooks
│   │   └── lib/           # Utilities
├── server/                 # Flask backend
│   ├── app/
│   │   ├── api/v1/        # API routes
│   │   ├── models/        # Database models
│   │   └── utils/         # Utilities
│   ├── requirements.txt    # Python dependencies
│   └── run.py             # Application entry point
├── docker-compose.yml      # Development setup
├── docker-compose.prod.yml # Production setup
└── README.md              # This file
```

## 🔧 Development

### Adding New Features
1. Update database models in `server/app/models/`
2. Create API routes in `server/app/api/v1/`
3. Update frontend components in `client/src/`
4. Add tests in test files
5. Update documentation

### Database Migrations
```bash
cd server
flask db migrate -m "Description of changes"
flask db upgrade
```

## 📞 Support

For issues and questions:
1. Check the test files for examples
2. Review the API documentation
3. Check Docker logs for errors
4. Verify database connectivity

## 🎯 Key Features

✅ **Complete B2B Workflow**: Manufacturer → Distributor → Retailer  
✅ **Role-Based Access Control**: Each role sees only relevant data  
✅ **Order Management**: Full order lifecycle with status tracking  
✅ **Invoice Generation**: PDF invoices with tax calculations  
✅ **Excel Upload**: Bulk product import functionality  
✅ **Monthly Reporting**: CSV reports for retailers  
✅ **Real-time Status Updates**: Order status tracking  
✅ **Partner Management**: Automatic partner visibility  
✅ **Dashboard Views**: Role-specific dashboards  

## 🚀 Getting Started with Testing

1. Start the backend: `docker-compose up -d`
2. Run the complete test: `python test_complete_flow.py`
3. Verify all 14 steps pass successfully
4. Check the frontend at `http://localhost:3000`

The platform is now ready for end-to-end B2B operations! 