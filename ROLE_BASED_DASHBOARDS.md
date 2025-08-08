# 🔐 Role-Based Dashboard System

This document describes the implementation of the role-based access control system with dedicated dashboards for each user role in the AuroMart B2B platform.

## 🎯 Overview

The system provides three distinct dashboards based on user roles:

- **Manufacturer Dashboard** (`/manufacturer/dashboard`)
- **Distributor Dashboard** (`/distributor/dashboard`) 
- **Retailer Dashboard** (`/retailer/dashboard`)

## 🏭 Manufacturer Features

### Dashboard Access
- **URL**: `/manufacturer/dashboard`
- **Access**: Only users with `role = 'manufacturer'`
- **Redirect**: Automatic redirect from `/` to `/manufacturer/dashboard`

### Features Available
- ✅ **Product Management**: Add, edit, delete products
- ✅ **Distributor Connections**: View connected distributors
- ✅ **Order Management**: Accept/reject orders from distributors
- ✅ **Invoice Generation**: Generate PDF invoices for shipped orders
- ✅ **Bulk Upload**: Upload products via Excel files
- ✅ **Analytics**: View product stats and order metrics

### API Endpoints
- `GET /api/v1/analytics/manufacturer-stats` - Dashboard statistics
- `GET /api/v1/orders/manufacturer-recent` - Recent orders from distributors
- `GET /api/v1/partners/distributors` - Connected distributors
- `GET /api/v1/products/` - Manufacturer's products (filtered by created_by)

## 🚚 Distributor Features

### Dashboard Access
- **URL**: `/distributor/dashboard`
- **Access**: Only users with `role = 'distributor'`
- **Redirect**: Automatic redirect from `/` to `/distributor/dashboard`

### Features Available
- ✅ **Manufacturer Products**: View products from connected manufacturer
- ✅ **Retailer Management**: View connected retailers
- ✅ **Order Fulfillment**: Accept/reject orders from retailers
- ✅ **Order Placement**: Place orders to manufacturer
- ✅ **Invoice Generation**: Generate invoices for retailers
- ✅ **Sales Reports**: Monthly sales analytics

### API Endpoints
- `GET /api/v1/analytics/distributor-stats` - Dashboard statistics
- `GET /api/v1/orders/retailer-incoming` - Incoming orders from retailers
- `GET /api/v1/partners/retailers` - Connected retailers
- `GET /api/v1/products/manufacturer` - Products from manufacturer

## 🛍️ Retailer Features

### Dashboard Access
- **URL**: `/retailer/dashboard`
- **Access**: Only users with `role = 'retailer'`
- **Redirect**: Automatic redirect from `/` to `/retailer/dashboard`

### Features Available
- ✅ **Product Catalog**: View products from distributor
- ✅ **Order Placement**: Place orders to distributor
- ✅ **Order Tracking**: Track order status
- ✅ **Invoice Access**: Download invoices
- ✅ **WhatsApp Notifications**: Simulated notifications
- ✅ **Reports**: Download monthly reports

### API Endpoints
- `GET /api/v1/analytics/retailer-stats` - Dashboard statistics
- `GET /api/v1/orders/my-orders` - Retailer's orders
- `GET /api/v1/products/distributor` - Products from distributor
- `GET /api/v1/invoices/my-invoices` - Retailer's invoices

## 🔄 Order Workflow

### Manufacturer → Distributor
1. Manufacturer adds products
2. Distributor places order to manufacturer
3. Manufacturer accepts/rejects order
4. Manufacturer fulfills and generates invoice
5. Distributor receives products

### Distributor → Retailer
1. Retailer places order to distributor
2. Distributor accepts/rejects order
3. Distributor fulfills using inventory
4. Distributor generates invoice
5. Retailer receives products and invoice

## 🏗️ Technical Implementation

### Frontend Structure
```
client/src/pages/
├── manufacturer/
│   └── dashboard.tsx          # Manufacturer dashboard
├── distributor/
│   └── dashboard.tsx          # Distributor dashboard
├── retailer/
│   └── dashboard.tsx          # Retailer dashboard
└── dashboard.tsx              # General dashboard (redirects)
```

### Backend API Structure
```
server/app/api/v1/
├── analytics.py               # Role-specific stats
├── orders.py                  # Role-specific orders
├── partners.py                # Role-specific partners
├── products.py                # Role-specific products
└── invoices.py                # Role-specific invoices
```

