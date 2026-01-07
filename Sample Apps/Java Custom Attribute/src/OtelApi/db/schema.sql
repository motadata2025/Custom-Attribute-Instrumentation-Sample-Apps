-- Create database (run this separately as postgres superuser)
-- CREATE DATABASE userdb;

-- Connect to userdb database before running the rest

-- Drop table if exists (for clean setup)
DROP TABLE IF EXISTS users;

-- Create users table with username as primary key
-- Includes all data types: String, int, double, boolean, List (stored as comma-separated string)
CREATE TABLE users (
    username VARCHAR(50) PRIMARY KEY,       -- String
    email VARCHAR(100) NOT NULL,            -- String
    full_name VARCHAR(100),                 -- String
    age INTEGER,                            -- int
    salary DECIMAL(12,2) DEFAULT 0.00,      -- double/float
    is_active BOOLEAN DEFAULT true,         -- boolean
    tags TEXT DEFAULT ''                    -- List<String> stored as comma-separated
);

-- Create index on email for faster lookups
CREATE INDEX idx_users_email ON users(email);

-- Insert dummy data for testing with all data types
INSERT INTO users (username, email, full_name, age, salary, is_active, tags) VALUES
    ('john_doe', 'john.doe@example.com', 'John Doe', 30, 75000.50, true, 'developer,senior,java'),
    ('jane_smith', 'jane.smith@example.com', 'Jane Smith', 28, 68000.00, true, 'designer,ui,ux'),
    ('bob_wilson', 'bob.wilson@example.com', 'Bob Wilson', 35,  95000.75, true, 'manager,lead'),
    ('alice_johnson', 'alice.johnson@example.com', 'Alice Johnson', 25, 55000.00, true, 'developer,junior,python'),
    ('charlie_brown', 'charlie.brown@example.com', 'Charlie Brown', 40, 120000.00, true, 'architect,senior'),
    ('diana_prince', 'diana.prince@example.com', 'Diana Prince', 32, 82000.25, false, 'qa,automation'),
    ('edward_stark', 'edward.stark@example.com', 'Edward Stark', 45, 150000.00, true, 'cto,executive'),
    ('fiona_green', 'fiona.green@example.com', 'Fiona Green', 29, 62000.50, true, 'developer,frontend,react'),
    ('george_lucas', 'george.lucas@example.com', 'George Lucas', 55, 200000.00, false, 'consultant,advisor'),
    ('helen_troy', 'helen.troy@example.com', 'Helen Troy', 27, 58000.00, true, 'developer,backend,nodejs');

-- Verify data
SELECT * FROM users;

