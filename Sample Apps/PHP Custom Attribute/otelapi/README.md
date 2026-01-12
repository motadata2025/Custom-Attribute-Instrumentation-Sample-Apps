# otelapi - Active Span Enrichment with OpenTelemetry

**Approach 1: API-Based Span Enrichment**

This project demonstrates how to add custom/business attributes to existing spans created by OpenTelemetry auto-instrumentation without creating new spans.

## 🎯 Overview

The **Active Span Enrichment** approach uses `Span::getCurrent()` to enrich spans that are already being tracked by OpenTelemetry's auto-instrumentation. This is the **recommended approach** for most use cases as it:

- ✅ Adds business context to existing traces
- ✅ Doesn't create visual noise in trace views
- ✅ Requires minimal code changes
- ✅ Works seamlessly with auto-instrumentation

## 🚀 Quick Start

### Prerequisites
- PHP 8.0 or higher
- PostgreSQL 12 or higher
- Composer

### Installation

1. **Install dependencies:**
   ```bash
   composer install
   ```

2. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your database credentials
   ```

3. **Setup database:**
   ```bash
   psql -U postgres -d postgres -f database/migrations/001_create_php_user_tbl.sql
   ```

4. **Start the server:**
   ```bash
   php -S localhost:8080 public/index.php
   ```

5. **Access the API:**
   - Swagger UI: http://localhost:8080/swagger
   - Health Check: http://localhost:8080/health
   - Datatype Test: http://localhost:8080/test/datatypes

## 📋 API Endpoints

### Health & Testing
- `GET /health` - Health check endpoint
- `GET /test/datatypes` - Test all OpenTelemetry supported datatypes

### User Management
- `GET /users` - Get all users (with optional filters)
- `GET /users/{id}` - Get user by ID
- `POST /users` - Create a new user
- `PUT /users/{id}` - Update a user
- `DELETE /users/{id}` - Delete a user

## 🧪 Testing OpenTelemetry Datatypes

The `/test/datatypes` endpoint demonstrates custom attribute injection with all supported datatypes:

**Scalar Types:**
- `bool` - Boolean values (true/false)
- `int` - Integer values (positive, negative, zero)
- `float` - Floating-point values
- `string` - String values (simple, empty, special characters)

**Array Types:**
- `bool[]` - Array of booleans
- `int[]` - Array of integers
- `float[]` - Array of floats
- `string[]` - Array of strings

### Example Request:
```bash
curl http://localhost:8080/test/datatypes
```

All custom attributes are prefixed with `apm.test.*` and will be visible in your OpenTelemetry traces.

## 💡 How It Works

### Active Span Enrichment Pattern

```php
use OpenTelemetry\API\Trace\Span;

// Get the current active span
$span = Span::getCurrent();

// Add custom attributes
if ($span->isRecording()) {
    $span->setAttribute('apm.user.id', $userId);
    $span->setAttribute('apm.operation.type', 'create_user');
    $span->setAttribute('apm.custom.data', $customData);
}
```

### Key Benefits:
1. **No new spans created** - Enriches existing HTTP/DB spans
2. **Clean traces** - No visual clutter in trace views
3. **Simple implementation** - Just a few lines of code
4. **Auto-instrumentation friendly** - Works with existing instrumentation

## 📊 Custom Attributes

All custom attributes in this project use the `apm.*` prefix for consistency:

- `apm.operation.type` - Type of operation (create, update, delete, etc.)
- `apm.user.id` - User identifier
- `apm.user.username` - Username
- `apm.user.email` - User email
- `apm.endpoint` - API endpoint
- `apm.http.method` - HTTP method
- `apm.result.count` - Result count for list operations
- `apm.test.*` - Test attributes for datatype validation

## 🏗️ Project Structure

```
otelapi/
├── composer.json           # Dependencies
├── .env.example           # Environment template
├── database/
│   └── migrations/        # Database migrations
├── public/
│   ├── index.php         # Application entry point
│   ├── openapi.json      # OpenAPI specification
│   └── swagger.html      # Swagger UI
└── src/
    ├── Config/           # Configuration classes
    ├── Controllers/      # API controllers
    │   ├── UserController.php
    │   └── DatatypeTestController.php
    ├── Models/           # Data models
    ├── Repositories/     # Data access layer
    └── Helpers/          # Helper utilities
```

## 🔧 Configuration

Edit `.env` file:

```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=postgres
DB_USER=postgres
DB_PASSWORD=postgres
PORT=8080
```

## 📖 Additional Resources

- [Main Project README](../README.md)
- [OpenTelemetry Methods Reference](../methods.md)
- [OpenTelemetry PHP Documentation](https://opentelemetry.io/docs/languages/php/)

## 📝 License

MIT

