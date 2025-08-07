-- Drop existing tables if they exist
DROP TABLE IF EXISTS invoices CASCADE;
DROP TABLE IF EXISTS invoice_items CASCADE;
DROP TABLE IF EXISTS orders CASCADE;
DROP TABLE IF EXISTS order_items CASCADE;
DROP TABLE IF EXISTS partner_links CASCADE;
DROP TABLE IF EXISTS products CASCADE;
DROP TABLE IF EXISTS users CASCADE;

-- Create users table
CREATE TABLE users (
    id VARCHAR(36) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL DEFAULT 'retailer',
    business_name TEXT,
    address TEXT,
    phone_number VARCHAR(50),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create products table
CREATE TABLE products (
    id VARCHAR(36) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    sku VARCHAR(100) UNIQUE NOT NULL,
    category VARCHAR(100) NOT NULL,
    description TEXT,
    price NUMERIC(10, 2) NOT NULL,
    unit VARCHAR(50) NOT NULL DEFAULT 'piece',
    stock INTEGER NOT NULL DEFAULT 0,
    image_url VARCHAR(500),
    created_by VARCHAR(36) NOT NULL REFERENCES users(id),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create partner_links table
CREATE TABLE partner_links (
    id VARCHAR(36) PRIMARY KEY,
    manufacturer_id VARCHAR(36) REFERENCES users(id),
    distributor_id VARCHAR(36) REFERENCES users(id),
    retailer_id VARCHAR(36) REFERENCES users(id),
    link_type VARCHAR(50) NOT NULL,
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create orders table
CREATE TABLE orders (
    id VARCHAR(36) PRIMARY KEY,
    buyer_id VARCHAR(36) NOT NULL REFERENCES users(id),
    seller_id VARCHAR(36) NOT NULL REFERENCES users(id),
    product_id VARCHAR(36) NOT NULL REFERENCES products(id),
    quantity INTEGER NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    delivery_method VARCHAR(50),
    delivery_address TEXT,
    invoice_path VARCHAR(500),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create invoices table
CREATE TABLE invoices (
    id VARCHAR(36) PRIMARY KEY,
    order_id VARCHAR(36) NOT NULL REFERENCES orders(id),
    pdf_url VARCHAR(500) NOT NULL,
    invoice_number VARCHAR(100) UNIQUE NOT NULL,
    total_amount NUMERIC(10, 2) NOT NULL,
    tax_amount NUMERIC(10, 2) DEFAULT 0,
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role);
CREATE INDEX idx_products_created_by ON products(created_by);
CREATE INDEX idx_products_category ON products(category);
CREATE INDEX idx_products_sku ON products(sku);
CREATE INDEX idx_partner_links_manufacturer ON partner_links(manufacturer_id);
CREATE INDEX idx_partner_links_distributor ON partner_links(distributor_id);
CREATE INDEX idx_partner_links_retailer ON partner_links(retailer_id);
CREATE INDEX idx_partner_links_type ON partner_links(link_type);
CREATE INDEX idx_orders_buyer ON orders(buyer_id);
CREATE INDEX idx_orders_seller ON orders(seller_id);
CREATE INDEX idx_orders_product ON orders(product_id);
CREATE INDEX idx_orders_status ON orders(status);
CREATE INDEX idx_invoices_order ON invoices(order_id);
CREATE INDEX idx_invoices_number ON invoices(invoice_number);

-- Insert sample data
INSERT INTO users (id, name, email, password_hash, role, business_name, phone_number, address) VALUES
('manufacturer-1', 'Test Manufacturer', 'manufacturer@test.com', 'hashed_password', 'manufacturer', 'Test Manufacturing Co', '1234567890', '123 Factory St'),
('distributor-1', 'Test Distributor', 'distributor@test.com', 'hashed_password', 'distributor', 'Test Distribution Co', '1234567891', '456 Distribution Ave'),
('retailer-1', 'Test Retailer', 'retailer@test.com', 'hashed_password', 'retailer', 'Test Retail Store', '1234567892', '789 Retail Blvd');

-- Insert sample products
INSERT INTO products (id, name, sku, category, description, price, unit, stock, created_by) VALUES
('product-1', 'Premium Mattress', 'SKU-PREM-001', 'Mattress', 'High-quality premium mattress', 500.00, 'piece', 100, 'manufacturer-1'),
('product-2', 'Standard Mattress', 'SKU-STD-001', 'Mattress', 'Standard quality mattress', 300.00, 'piece', 200, 'manufacturer-1');

-- Insert sample partner links
INSERT INTO partner_links (id, manufacturer_id, distributor_id, link_type) VALUES
('link-1', 'manufacturer-1', 'distributor-1', 'manufacturer_distributor');

INSERT INTO partner_links (id, distributor_id, retailer_id, link_type) VALUES
('link-2', 'distributor-1', 'retailer-1', 'distributor_retailer'); 