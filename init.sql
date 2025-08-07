-- Initialize AuroMart Database

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create tables
CREATE TABLE IF NOT EXISTS users (
    id VARCHAR(36) PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    first_name VARCHAR(255) NOT NULL,
    last_name VARCHAR(255) NOT NULL,
    profile_image_url VARCHAR(500),
    role VARCHAR(50) NOT NULL DEFAULT 'retailer',
    business_name TEXT,
    address TEXT,
    phone_number VARCHAR(50),
    whatsapp_number VARCHAR(50),
    password_hash VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS categories (
    id VARCHAR(36) PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS products (
    id VARCHAR(36) PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    sku VARCHAR(255) UNIQUE NOT NULL,
    category_id VARCHAR(36) REFERENCES categories(id),
    manufacturer_id VARCHAR(36) REFERENCES users(id),
    image_url TEXT,
    base_price DECIMAL(10,2),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS inventory (
    id VARCHAR(36) PRIMARY KEY DEFAULT gen_random_uuid(),
    distributor_id VARCHAR(36) REFERENCES users(id) NOT NULL,
    product_id VARCHAR(36) REFERENCES products(id) NOT NULL,
    quantity INTEGER NOT NULL DEFAULT 0,
    selling_price DECIMAL(10,2),
    is_available BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Updated orders table with new structure
CREATE TABLE IF NOT EXISTS orders (
    id VARCHAR(36) PRIMARY KEY DEFAULT gen_random_uuid(),
    order_type VARCHAR(50) NOT NULL, -- 'manufacturer_distributor' or 'distributor_retailer'
    manufacturer_id VARCHAR(36) REFERENCES users(id),
    distributor_id VARCHAR(36) REFERENCES users(id),
    retailer_id VARCHAR(36) REFERENCES users(id),
    order_number VARCHAR(50) UNIQUE NOT NULL,
    total_amount DECIMAL(10,2) NOT NULL,
    tax_amount DECIMAL(10,2) DEFAULT 0,
    shipping_amount DECIMAL(10,2) DEFAULT 0,
    status VARCHAR(20) DEFAULT 'pending', -- pending, accepted, processing, shipped, delivered, cancelled
    delivery_address TEXT,
    delivery_method VARCHAR(50), -- 'delivery', 'pickup'
    expected_delivery_date TIMESTAMP,
    actual_delivery_date TIMESTAMP,
    notes TEXT,
    tracking_number VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS order_items (
    id VARCHAR(36) PRIMARY KEY DEFAULT gen_random_uuid(),
    order_id VARCHAR(36) REFERENCES orders(id) NOT NULL,
    product_id VARCHAR(36) REFERENCES products(id) NOT NULL,
    quantity INTEGER NOT NULL,
    unit_price DECIMAL(10,2) NOT NULL,
    total_price DECIMAL(10,2) NOT NULL,
    product_name VARCHAR(200) NOT NULL,
    product_sku VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Updated partnerships table with new structure
CREATE TABLE IF NOT EXISTS partnerships (
    id VARCHAR(36) PRIMARY KEY DEFAULT gen_random_uuid(),
    partnership_type VARCHAR(50) NOT NULL, -- 'manufacturer_distributor' or 'distributor_retailer'
    manufacturer_id VARCHAR(36) REFERENCES users(id),
    distributor_id VARCHAR(36) REFERENCES users(id),
    retailer_id VARCHAR(36) REFERENCES users(id),
    status VARCHAR(20) DEFAULT 'active', -- active, inactive, pending
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- New invoices table
CREATE TABLE IF NOT EXISTS invoices (
    id VARCHAR(36) PRIMARY KEY DEFAULT gen_random_uuid(),
    invoice_type VARCHAR(50) NOT NULL, -- 'manufacturer_distributor' or 'distributor_retailer'
    manufacturer_id VARCHAR(36) REFERENCES users(id),
    distributor_id VARCHAR(36) REFERENCES users(id),
    retailer_id VARCHAR(36) REFERENCES users(id),
    invoice_number VARCHAR(50) UNIQUE NOT NULL,
    order_id VARCHAR(36) REFERENCES orders(id) NOT NULL,
    subtotal DECIMAL(10,2) NOT NULL,
    tax_amount DECIMAL(10,2) DEFAULT 0,
    shipping_amount DECIMAL(10,2) DEFAULT 0,
    total_amount DECIMAL(10,2) NOT NULL,
    status VARCHAR(20) DEFAULT 'pending', -- pending, paid, overdue, cancelled
    payment_method VARCHAR(50),
    payment_date TIMESTAMP,
    due_date TIMESTAMP,
    notes TEXT,
    terms_conditions TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS invoice_items (
    id VARCHAR(36) PRIMARY KEY DEFAULT gen_random_uuid(),
    invoice_id VARCHAR(36) REFERENCES invoices(id) NOT NULL,
    product_id VARCHAR(36) REFERENCES products(id) NOT NULL,
    quantity INTEGER NOT NULL,
    unit_price DECIMAL(10,2) NOT NULL,
    total_price DECIMAL(10,2) NOT NULL,
    product_name VARCHAR(200) NOT NULL,
    product_sku VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS favorites (
    id VARCHAR(36) PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id VARCHAR(36) REFERENCES users(id) NOT NULL,
    favorite_user_id VARCHAR(36) REFERENCES users(id) NOT NULL,
    favorite_type VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS search_history (
    id VARCHAR(36) PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id VARCHAR(36) REFERENCES users(id) NOT NULL,
    search_term VARCHAR(255) NOT NULL,
    search_type VARCHAR(50) NOT NULL,
    result_count INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS whatsapp_notifications (
    id VARCHAR(36) PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id VARCHAR(36) REFERENCES users(id) NOT NULL,
    message TEXT NOT NULL,
    type VARCHAR(50) NOT NULL, -- order_update, invoice_sent, etc.
    sent_at TIMESTAMP,
    is_delivered BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);
CREATE INDEX IF NOT EXISTS idx_products_category ON products(category_id);
CREATE INDEX IF NOT EXISTS idx_products_manufacturer ON products(manufacturer_id);
CREATE INDEX IF NOT EXISTS idx_inventory_distributor ON inventory(distributor_id);
CREATE INDEX IF NOT EXISTS idx_inventory_product ON inventory(product_id);
CREATE INDEX IF NOT EXISTS idx_orders_manufacturer ON orders(manufacturer_id);
CREATE INDEX IF NOT EXISTS idx_orders_distributor ON orders(distributor_id);
CREATE INDEX IF NOT EXISTS idx_orders_retailer ON orders(retailer_id);
CREATE INDEX IF NOT EXISTS idx_orders_type ON orders(order_type);
CREATE INDEX IF NOT EXISTS idx_partnerships_manufacturer ON partnerships(manufacturer_id);
CREATE INDEX IF NOT EXISTS idx_partnerships_distributor ON partnerships(distributor_id);
CREATE INDEX IF NOT EXISTS idx_partnerships_retailer ON partnerships(retailer_id);
CREATE INDEX IF NOT EXISTS idx_partnerships_type ON partnerships(partnership_type);
CREATE INDEX IF NOT EXISTS idx_invoices_manufacturer ON invoices(manufacturer_id);
CREATE INDEX IF NOT EXISTS idx_invoices_distributor ON invoices(distributor_id);
CREATE INDEX IF NOT EXISTS idx_invoices_retailer ON invoices(retailer_id);
CREATE INDEX IF NOT EXISTS idx_invoices_type ON invoices(invoice_type);
CREATE INDEX IF NOT EXISTS idx_favorites_user ON favorites(user_id);
CREATE INDEX IF NOT EXISTS idx_favorites_favorite_user ON favorites(favorite_user_id);
CREATE INDEX IF NOT EXISTS idx_search_history_user ON search_history(user_id);
CREATE INDEX IF NOT EXISTS idx_whatsapp_notifications_user ON whatsapp_notifications(user_id);

-- Insert sample data
INSERT INTO categories (id, name, description) VALUES
    (gen_random_uuid(), 'Electronics', 'Electronic devices and accessories'),
    (gen_random_uuid(), 'Clothing', 'Apparel and fashion items'),
    (gen_random_uuid(), 'Home & Garden', 'Home improvement and garden supplies'),
    (gen_random_uuid(), 'Sports', 'Sports equipment and accessories'),
    (gen_random_uuid(), 'Books', 'Books and educational materials')
ON CONFLICT DO NOTHING;

-- Insert sample users
INSERT INTO users (id, email, first_name, last_name, role, business_name, address, phone_number) VALUES
    (gen_random_uuid(), 'retailer1@example.com', 'John', 'Retailer', 'retailer', 'Retail Store 1', '123 Main St, City', '+1234567890'),
    (gen_random_uuid(), 'distributor1@example.com', 'Jane', 'Distributor', 'distributor', 'Distribution Co 1', '456 Business Ave, City', '+1234567891'),
    (gen_random_uuid(), 'manufacturer1@example.com', 'Bob', 'Manufacturer', 'manufacturer', 'Manufacturing Co 1', '789 Industrial Blvd, City', '+1234567892')
ON CONFLICT DO NOTHING; 