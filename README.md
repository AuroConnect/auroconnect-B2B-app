# AuroMart - B2B Trade Partner Platform

A production-ready, role-based web application for a 3-tier B2B flow: **Manufacturer → Distributor → Retailer**.

## 🚀 Features

### Core Functionality
- **Authentication & Role Management**: Secure login/signup with role-based access
- **Product Management**: CRUD operations, bulk Excel upload, inventory tracking
- **Partner Management**: Link manufacturers with distributors, distributors with retailers
- **Order Management**: Complete order lifecycle (pending → accepted → shipped → delivered)
- **Cart System**: Add products, manage quantities, place orders
- **Pricing Rules**: Custom pricing per distributor, volume discounts
- **Invoice Generation**: PDF invoices for orders
- **Reports & Analytics**: Sales reports, export to PDF/CSV
- **Notifications**: Real-time in-app notifications
- **Business Settings**: Profile management, addresses, preferences

### Role-Based Access
- **Manufacturer**: Manage products, view distributor orders, set pricing
- **Distributor**: Browse manufacturer catalog, manage retailer orders
- **Retailer**: Browse distributor catalog, place orders, track deliveries

## 🛠 Tech Stack

### Backend
- **Framework**: Flask (Python)
- **Database**: MySQL
- **ORM**: SQLAlchemy
- **Authentication**: JWT (Flask-JWT-Extended)
- **File Processing**: Pandas (Excel upload)
- **PDF Generation**: ReportLab

### Frontend
- **Framework**: React 18 with TypeScript
- **Styling**: Tailwind CSS
- **State Management**: React Query (TanStack Query)
- **Routing**: Wouter
- **HTTP Client**: Axios
- **UI Components**: Custom components with Lucide icons

### Infrastructure
- **Containerization**: Docker & Docker Compose
- **Database**: MySQL (EC2 instance)
- **Production**: Optimized for deployment

## 📋 Prerequisites

- Docker & Docker Compose
- Node.js 18+ (for development)
- Python 3.9+ (for development)
- MySQL database (production)

## 🚀 Quick Start

### Production Deployment

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd auroconnect-B2B-app
   ```

2. **Configure environment variables**
   ```bash
   # Update database connection in docker-compose.prod.yml
   DATABASE_URL=mysql+pymysql://username:password@your-mysql-host:3306/database_name
   ```

3. **Build and run production containers**
   ```bash
   docker-compose -f docker-compose.prod.yml build --no-cache
   docker-compose -f docker-compose.prod.yml up -d
   ```

4. **Create demo users**
   ```bash
   python create_demo_users.py
   ```

5. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:5000

### Development Setup

1. **Start development environment**
   ```bash
   docker-compose up -d
   ```

2. **Install frontend dependencies** (if developing locally)
   ```bash
   cd client
   npm install
   npm run dev
   ```

3. **Install backend dependencies** (if developing locally)
   ```bash
   cd server
   pip install -r requirements.txt
   python run.py
   ```

## 👥 Demo Users

The application comes with pre-configured demo users for testing:

| Role | Email | Password | Business Name |
|------|-------|----------|---------------|
| Manufacturer | m@demo.com | Demo@123 | Auro Manufacturer |
| Distributor | d@demo.com | Demo@123 | Auro Distributor |
| Retailer | r@demo.com | Demo@123 | Auro Retailer |

## 🔄 Key Workflows

### 1. Product Management (Manufacturer)
1. Login as manufacturer (m@demo.com)
2. Navigate to Products page
3. Add new products or bulk upload via Excel
4. Set pricing rules for distributors

### 2. Order Placement (Retailer → Distributor)
1. Login as retailer (r@demo.com)
2. Browse catalog in Products page
3. Add items to cart
4. Place order with delivery details

### 3. Order Processing (Distributor)
1. Login as distributor (d@demo.com)
2. View incoming orders in Orders page
3. Accept/reject orders
4. Update status (packed → shipped → delivered)

### 4. Partner Management
1. Manufacturers can link with distributors
2. Distributors can link with retailers
3. Each role sees only their linked partners' data

## 📊 Database Schema

### Core Tables
- `users` - User accounts with role-based access
- `products` - Product catalog with inventory
- `orders` - Order management with status tracking
- `order_items` - Individual items in orders
- `partner_links` - Manufacturer-Distributor relationships
- `distributor_retailer_links` - Distributor-Retailer relationships
- `pricing_rules` - Custom pricing configurations
- `notifications` - In-app notification system

## 🔒 Security Features

- **JWT Authentication**: Secure token-based authentication
- **Role-Based Access Control**: Strict data visibility rules
- **Input Validation**: Server-side validation for all inputs
- **SQL Injection Protection**: Parameterized queries via SQLAlchemy
- **CORS Configuration**: Controlled cross-origin requests
- **Password Hashing**: Secure password storage with Werkzeug

## 📱 Responsive Design

- Mobile-first responsive design
- Optimized for all screen sizes
- Touch-friendly interface
- Progressive Web App features

## 🚀 Production Deployment

### Environment Variables
```bash
# Database
DATABASE_URL=mysql+pymysql://user:pass@host:3306/db

# Security
JWT_SECRET_KEY=your-super-secret-key
SECRET_KEY=your-app-secret-key

# CORS
CORS_ORIGINS=http://localhost:3000,https://yourdomain.com

# Flask
FLASK_ENV=production
```

### Docker Production Commands
```bash
# Build production images
docker-compose -f docker-compose.prod.yml build --no-cache

# Start production services
docker-compose -f docker-compose.prod.yml up -d

# View logs
docker-compose -f docker-compose.prod.yml logs -f

# Stop services
docker-compose -f docker-compose.prod.yml down
```

## 🧪 Testing

### API Testing
```bash
# Test authentication
python test_auth.py

# Test demo user login
python test_demo_login.py

# Create demo users
python create_demo_users.py
```

### Manual Testing Checklist
- [ ] All roles can sign up and login
- [ ] Product CRUD operations work
- [ ] Cart functionality works
- [ ] Order placement and processing
- [ ] Partner linking works
- [ ] Reports generation
- [ ] Invoice generation
- [ ] Notifications work

## 📈 Performance Optimizations

- **Database Indexing**: Optimized queries with proper indexes
- **Caching**: React Query for frontend caching
- **Lazy Loading**: Components loaded on demand
- **Image Optimization**: Compressed product images
- **Bundle Optimization**: Minified production builds

## 🐛 Troubleshooting

### Common Issues

1. **Database Connection Failed**
   - Check MySQL server is running
   - Verify connection string in docker-compose.yml
   - Ensure database exists

2. **Authentication Errors**
   - Clear browser cache and cookies
   - Check JWT secret key configuration
   - Verify user exists in database

3. **Frontend Build Issues**
   - Clear node_modules and reinstall
   - Check Node.js version compatibility
   - Verify environment variables

### Logs
```bash
# Backend logs
docker logs auromart-backend-prod

# Frontend logs
docker logs auromart-frontend-prod

# All services
docker-compose -f docker-compose.prod.yml logs -f
```

## 📞 Support

For technical support or feature requests:
- Create an issue in the repository
- Contact the development team
- Check the troubleshooting section above

## 📄 License

This project is proprietary software. All rights reserved.

---

**AuroMart B2B Platform** - Streamlining B2B trade relationships with modern technology. 