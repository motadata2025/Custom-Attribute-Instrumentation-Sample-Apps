# Setup Guide - Go Custom Attribute Instrumentation

This guide provides step-by-step instructions for setting up and running all projects in this repository.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Database Setup](#database-setup)
3. [Project Setup](#project-setup)
4. [Running the Applications](#running-the-applications)
5. [Testing](#testing)
6. [Troubleshooting](#troubleshooting)

## Prerequisites

### Required Software

- **Go**: Version 1.23.12 or higher
  ```bash
  go version
  # Should output: go version go1.23.12 or higher
  ```

- **PostgreSQL**: Version 12 or higher (for otelapi and oteltracer)
  ```bash
  psql --version
  # Should output: psql (PostgreSQL) 12.x or higher
  ```

### Optional (for Production Tracing)

- **OpenTelemetry eBPF Auto-Instrumentation Agent**
- **Jaeger/Tempo/Other OTLP-compatible backend**

## Database Setup

### 1. Install PostgreSQL

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
```

**macOS:**
```bash
brew install postgresql@14
brew services start postgresql@14
```

**Windows:**
Download and install from [postgresql.org](https://www.postgresql.org/download/windows/)

### 2. Start PostgreSQL Service

**Linux:**
```bash
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

**macOS:**
```bash
brew services start postgresql@14
```

### 3. Create Database and User

```bash
# Connect to PostgreSQL
sudo -u postgres psql

# Create database (if needed)
CREATE DATABASE postgres;

# Create user (if needed)
CREATE USER postgres WITH PASSWORD 'postgres';

# Grant privileges
GRANT ALL PRIVILEGES ON DATABASE postgres TO postgres;

# Exit
\q
```

### 4. Verify Connection

```bash
psql -h localhost -p 5432 -U postgres -d postgres
# Enter password: postgres
# Should connect successfully
```

## Project Setup

### 1. Clone/Navigate to Repository

```bash
cd "/home/shiven-patel/Desktop/Open Telemetry/Custom Attribute/Go Custom Attribute"
```

### 2. Setup OtelAPI (Recommended - Working Implementation)

```bash
cd otelapi

# Copy environment file
cp .env.example .env

# Edit .env if needed (optional)
nano .env

# Install dependencies
go mod download

# Generate Swagger docs (if modified)
go install github.com/swaggo/swag/cmd/swag@latest
swag init

# Build the application
go build -o otelapi_exe

# Verify build
./otelapi_exe --help
```

### 3. Setup OtelTracer (Educational - Non-Working)

```bash
cd ../oteltracer

# Copy environment file
cp .env.example .env

# Edit .env if needed (optional)
nano .env

# Install dependencies
go mod download

# Generate Swagger docs (if modified)
swag init

# Build the application
go build -o oteltracer_exe
```

### 4. Setup OtelTracer02 (Quick Demo)

```bash
cd ../oteltracer02

# Install dependencies
go mod download

# Build the application
go build -o oteltracer02
```

## Running the Applications

### Option 1: Run OtelAPI (Recommended)

```bash
cd otelapi

# Method 1: Using go run
go run .

# Method 2: Using compiled binary
./otelapi_exe

# Access the application
# API: http://localhost:8080
# Swagger: http://localhost:8080/swagger/
# Health: http://localhost:8080/health
```

### Option 2: Run OtelTracer02 (Quick Demo - No Database)

```bash
cd oteltracer02

# Method 1: Using go run
go run main.go

# Method 2: Using compiled binary
./oteltracer02

# Access the application
# Web UI: http://localhost:8082
```

### Option 3: Run OtelTracer (Educational)

```bash
cd oteltracer

# Method 1: Using go run
go run .

# Method 2: Using compiled binary
./oteltracer_exe

# Access the application
# API: http://localhost:8081
# Swagger: http://localhost:8081/swagger/
```

### Running Multiple Projects Simultaneously

You can run all three projects at the same time (they use different ports):

```bash
# Terminal 1
cd otelapi && go run .

# Terminal 2
cd oteltracer && go run .

# Terminal 3
cd oteltracer02 && go run main.go
```

## Testing

### Test OtelAPI

```bash
# Health check
curl http://localhost:8080/health

# Create a user
curl -X POST http://localhost:8080/users \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "full_name": "Test User"
  }'

# Get user
curl http://localhost:8080/users/testuser

# Get all users
curl http://localhost:8080/users

# Update user
curl -X PUT http://localhost:8080/users/testuser \
  -H "Content-Type: application/json" \
  -d '{
    "email": "updated@example.com",
    "full_name": "Updated User"
  }'

# Delete user
curl -X DELETE http://localhost:8080/users/testuser
```

### Test OtelTracer02

```bash
# Test external API call
curl http://localhost:8082/api/call

# Test all attribute types
curl http://localhost:8082/api/test-attributes

# Or use the web interface
open http://localhost:8082
```

## Troubleshooting

### Database Connection Issues

**Error**: `Failed to connect to database`

**Solution**:
1. Verify PostgreSQL is running:
   ```bash
   sudo systemctl status postgresql
   ```

2. Check connection parameters in `.env` file

3. Test connection manually:
   ```bash
   psql -h localhost -p 5432 -U postgres -d postgres
   ```

### Port Already in Use

**Error**: `bind: address already in use`

**Solution**:
1. Check what's using the port:
   ```bash
   lsof -i :8080  # or :8081, :8082
   ```

2. Kill the process or change PORT in `.env` file

### Go Module Issues

**Error**: `cannot find module`

**Solution**:
```bash
go mod tidy
go mod download
```

### Swagger Generation Issues

**Error**: `swag: command not found`

**Solution**:
```bash
go install github.com/swaggo/swag/cmd/swag@latest
export PATH=$PATH:$(go env GOPATH)/bin
swag init
```

### Permission Denied on Binary

**Error**: `permission denied: ./otelapi_exe`

**Solution**:
```bash
chmod +x otelapi_exe
./otelapi_exe
```

## Next Steps

1. **Read the Documentation**: Start with [README.md](README.md)
2. **Understand the POC**: Review [Go_Custom_Attribute_POC.md](Go_Custom_Attribute_POC.md)
3. **Compare Methods**: Read [Methods.md](Methods.md)
4. **Explore Projects**: Check individual project READMEs
5. **View Snapshots**: See [TestingSnapshots/](TestingSnapshots/)

## Support

For issues or questions:
- Review project-specific README files
- Check the troubleshooting section above
- Review the POC documentation

---

**Last Updated**: January 6, 2026

