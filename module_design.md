# AuroMart Module Design

## Overview
This document details the functional modules for the AuroMart B2B supply chain management system. Each module corresponds to a specific user role and contains the features and functionality required for that role.

## Authentication Module

### Features
1. **User Registration**
   - Role-based signup (Manufacturer, Distributor, Retailer)
   - Email validation
   - Password strength requirements
   - Company information collection

2. **User Login**
   - Secure authentication with email and password
   - Session management
   - Remember me functionality
   - Password reset workflow

3. **Role-based Access Control**
   - Dashboard routing based on user role
   - Permission validation for all actions
   - Session timeout and security

### API Endpoints
- POST /auth/register - User registration
- POST /auth/login - User login
- POST /auth/logout - User logout
- POST /auth/forgot-password - Password reset request
- POST /auth/reset-password - Password reset

## Manufacturer Module

### Features
1. **Product Management**
   - Create new products (name, description, category, price)
   - Edit existing products
   - Delete products
   - View product catalog
   - Search and filter products

2. **Inventory Assignment**
   - Assign products to specific distributors
   - Set quantity for each distributor
   - View inventory distribution
   - Update inventory assignments

3. **Order Tracking**
   - View all downstream orders
   - Filter orders by distributor
   - Filter orders by product
   - View order status and history

4. **Sales Reporting**
   - Region-wise sales reports
   - Product-wise sales reports
   - Time period filtering
   - Export reports to PDF/CSV

### API Endpoints
- GET /manufacturer/products - List all products
- POST /manufacturer/products - Create new product
- GET /manufacturer/products/<id> - Get product details
- PUT /manufacturer/products/<id> - Update product
- DELETE /manufacturer/products/<id> - Delete product
- POST /manufacturer/inventory/assign - Assign inventory to distributor
- GET /manufacturer/orders - List all orders
- GET /manufacturer/reports/sales - Generate sales report

## Distributor Module

### Features
1. **Inventory Management**
   - View assigned products with current stock
   - View reserved quantities
   - Low stock alerts
   - Inventory history

2. **Order Processing**
   - View incoming orders from retailers
   - Accept or reject orders
   - Select fulfillment type (Delivery/Pickup)
   - Update order status (Accepted, Packed, Dispatched, Delivered)

3. **Notification System**
   - WhatsApp-style alerts for new orders
   - Status update notifications
   - Invoice notifications

4. **Invoice Generation**
   - Auto-generate invoices upon delivery
   - View invoice details
   - Download invoices as PDF
   - Send invoices via WhatsApp simulation

5. **Reporting**
   - Monthly sales reports
   - Order history
   - Export reports to PDF/CSV

### API Endpoints
- GET /distributor/inventory - List assigned inventory
- GET /distributor/orders - List incoming orders
- GET /distributor/orders/<id> - Get order details
- POST /distributor/orders/<id>/accept - Accept order
- POST /distributor/orders/<id>/reject - Reject order
- PUT /distributor/orders/<id>/status - Update order status
- GET /distributor/invoices - List invoices
- GET /distributor/invoices/<id> - Get invoice details
- GET /distributor/reports/monthly - Generate monthly report

## Retailer Module

### Features
1. **Product Catalog**
   - Browse products from assigned distributor
   - Search and filter products
   - View product details
   - Check availability

2. **Order Management**
   - Add products to cart
   - Submit orders with quantity
   - View order history
   - Track order status in real-time

3. **Invoice Management**
   - View received invoices
   - Download invoices as PDF
   - View invoice details

4. **Notification System**
   - WhatsApp alerts for order status updates
   - Invoice notifications
   - Delivery notifications

5. **Reporting**
   - Monthly purchase reports
   - Download reports as PDF/CSV
   - View purchase history

### API Endpoints
- GET /retailer/catalog - Browse product catalog
- GET /retailer/catalog/<id> - Get product details
- POST /retailer/orders - Create new order
- GET /retailer/orders - List orders
- GET /retailer/orders/<id> - Get order details
- GET /retailer/invoices - List invoices
- GET /retailer/invoices/<id> - Get invoice details
- GET /retailer/reports/monthly - Generate monthly report

## Order Flow Module

### Features
1. **Order Lifecycle Management**
   - Status tracking from Pending to Delivered
   - Automatic status transitions
   - Manual status updates by distributors
   - Order history and audit trail

2. **Fulfillment Management**
   - Fulfillment type selection (Delivery/Pickup)
   - Tracking number assignment
   - Delivery confirmation

3. **Integration Points**
   - Inventory reservation on order placement
   - Inventory deduction on delivery
   - Invoice generation on delivery
   - Notification triggers at each stage

### Workflow
1. Retailer places order → Order status: Pending
2. Distributor receives notification → Can Accept/Reject
3. If accepted → Order status: Accepted
4. Distributor packs order → Order status: Packed
5. Distributor dispatches order → Order status: Dispatched
6. Order delivered → Order status: Delivered
7. Invoice auto-generated and sent to retailer

## Invoice Module

