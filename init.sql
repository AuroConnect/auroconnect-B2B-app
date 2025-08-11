-- Initialize AuroMart Database for MySQL

-- Create database if not exists
CREATE DATABASE IF NOT EXISTS wa;
USE wa;

-- Create tables
CREATE TABLE IF NOT EXISTS users (
    id VARCHAR(36) PRIMARY KEY DEFAULT (UUID()),
    email VARCHAR(255) UNIQUE,
    first_name VARCHAR(255),
    last_name VARCHAR(255),
    profile_image_url VARCHAR(500),
    role VARCHAR(50) NOT NULL DEFAULT 'retailer',
    business_name TEXT,
    address TEXT,
    phone_number VARCHAR(50),
    whatsapp_number VARCHAR(50),
    password_hash VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS categories (
    id VARCHAR(36) PRIMARY KEY DEFAULT (UUID()),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS products (
    id VARCHAR(36) PRIMARY KEY DEFAULT (UUID()),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    sku VARCHAR(255) UNIQUE NOT NULL,
    category_id VARCHAR(36),
    manufacturer_id VARCHAR(36),
    image_url TEXT,
    base_price DECIMAL(10,2),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES categories(id),
    FOREIGN KEY (manufacturer_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS inventory (
    id VARCHAR(36) PRIMARY KEY DEFAULT (UUID()),
    distributor_id VARCHAR(36) NOT NULL,
    product_id VARCHAR(36) NOT NULL,
    quantity INTEGER NOT NULL DEFAULT 0,
    selling_price DECIMAL(10,2),
    is_available BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (distributor_id) REFERENCES users(id),
    FOREIGN KEY (product_id) REFERENCES products(id)
);

CREATE TABLE IF NOT EXISTS orders (
    id VARCHAR(36) PRIMARY KEY DEFAULT (UUID()),
    order_number VARCHAR(255) UNIQUE NOT NULL,
    retailer_id VARCHAR(36) NOT NULL,
    distributor_id VARCHAR(36) NOT NULL,
    status VARCHAR(50) DEFAULT 'pending',
    delivery_mode VARCHAR(50) DEFAULT 'delivery',
    total_amount DECIMAL(10,2),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (retailer_id) REFERENCES users(id),
    FOREIGN KEY (distributor_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS order_items (
    id VARCHAR(36) PRIMARY KEY DEFAULT (UUID()),
    order_id VARCHAR(36) NOT NULL,
    product_id VARCHAR(36) NOT NULL,
    quantity INTEGER NOT NULL,
    unit_price DECIMAL(10,2) NOT NULL,
    total_price DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (order_id) REFERENCES orders(id),
    FOREIGN KEY (product_id) REFERENCES products(id)
);

CREATE TABLE IF NOT EXISTS partnerships (
    id VARCHAR(36) PRIMARY KEY DEFAULT (UUID()),
    requester_id VARCHAR(36) NOT NULL,
    partner_id VARCHAR(36) NOT NULL,
    status VARCHAR(50) DEFAULT 'pending',
    partnership_type VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (requester_id) REFERENCES users(id),
    FOREIGN KEY (partner_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS favorites (
    id VARCHAR(36) PRIMARY KEY DEFAULT (UUID()),
    user_id VARCHAR(36) NOT NULL,
    favorite_user_id VARCHAR(36) NOT NULL,
    favorite_type VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (favorite_user_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS search_history (
    id VARCHAR(36) PRIMARY KEY DEFAULT (UUID()),
    user_id VARCHAR(36) NOT NULL,
    search_term VARCHAR(255) NOT NULL,
    search_type VARCHAR(50) NOT NULL,
    result_count INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS invoices (
    id VARCHAR(36) PRIMARY KEY DEFAULT (UUID()),
    order_id VARCHAR(36) NOT NULL,
    invoice_number VARCHAR(255) UNIQUE NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    status VARCHAR(50) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (order_id) REFERENCES orders(id)
);

CREATE TABLE IF NOT EXISTS whatsapp_notifications (
    id VARCHAR(36) PRIMARY KEY DEFAULT (UUID()),
    user_id VARCHAR(36) NOT NULL,
    message TEXT NOT NULL,
    type VARCHAR(50) NOT NULL,
    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_delivered BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS carts (
    id VARCHAR(36) PRIMARY KEY DEFAULT (UUID()),
    user_id VARCHAR(36) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS cart_items (
    id VARCHAR(36) PRIMARY KEY DEFAULT (UUID()),
    cart_id VARCHAR(36) NOT NULL,
    product_id VARCHAR(36) NOT NULL,
    quantity INTEGER NOT NULL DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (cart_id) REFERENCES carts(id),
    FOREIGN KEY (product_id) REFERENCES products(id)
);

-- Create indexes
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role);
CREATE INDEX idx_products_category ON products(category_id);
CREATE INDEX idx_products_manufacturer ON products(manufacturer_id);
CREATE INDEX idx_inventory_distributor ON inventory(distributor_id);
CREATE INDEX idx_inventory_product ON inventory(product_id);
CREATE INDEX idx_orders_retailer ON orders(retailer_id);
CREATE INDEX idx_orders_distributor ON orders(distributor_id);
CREATE INDEX idx_partnerships_requester ON partnerships(requester_id);
CREATE INDEX idx_partnerships_partner ON partnerships(partner_id);
CREATE INDEX idx_favorites_user ON favorites(user_id);
CREATE INDEX idx_favorites_favorite_user ON favorites(favorite_user_id);
CREATE INDEX idx_search_history_user ON search_history(user_id);
CREATE INDEX idx_invoices_order ON invoices(order_id);
CREATE INDEX idx_whatsapp_notifications_user ON whatsapp_notifications(user_id);
CREATE INDEX idx_carts_user ON carts(user_id);
CREATE INDEX idx_cart_items_cart ON cart_items(cart_id);
CREATE INDEX idx_cart_items_product ON cart_items(product_id);

-- Insert sample data
INSERT INTO categories (id, name, description) VALUES
    (UUID(), 'Electronics', 'Electronic devices and accessories'),
    (UUID(), 'Clothing', 'Apparel and fashion items'),
    (UUID(), 'Home & Garden', 'Home improvement and garden supplies'),
    (UUID(), 'Sports', 'Sports equipment and accessories'),
    (UUID(), 'Books', 'Books and educational materials')
ON DUPLICATE KEY UPDATE name=name;

-- Insert sample users
INSERT INTO users (id, email, first_name, last_name, role, business_name, address, phone_number) VALUES
    (UUID(), 'retailer1@example.com', 'John', 'Retailer', 'retailer', 'Retail Store 1', '123 Main St, City', '+1234567890'),
    (UUID(), 'distributor1@example.com', 'Jane', 'Distributor', 'distributor', 'Distribution Co 1', '456 Business Ave, City', '+1234567891'),
    (UUID(), 'manufacturer1@example.com', 'Bob', 'Manufacturer', 'manufacturer', 'Manufacturing Co 1', '789 Industrial Blvd, City', '+1234567892')
ON DUPLICATE KEY UPDATE email=email; 