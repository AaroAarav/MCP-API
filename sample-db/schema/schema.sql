-- Sample DB Schema

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 1. users
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) NOT NULL UNIQUE,
    email VARCHAR(255) NOT NULL UNIQUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    last_login TIMESTAMPTZ,
    status VARCHAR(20) DEFAULT 'active'
);
-- Index intentionally missing for status column to generate seq scans later

-- 2. products
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    price NUMERIC(10, 2) NOT NULL,
    stock INT NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 3. orders
CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL REFERENCES users(id),
    total_amount NUMERIC(10, 2) NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    created_at TIMESTAMPTZ DEFAULT NOW()
);
-- Unindexed Foreign Key: user_id to cause issues
-- CREATE INDEX idx_orders_user_id ON orders(user_id); -- Missing on purpose

-- 4. order_items
CREATE TABLE order_items (
    id SERIAL PRIMARY KEY,
    order_id INT NOT NULL REFERENCES orders(id),
    product_id INT NOT NULL REFERENCES products(id),
    quantity INT NOT NULL,
    unit_price NUMERIC(10, 2) NOT NULL
);
-- Unindexed FKs

-- 5. payments
CREATE TABLE payments (
    id SERIAL PRIMARY KEY,
    order_id INT NOT NULL REFERENCES orders(id),
    amount NUMERIC(10, 2) NOT NULL,
    payment_date TIMESTAMPTZ DEFAULT NOW(),
    status VARCHAR(20) DEFAULT 'completed'
);

-- Duplicate indexes on payments to trigger duplicate index detection
CREATE INDEX idx_payments_order_id ON payments(order_id);
CREATE INDEX idx_payments_order_id_dup ON payments(order_id);

-- 6. sessions
CREATE TABLE sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id INT REFERENCES users(id),
    token VARCHAR(255) NOT NULL,
    expires_at TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
-- Create an index that will never be used (unused index detection)
CREATE INDEX idx_sessions_never_used ON sessions(token, expires_at);

-- 7. audit_logs
CREATE TABLE audit_logs (
    id SERIAL PRIMARY KEY,
    actor VARCHAR(100) NOT NULL,
    action VARCHAR(50) NOT NULL,
    target VARCHAR(255),
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    success BOOLEAN,
    duration_ms INT,
    result_detail TEXT
);
