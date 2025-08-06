-- Initialize AuroMart Database

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create tables
CREATE TABLE IF NOT EXISTS users (
    id VARCHAR(36) PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE,
    first_name VARCHAR(255),
    last_name VARCHAR(255),
    profile_image_url VARCHAR(500),
    role VARCHAR(50) NOT NULL DEFAULT 'retailer',
    business_name TEXT,
    address TEXT,
    phone_number VARCHAR(50),
    whatsapp_number VARCHAR(50),
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

CREATE TABLE IF NOT EXISTS orders (
    id VARCHAR(36) PRIMARY KEY DEFAULT gen_random_uuid(),
    order_number VARCHAR(255) UNIQUE NOT NULL,
    retailer_id VARCHAR(36) REFERENCES users(id) NOT NULL,
    distributor_id VARCHAR(36) REFERENCES users(id) NOT NULL,
    status VARCHAR(50) DEFAULT 'pending',
    delivery_mode VARCHAR(50) DEFAULT 'delivery',
    total_amount DECIMAL(10,2),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS order_items (
    id VARCHAR(36) PRIMARY KEY DEFAULT gen_random_uuid(),
    order_id VARCHAR(36) REFERENCES orders(id) NOT NULL,
    product_id VARCHAR(36) REFERENCES products(id) NOT NULL,
    quantity INTEGER NOT NULL,
    unit_price DECIMAL(10,2) NOT NULL,
    total_price DECIMAL(10,2) NOT NULL
);

CREATE TABLE IF NOT EXISTS partnerships (
    id VARCHAR(36) PRIMARY KEY DEFAULT gen_random_uuid(),
    requester_id VARCHAR(36) REFERENCES users(id) NOT NULL,
    partner_id VARCHAR(36) REFERENCES users(id) NOT NULL,
    status VARCHAR(50) DEFAULT 'pending',
    partnership_type VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);
CREATE INDEX IF NOT EXISTS idx_products_category ON products(category_id);
CREATE INDEX IF NOT EXISTS idx_products_manufacturer ON products(manufacturer_id);
CREATE INDEX IF NOT EXISTS idx_inventory_distributor ON inventory(distributor_id);
CREATE INDEX IF NOT EXISTS idx_inventory_product ON inventory(product_id);
CREATE INDEX IF NOT EXISTS idx_orders_retailer ON orders(retailer_id);
CREATE INDEX IF NOT EXISTS idx_orders_distributor ON orders(distributor_id);
CREATE INDEX IF NOT EXISTS idx_partnerships_requester ON partnerships(requester_id);
CREATE INDEX IF NOT EXISTS idx_partnerships_partner ON partnerships(partner_id);
CREATE INDEX IF NOT EXISTS idx_favorites_user ON favorites(user_id);
CREATE INDEX IF NOT EXISTS idx_favorites_favorite_user ON favorites(favorite_user_id);
CREATE INDEX IF NOT EXISTS idx_search_history_user ON search_history(user_id);

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