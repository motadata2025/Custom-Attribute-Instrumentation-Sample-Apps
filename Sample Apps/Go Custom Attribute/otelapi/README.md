# OtelAPI - User Management API with OpenTelemetry Custom Attributes

## Overview

**OtelAPI** is a demonstration project showing how to inject custom business attributes into OpenTelemetry traces using the **Explicit Span Creation** approach in Go. This project implements a complete user management REST API with PostgreSQL database integration.

## Purpose

This project demonstrates the **WORKING** approach for adding custom attributes to OpenTelemetry traces when using eBPF-based auto-instrumentation:

- ✅ **Creates new child spans** using `tracer.Start()`
- ✅ **Adds custom attributes** to manually created spans
- ✅ **Works with eBPF auto-instrumentation** - manual spans become children of auto-instrumented spans
- ✅ **Captures timing and duration** of business operations

## Architecture

### Technology Stack

- **Language**: Go 1.24.0
- **Database**: PostgreSQL
- **Web Framework**: Standard `net/http`
- **Documentation**: Swagger/OpenAPI
- **Observability**: OpenTelemetry 1.24.0

### Project Structure

```
otelapi/
├── main.go           # Application entry point and HTTP routing
├── handlers.go       # HTTP request handlers with custom span creation
├── repository.go     # Database operations with custom spans
├── database.go       # Database connection and schema management
├── models.go         # Data models and request/response structures
├── go.mod            # Go module dependencies
├── docs/             # Auto-generated Swagger documentation
└── NotPossible.md    # Technical explanation of why active span enrichment doesn't work
```

## Key Features

### 1. Custom Attribute Injection

Every handler and repository method creates a **new child span** and attaches custom business attributes:

```go
tracer := otel.Tracer("otelapi")
ctx, span := tracer.Start(r.Context(), "CreateUser")
defer span.End()

span.SetAttributes(
    attribute.String("apm.http.method", r.Method),
    attribute.String("apm.operation", "create_user"),
    attribute.String("apm.user.username", req.Username),
)
```

### 2. Complete CRUD Operations

- **Create User**: `POST /users`
- **Get User**: `GET /users/{username}`
- **Get All Users**: `GET /users`
- **Update User**: `PUT /users/{username}`
- **Delete User**: `DELETE /users/{username}`
- **Health Check**: `GET /health`

### 3. Swagger Documentation

Interactive API documentation available at:
```
http://localhost:8080/swagger/
```

### 4. Multi-Layer Tracing

The application creates a hierarchical trace structure:

```
HTTP Request (auto-instrumented by eBPF)
└── Handler Span (manual - with custom attributes)
    └── Repository Span (manual - with custom attributes)
        └── Database Query (auto-instrumented by eBPF)
```

## Installation & Setup

### Prerequisites

- Go 1.23.12 or higher
- PostgreSQL database
- OpenTelemetry eBPF auto-instrumentation agent (for production use)

### Environment Variables

Configure the following environment variables:

```bash
DB_HOST=localhost
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=postgres
DB_NAME=postgres
PORT=8080
```

### Build & Run

1. **Install dependencies**:
   ```bash
   go mod download
   ```

2. **Generate Swagger documentation** (if modified):
   ```bash
   swag init
   ```

3. **Run the application**:
   ```bash
   go run .
   ```

4. **Or build and run**:
   ```bash
   go build -o otelapi_exe
   ./otelapi_exe
   ```

### Database Schema

The application automatically creates the following schema on startup:

```sql
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(255) UNIQUE NOT NULL,
    email VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Custom Attributes Reference

### Handler-Level Attributes

| Attribute | Type | Example | Description |
|-----------|------|---------|-------------|
| `apm.http.method` | string | `"GET"` | HTTP method |
| `apm.http.url` | string | `"/users/john"` | Request URL |
| `apm.operation` | string | `"create_user"` | Business operation name |
| `apm.user.username` | string | `"john"` | Username being operated on |
| `apm.user.email` | string | `"john@example.com"` | User email |

### Repository-Level Attributes

| Attribute | Type | Example | Description |
|-----------|------|---------|-------------|
| `apm.db.operation` | string | `"insert"` | Database operation type |
| `apm.repository.method` | string | `"CreateUser"` | Repository method name |
| `apm.user.username` | string | `"john"` | Username parameter |

## Testing the API

### Create a User

```bash
curl -X POST http://localhost:8080/users \
  -H "Content-Type: application/json" \
  -d '{
    "username": "johndoe",
    "email": "john@example.com",
    "full_name": "John Doe"
  }'
```

### Get a User

```bash
curl http://localhost:8080/users/johndoe
```

### Update a User

```bash
curl -X PUT http://localhost:8080/users/johndoe \
  -H "Content-Type: application/json" \
  -d '{
    "email": "newemail@example.com",
    "full_name": "John Updated"
  }'
```

### Delete a User

```bash
curl -X DELETE http://localhost:8080/users/johndoe
```

## Why This Approach Works

Unlike the `oteltracer` project which attempts to enrich existing spans (doesn't work with eBPF), this project:

1. **Creates new spans** explicitly using `tracer.Start()`
2. **These spans become children** of auto-instrumented spans through context propagation
3. **Custom attributes are attached** to the manually created spans
4. **Both auto and manual spans** appear in the same trace with proper parent-child relationships

See `NotPossible.md` for detailed technical explanation.

## Related Documentation

- **Main POC Document**: `../Go_Custom_Attribute_POC.md`
- **Methods Comparison**: `../Methods.md`
- **Why Active Span Enrichment Fails**: `NotPossible.md`

## License

This is a proof-of-concept demonstration project.

