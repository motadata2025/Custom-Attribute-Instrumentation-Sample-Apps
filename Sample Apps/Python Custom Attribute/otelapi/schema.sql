-- Drop table if exists
DROP TABLE IF EXISTS users CASCADE;

-- Create users table with username as primary key
CREATE TABLE users (
    username VARCHAR(50) PRIMARY KEY,
    email VARCHAR(100) NOT NULL,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    age INTEGER,
    phone VARCHAR(20),
    address TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert dummy data
INSERT INTO users (username, email, first_name, last_name, age, phone, address) VALUES
('john_doe', 'john.doe@example.com', 'John', 'Doe', 28, '+1-555-0101', '123 Main St, New York, NY 10001'),
('jane_smith', 'jane.smith@example.com', 'Jane', 'Smith', 32, '+1-555-0102', '456 Oak Ave, Los Angeles, CA 90001'),
('bob_johnson', 'bob.johnson@example.com', 'Bob', 'Johnson', 45, '+1-555-0103', '789 Pine Rd, Chicago, IL 60601'),
('alice_williams', 'alice.williams@example.com', 'Alice', 'Williams', 26, '+1-555-0104', '321 Elm St, Houston, TX 77001'),
('charlie_brown', 'charlie.brown@example.com', 'Charlie', 'Brown', 35, '+1-555-0105', '654 Maple Dr, Phoenix, AZ 85001'),
('diana_davis', 'diana.davis@example.com', 'Diana', 'Davis', 29, '+1-555-0106', '987 Cedar Ln, Philadelphia, PA 19101'),
('edward_miller', 'edward.miller@example.com', 'Edward', 'Miller', 41, '+1-555-0107', '147 Birch Blvd, San Antonio, TX 78201'),
('fiona_wilson', 'fiona.wilson@example.com', 'Fiona', 'Wilson', 24, '+1-555-0108', '258 Spruce Way, San Diego, CA 92101'),
('george_moore', 'george.moore@example.com', 'George', 'Moore', 38, '+1-555-0109', '369 Walnut Ct, Dallas, TX 75201'),
('hannah_taylor', 'hannah.taylor@example.com', 'Hannah', 'Taylor', 31, '+1-555-0110', '741 Ash Pl, San Jose, CA 95101');

