-- Create database (run this separately as postgres superuser)
CREATE DATABASE orderdb;

-- Connect to orderdb database before running the rest

-- Drop tables if exist (for clean setup)
DROP TABLE IF EXISTS order_items;
DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS customers;

-- Create customers table
CREATE TABLE customers (
    customer_id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL,
    phone VARCHAR(20),
    address TEXT,
    is_premium BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create orders table
CREATE TABLE orders (
    order_id VARCHAR(50) PRIMARY KEY,
    customer_id VARCHAR(50) NOT NULL REFERENCES customers(customer_id),
    total DECIMAL(12,2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'USD',
    status VARCHAR(20) DEFAULT 'PENDING',
    payment_id VARCHAR(50),
    payment_method VARCHAR(20),
    tracking_number VARCHAR(50),
    carrier VARCHAR(20),
    shipping_method VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create order_items table
CREATE TABLE order_items (
    item_id SERIAL PRIMARY KEY,
    order_id VARCHAR(50) NOT NULL REFERENCES orders(order_id),
    product_name VARCHAR(100) NOT NULL,
    quantity INTEGER NOT NULL,
    unit_price DECIMAL(10,2) NOT NULL,
    subtotal DECIMAL(12,2) NOT NULL
);

-- Create indexes
CREATE INDEX idx_orders_customer ON orders(customer_id);
CREATE INDEX idx_orders_status ON orders(status);
CREATE INDEX idx_order_items_order ON order_items(order_id);

-- Insert dummy customers
INSERT INTO customers (customer_id, name, email, phone, address, is_premium) VALUES
    ('CUST-001', 'John Doe', 'john.doe@example.com', '+1-555-0101', '123 Main St, New York, NY 10001', true),
    ('CUST-002', 'Jane Smith', 'jane.smith@example.com', '+1-555-0102', '456 Oak Ave, Los Angeles, CA 90001', false),
    ('CUST-003', 'Bob Wilson', 'bob.wilson@example.com', '+1-555-0103', '789 Pine Rd, Chicago, IL 60601', true),
    ('CUST-004', 'Alice Johnson', 'alice.johnson@example.com', '+1-555-0104', '321 Elm St, Houston, TX 77001', false),
    ('CUST-005', 'Charlie Brown', 'charlie.brown@example.com', '+1-555-0105', '654 Maple Dr, Phoenix, AZ 85001', true);

-- Insert dummy orders
INSERT INTO orders (order_id, customer_id, total, currency, status, payment_id, payment_method, tracking_number, carrier, shipping_method) VALUES
    ('ORD-001', 'CUST-001', 299.99, 'USD', 'COMPLETED', 'PAY-1001', 'CREDIT_CARD', 'TRK-1001', 'FedEx', 'EXPRESS'),
    ('ORD-002', 'CUST-001', 149.50, 'USD', 'SHIPPED', 'PAY-1002', 'PAYPAL', 'TRK-1002', 'UPS', 'STANDARD'),
    ('ORD-003', 'CUST-002', 599.00, 'USD', 'COMPLETED', 'PAY-1003', 'CREDIT_CARD', 'TRK-1003', 'FedEx', 'EXPRESS'),
    ('ORD-004', 'CUST-003', 89.99, 'USD', 'PROCESSING', 'PAY-1004', 'DEBIT_CARD', NULL, NULL, 'STANDARD'),
    ('ORD-005', 'CUST-003', 1250.00, 'USD', 'COMPLETED', 'PAY-1005', 'CREDIT_CARD', 'TRK-1005', 'DHL', 'EXPRESS'),
    ('ORD-006', 'CUST-004', 45.00, 'USD', 'PENDING', NULL, NULL, NULL, NULL, 'ECONOMY'),
    ('ORD-007', 'CUST-005', 799.99, 'USD', 'COMPLETED', 'PAY-1007', 'CREDIT_CARD', 'TRK-1007', 'FedEx', 'EXPRESS'),
    ('ORD-008', 'CUST-002', 199.00, 'USD', 'CANCELLED', 'PAY-1008', 'PAYPAL', NULL, NULL, 'STANDARD'),
    ('ORD-009', 'CUST-001', 350.75, 'USD', 'SHIPPED', 'PAY-1009', 'CREDIT_CARD', 'TRK-1009', 'UPS', 'EXPRESS'),
    ('ORD-010', 'CUST-005', 125.50, 'USD', 'PROCESSING', 'PAY-1010', 'DEBIT_CARD', NULL, NULL, 'STANDARD');

-- Insert dummy order items
INSERT INTO order_items (order_id, product_name, quantity, unit_price, subtotal) VALUES
    ('ORD-001', 'Wireless Headphones', 1, 199.99, 199.99),
    ('ORD-001', 'Phone Case', 2, 50.00, 100.00),
    ('ORD-002', 'USB-C Cable', 3, 29.50, 88.50),
    ('ORD-002', 'Screen Protector', 2, 30.50, 61.00),
    ('ORD-003', 'Smart Watch', 1, 599.00, 599.00),
    ('ORD-004', 'Bluetooth Speaker', 1, 89.99, 89.99),
    ('ORD-005', 'Laptop Stand', 1, 150.00, 150.00),
    ('ORD-005', 'Mechanical Keyboard', 1, 250.00, 250.00),
    ('ORD-005', 'Gaming Mouse', 1, 100.00, 100.00),
    ('ORD-005', 'Monitor Arm', 1, 750.00, 750.00),
    ('ORD-006', 'Notebook Set', 3, 15.00, 45.00),
    ('ORD-007', 'Tablet', 1, 799.99, 799.99),
    ('ORD-008', 'Wireless Charger', 1, 49.00, 49.00),
    ('ORD-008', 'Power Bank', 1, 150.00, 150.00),
    ('ORD-009', 'Camera Lens', 1, 350.75, 350.75),
    ('ORD-010', 'Memory Card', 5, 25.10, 125.50);

-- Verify data
SELECT 'Customers:' AS table_name;
SELECT * FROM customers;

SELECT 'Orders:' AS table_name;
SELECT * FROM orders;

SELECT 'Order Items:' AS table_name;
SELECT * FROM order_items;

-- Summary query
SELECT 
    c.name AS customer_name,
    COUNT(o.order_id) AS total_orders,
    SUM(o.total) AS total_spent
FROM customers c
LEFT JOIN orders o ON c.customer_id = o.customer_id
GROUP BY c.customer_id, c.name
ORDER BY total_spent DESC;

