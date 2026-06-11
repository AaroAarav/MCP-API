-- Data Seeding Script
-- We use generate_series to create millions of rows

-- 1. Insert 1,000,000 users
INSERT INTO users (username, email, created_at, status)
SELECT 
    'user_' || i,
    'user_' || i || '@example.com',
    NOW() - (random() * interval '365 days'),
    CASE WHEN random() < 0.9 THEN 'active' ELSE 'inactive' END
FROM generate_series(1, 1000000) i;

-- 2. Insert 10,000 products
INSERT INTO products (name, description, price, stock)
SELECT 
    'Product ' || i,
    'Description for product ' || i,
    (random() * 1000 + 10)::numeric(10, 2),
    (random() * 500)::int
FROM generate_series(1, 10000) i;

-- 3. Insert 5,000,000 orders
INSERT INTO orders (user_id, total_amount, status, created_at)
SELECT 
    (random() * 999999 + 1)::int,
    (random() * 5000 + 10)::numeric(10, 2),
    CASE WHEN random() < 0.8 THEN 'completed' ELSE 'pending' END,
    NOW() - (random() * interval '365 days')
FROM generate_series(1, 5000000) i;

-- 4. Generate Bloat in users table
-- We'll delete and update to create dead tuples
UPDATE users SET status = 'pending_review' WHERE id % 5 = 0;
DELETE FROM users WHERE id % 7 = 0;

-- 5. Generate Bloated Index
-- We update payments heavily on the same row to bloat its indexes
INSERT INTO payments (order_id, amount, status)
SELECT id, total_amount, 'processing'
FROM orders
WHERE id % 100 = 0;

UPDATE payments SET status = 'completed';
UPDATE payments SET status = 'refunded' WHERE id % 2 = 0;
UPDATE payments SET status = 'disputed' WHERE id % 3 = 0;
