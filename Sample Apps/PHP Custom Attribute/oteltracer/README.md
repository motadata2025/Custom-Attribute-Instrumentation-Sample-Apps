# PHP User Management CRUD API with OpenTelemetry Manual Tracing

A RESTful API for user management built with PHP and PostgreSQL, demonstrating **OpenTelemetry manual tracing and custom spans**.

## Features

- ✅ Full CRUD operations for user management
- ✅ PostgreSQL database with proper indexing
- ✅ RESTful API design
- ✅ JSON request/response format
- ✅ Error handling and validation
- ✅ **OpenTelemetry manual tracing implementation**
- ✅ **Custom spans for detailed observability**

## Prerequisites

- PHP 8.0 or higher
- PostgreSQL 12 or higher
- Composer

## Installation

1. **Install dependencies:**
   ```bash
   cd oteltracer
   composer install --no-dev
   ```

2. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your database credentials
   ```

3. **Set up the database:**
   ```bash
   psql -U postgres -d postgres -f database/migrations/001_create_php_user_tbl.sql
   ```

## Running the API

Start the PHP built-in server:

```bash
composer start
# Or manually:
php -S localhost:8082 public/index.php
```

The API will be available at `http://localhost:8082`

## API Endpoints

### Health Check
```
GET /health
```

### Get All Users
```
GET /users
GET /users?is_active=true
```

### Get User by ID
```
GET /users/{id}
```

### Create User
```
POST /users
Content-Type: application/json

{
  "username": "newuser",
  "email": "newuser@example.com",
  "full_name": "New User",
  "age": 25,
  "salary": 70000.00,
  "is_active": true,
  "tags": ["developer", "php", "backend"]
}
```

### Update User
```
PUT /users/{id}
Content-Type: application/json

{
  "username": "updateduser",
  "email": "updated@example.com",
  "full_name": "Updated User",
  "age": 26,
  "salary": 75000.00,
  "is_active": true,
  "tags": ["senior", "developer"]
}
```

### Delete User
```
DELETE /users/{id}
```

## Example Usage

### Create a new user:
```bash
curl -X POST http://localhost:8082/users \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "full_name": "Test User",
    "age": 30,
    "salary": 80000.00,
    "is_active": true,
    "tags": ["developer", "php"]
  }'
```

### Get all users:
```bash
curl http://localhost:8082/users
```

### Get user by ID:
```bash
curl http://localhost:8082/users/1
```

### Update user:
```bash
curl -X PUT http://localhost:8082/users/1 \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "newemail@example.com",
    "full_name": "Updated Test User",
    "age": 31,
    "salary": 85000.00,
    "is_active": true,
    "tags": ["senior", "developer", "php"]
  }'
```

### Delete user:
```bash
curl -X DELETE http://localhost:8082/users/1
```

## Project Structure

```
oteltracer/
├── public/
│   └── index.php          # Entry point and routing
├── src/
│   ├── Config/
│   │   └── Database.php   # Database configuration
│   ├── Controllers/
│   │   └── UserController.php  # User CRUD operations with manual tracing
│   ├── Models/
│   │   └── User.php       # User model
│   ├── Repositories/
│   │   └── UserRepository.php  # Database operations
│   ├── Services/          # Service layer for custom spans
│   └── Jobs/              # Background job processing
├── database/
│   └── migrations/
│       └── 001_create_php_user_tbl.sql
├── .env                   # Environment configuration
├── composer.json          # Dependencies
└── README.md             # This file
```

## Database Schema

The `php_user_tbl` table includes:
- `id` (SERIAL PRIMARY KEY)
- `username` (VARCHAR, UNIQUE)
- `email` (VARCHAR)
- `full_name` (VARCHAR)
- `age` (INTEGER)
- `salary` (DECIMAL)
- `is_active` (BOOLEAN)
- `tags` (TEXT[])
- `created_at` (TIMESTAMP)
- `updated_at` (TIMESTAMP, auto-updated)

