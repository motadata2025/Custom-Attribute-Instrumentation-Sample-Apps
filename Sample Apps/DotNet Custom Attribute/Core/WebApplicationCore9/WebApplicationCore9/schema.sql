-- This script is intended for use with PostgreSQL.

-- Step 1: Create the new database `productdb`.
-- You can run this command from the default `postgres` database query tool.
-- Note: You may need to disconnect and reconnect to the new database in pgAdmin
-- before running the rest of the script.
CREATE DATABASE productdb;

-- Step 2: Connect to the `productdb` database.
-- In pgAdmin, you can do this by right-clicking the `productdb` database in the
-- browser tree and selecting "Query Tool".

-- Step 3: Run the following commands in the context of the `productdb` database.

-- Drop the table if it already exists to start fresh.
DROP TABLE IF EXISTS "Products";

-- Create the "Products" table.
CREATE TABLE "Products" (
    "Id" SERIAL PRIMARY KEY,
    "Name" TEXT NOT NULL,
    "IsAvailable" BOOLEAN NOT NULL,
    "Price" DOUBLE PRECISION NOT NULL,
    "Weight" REAL NOT NULL,
    "Quantity" INTEGER NOT NULL,
    "Barcode" BIGINT NOT NULL,
    "Discount" REAL NOT NULL,
    "Flags" BOOLEAN[] NOT NULL,
    "Dimensions" DOUBLE PRECISION[] NOT NULL,
    "Ratings" REAL[] NOT NULL,
    "Serials" INTEGER[] NOT NULL,
    "Categories" BIGINT[] NOT NULL,
    "Tags" TEXT[] NOT NULL
);

-- Insert sample data into the "Products" table.
INSERT INTO "Products" ("Name", "IsAvailable", "Price", "Weight", "Quantity", "Barcode", "Discount", "Flags", "Dimensions", "Ratings", "Serials", "Categories", "Tags")
VALUES 
(
    'Laptop Pro 15', 
    true, 
    1499.99, 
    1.8, 
    50, 
    1234567890123, 
    0.1, 
    ARRAY[true, false, true], 
    ARRAY[35.79, 24.59, 1.55], 
    ARRAY[4.5, 4.8, 4.2], 
    ARRAY[1001, 1002, 1003], 
    ARRAY[101, 202], 
    ARRAY['electronics', 'computer', 'pro']
),
(
    'Wireless Mouse', 
    true, 
    29.99, 
    0.1, 
    200, 
    9876543210987, 
    0.05, 
    ARRAY[true, true], 
    ARRAY[10.5, 6.5, 3.8], 
    ARRAY[4.2, 4.0], 
    ARRAY[2001, 2002], 
    ARRAY[102, 303], 
    ARRAY['electronics', 'accessory', 'peripheral']
),
(
    'Mechanical Keyboard', 
    false, 
    120.00, 
    1.1, 
    0, 
    5555555555555, 
    0.0, 
    ARRAY[true, false], 
    ARRAY[44.0, 13.5, 3.5], 
    ARRAY[4.9, 4.8], 
    ARRAY[3001], 
    ARRAY[102, 304], 
    ARRAY['electronics', 'keyboard', 'gaming']
);