### Authentication Flow
1. User logs in with email/password
2. System checks user role
3. Automatic redirect to role-specific dashboard
4. Dashboard shows role-appropriate data and features

### Access Control
- **Role-based routing**: Users can only access their role's dashboard
- **API protection**: Backend endpoints check user role before returning data
- **Data filtering**: Each role sees only relevant data based on partnerships

## 🧪 Testing

### Test Users
```python
# Manufacturer
email: "hrushikesh@auromart.com"
password: "password123"

# Distributor  
email: "distributor1@test.com"
password: "password123"

# Retailer
email: "retailer1@test.com"
password: "password123"
```

### Test Script
Run the test script to verify all role-based features:
```bash
python test_role_based_dashboards.py
```

## 🚀 Getting Started

### 1. Start the Backend
```bash
cd server
python run.py
```

### 2. Start the Frontend
```bash
cd client
npm run dev
```

### 3. Access Dashboards
- **Manufacturer**: http://localhost:5173/manufacturer/dashboard
- **Distributor**: http://localhost:5173/distributor/dashboard
- **Retailer**: http://localhost:5173/retailer/dashboard

### 4. Login Flow
1. Go to http://localhost:5173
2. Login with test credentials
3. Automatic redirect to role-specific dashboard

## 📊 Dashboard Features

### Manufacturer Dashboard
- **Stats Cards**: Total products, connected distributors, pending orders, invoices generated
- **Recent Orders**: Orders from distributors with accept/reject actions
- **Connected Distributors**: List of active distributor partnerships
- **Quick Actions**: Add product, bulk upload, manage distributors, view orders

### Distributor Dashboard
- **Stats Cards**: Available products, connected retailers, pending orders, monthly sales
- **Recent Orders**: Incoming orders from retailers with accept/reject actions
- **Connected Retailers**: List of active retailer partnerships
- **Quick Actions**: Place order to manufacturer, manage retailers, view orders, generate reports

### Retailer Dashboard
- **Stats Cards**: Available products, my orders, pending orders, invoices
- **My Orders**: Personal order history with tracking
- **Recent Invoices**: Downloadable invoices with download buttons
- **Quick Actions**: Place new order, browse products, track orders, download reports

## 🔐 Security Features

### Role-Based Access Control
- ✅ **Frontend Protection**: Role-specific route guards
- ✅ **Backend Protection**: API endpoint role validation
- ✅ **Data Isolation**: Users only see their relevant data
- ✅ **Authentication**: JWT-based authentication required

### Data Privacy
- ✅ **Partnership-based filtering**: Users only see data from their partners
- ✅ **Order isolation**: Users only see orders they're involved in
- ✅ **Product filtering**: Users only see products from their supply chain

## 🎨 UI/UX Features

### Consistent Design
- ✅ **Modern UI**: Clean, professional design
- ✅ **Responsive**: Works on desktop and mobile
- ✅ **Loading States**: Proper loading indicators
- ✅ **Error Handling**: User-friendly error messages

### Role-Specific Branding
- ✅ **Manufacturer**: Blue theme with factory icons
- ✅ **Distributor**: Green theme with truck icons  
- ✅ **Retailer**: Purple theme with store icons

## 🔄 Future Enhancements

### Planned Features
- [ ] **Real-time notifications** via WebSocket
- [ ] **Advanced analytics** with charts and graphs
- [ ] **Bulk operations** for orders and products
- [ ] **Export functionality** for reports
- [ ] **Mobile app** for field operations

### Integration Features
- [ ] **WhatsApp Business API** integration
- [ ] **Payment gateway** integration
- [ ] **Inventory management** system
- [ ] **Shipping integration** with logistics providers

## 📝 API Documentation

### Authentication
All API endpoints require JWT authentication:
```
Authorization: Bearer <token>
```

### Common Response Format
```json
{
  "message": "Success message",
  "data": {
    // Response data
  }
}
```

### Error Response Format
```json
{
  "message": "Error message",
  "error": "Detailed error information"
}
```

## 🤝 Contributing

When adding new features:

1. **Follow role-based patterns**: Ensure new features respect role boundaries
2. **Add proper validation**: Include role checks in new endpoints
3. **Update documentation**: Keep this document current
4. **Add tests**: Include role-specific test cases

## 📞 Support

For issues or questions:
- Check the test script for API verification
- Review the role-based routing logic
- Verify partnership relationships in the database
- Test with different user roles to ensure proper isolation