### Features
1. **Auto-generation**
   - Automatic creation upon order delivery
   - Calculation of subtotal, tax, and total
   - Unique invoice numbering

2. **Invoice Details**
   - Retailer information
   - Distributor information
   - Product details (name, quantity, price)
   - Subtotal, tax, and total amounts
   - Invoice date and due date

3. **Export and Delivery**
   - PDF generation using WeasyPrint
   - Download from dashboard
   - WhatsApp-style delivery simulation

### Data Structure
- Invoice number (unique)
- Order reference
- Parties information (retailer, distributor)
- Line items (product, quantity, price)
- Financial details (subtotal, tax, total)
- Dates (issued, due)

## Reporting Module

### Features
1. **Manufacturer Reports**
   - Sales by distributor
   - Sales by retailer
   - Sales by region
   - Sales by product
   - Time period filtering

2. **Distributor Reports**
   - Monthly sales summary
   - Order fulfillment statistics
   - Product performance
   - Customer analysis

3. **Retailer Reports**
   - Purchase history
   - Monthly spending summary
   - Product preferences
   - Supplier performance

4. **Export Options**
   - PDF format
   - CSV format
   - Custom date ranges
   - Filtered data sets

## Notification Module

### Features
1. **WhatsApp Simulation**
   - Console-based messaging system
   - Message templates for different events
   - User-specific message routing
   - Read status tracking

2. **Notification Types**
   - New order alerts (Distributor)
   - Order status updates (Retailer)
   - Invoice notifications (Retailer)
   - Low stock alerts (Distributor)

3. **Message Templates**
   - New order: "🛒 New order from Retailer XYZ. Please acknowledge."
   - Order accepted: "✅ Your order has been accepted by Distributor ABC."
   - Order ready: "📦 Your order is ready for [Delivery/Pickup]."
   - Invoice sent: "📄 Invoice #INV-XXXX has been generated."

### Implementation
- Flask routes for message handling
- In-memory storage for messages
- Timestamp tracking
- User-specific message queues

## Dashboard Module

### Features
1. **Manufacturer Dashboard**
   - Product catalog overview
   - Recent orders summary
   - Top selling products
   - Inventory distribution map
   - Quick actions (Add Product, Assign Inventory)

2. **Distributor Dashboard**
   - Inventory status
   - Pending orders
   - Recent notifications
   - Sales performance
   - Quick actions (Update Order Status, Generate Report)

3. **Retailer Dashboard**
   - Available products
   - Order status tracking
   - Recent invoices
   - Purchase history
   - Quick actions (Place Order, View Catalog)

### Components
- Summary cards with key metrics
- Charts for data visualization
- Recent activity feeds
- Quick action buttons
- Filter and search capabilities

## API Design

### Authentication
- POST /api/v1/auth/register
- POST /api/v1/auth/login
- POST /api/v1/auth/logout
- POST /api/v1/auth/refresh

### Manufacturer
- GET /api/v1/manufacturer/products
- POST /api/v1/manufacturer/products
- GET /api/v1/manufacturer/products/{id}
- PUT /api/v1/manufacturer/products/{id}
- DELETE /api/v1/manufacturer/products/{id}
- POST /api/v1/manufacturer/inventory/assign
- GET /api/v1/manufacturer/orders
- GET /api/v1/manufacturer/reports/sales

### Distributor
- GET /api/v1/distributor/inventory
- GET /api/v1/distributor/orders
- GET /api/v1/distributor/orders/{id}
- POST /api/v1/distributor/orders/{id}/accept
- POST /api/v1/distributor/orders/{id}/reject
- PUT /api/v1/distributor/orders/{id}/status
- GET /api/v1/distributor/invoices
- GET /api/v1/distributor/invoices/{id}
- GET /api/v1/distributor/reports/monthly

### Retailer
- GET /api/v1/retailer/catalog
- GET /api/v1/retailer/catalog/{id}
- POST /api/v1/retailer/orders
- GET /api/v1/retailer/orders
- GET /api/v1/retailer/orders/{id}
- GET /api/v1/retailer/invoices
- GET /api/v1/retailer/invoices/{id}
- GET /api/v1/retailer/reports/monthly

### Common
- GET /api/v1/notifications
- PUT /api/v1/notifications/{id}/read
- GET /api/v1/reports/export

## Security Considerations

### Authentication
- Password hashing with bcrypt
- JWT token authentication
- Session timeout
- CSRF protection

### Authorization
- Role-based access control
- Resource ownership validation
- Permission checks on all endpoints

### Data Protection
- Input validation and sanitization
- SQL injection prevention
- XSS protection
- Secure headers

## Error Handling

### HTTP Status Codes
- 200: Success
- 201: Created
- 400: Bad Request
- 401: Unauthorized
- 403: Forbidden
- 404: Not Found
- 500: Internal Server Error

### Error Response Format
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data",
    "details": [
      {
        "field": "email",
        "message": "Email is required"
      }
    ]
  }
}
```

This module design provides a comprehensive overview of the functionality for each user role in the AuroMart system, ensuring all requirements are met while maintaining a clean separation of concerns.