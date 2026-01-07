# OpenTelemetry Decorator-Based Implementation (Method 1)

[![Python](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/)
[![OpenTelemetry](https://img.shields.io/badge/OpenTelemetry-1.28%2B-orange.svg)](https://opentelemetry.io/)
[![Port](https://img.shields.io/badge/port-5000-green.svg)](http://localhost:5000)

> **Method 1: Decorator-Based (Annotation) Instrumentation** - Automatic span creation using Python decorators

## 📋 Table of Contents

- [Overview](#-overview)
- [Key Features](#-key-features)
- [Quick Start](#-quick-start)
- [How It Works](#-how-it-works)
- [Project Structure](#-project-structure)
- [What Gets Captured](#-what-gets-captured)
- [Advantages](#-advantages)
- [API Documentation](#-api-documentation)
- [Troubleshooting](#-troubleshooting)

## 🎯 Overview

This project demonstrates **Method 1: Decorator-Based (Annotation) Instrumentation** - using decorators to create new spans for each service method.

This approach is similar to Java's `@WithSpan` annotation and provides automatic span creation with minimal code changes. It's ideal for service layer methods where you want to track individual operation durations and create a clear parent-child span hierarchy.

### Key Features

- ✅ **Decorator-based** - Uses `@tracer.start_as_current_span()` decorators
- ✅ **Creates NEW spans** - Each decorated method creates a child span
- ✅ **Simple nested hierarchy** - 2-3 levels of span nesting
- ✅ **OOP approach** - Pure object-oriented programming with instance methods
- ✅ **Automatic lifecycle** - Spans are automatically started and ended
- ✅ **Best for tracking** - Individual operation durations and service layer logic
- ✅ **Clean code** - Declarative syntax, minimal boilerplate

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- PostgreSQL running on localhost:5432
- Docker (for Jaeger)

### Step 1: Start Jaeger (if not running)

```bash
docker run -d --name jaeger \
  -e COLLECTOR_OTLP_ENABLED=true \
  -p 16686:16686 \
  -p 4317:4317 \
  -p 4318:4318 \
  jaegertracing/all-in-one:latest

# Verify Jaeger is running
docker ps | grep jaeger

# Access Jaeger UI at http://localhost:16686
```

### Step 2: Setup Database

```bash
# Connect to PostgreSQL
psql -U postgres

# Create database
CREATE DATABASE user_management;

# Exit
\q
```

The database schema will be automatically created when you run the application.

### Step 3: Create Virtual Environment

```bash
# Create virtual environment
python -m venv vOtelAnnotation

# Activate virtual environment
source vOtelAnnotation/bin/activate  # Linux/macOS
# OR
vOtelAnnotation\Scripts\activate     # Windows
```

### Step 4: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 5: Run the Application

```bash
python app.py
```

The application will start on `http://localhost:5000`

**Expected Output:**
```
 * Running on http://127.0.0.1:5000
 * Debug mode: on
OpenTelemetry instrumentation initialized
Service: PythonCustomAttributesAnnotation
```

### Step 6: Test the API

```bash
# Create a user
curl -X POST http://localhost:5000/api/users \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "email": "john@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "age": 30
  }'

# Get all users
curl http://localhost:5000/api/users

# Get specific user
curl http://localhost:5000/api/users/john_doe

# Update user
curl -X PUT http://localhost:5000/api/users/john_doe \
  -H "Content-Type: application/json" \
  -d '{"age": 31}'

# Delete user
curl -X DELETE http://localhost:5000/api/users/john_doe
```

### Step 7: View Traces in Jaeger

1. Open http://localhost:16686
2. In the **Service** dropdown, select: `PythonCustomAttributesAnnotation`
3. Click **"Find Traces"** button
4. Click on any trace to view details
5. Observe the **nested span hierarchy** with service method spans

**What you'll see:**
- HTTP span (auto-instrumented by Flask)
- Service method spans (created by decorators)
- Database spans (auto-instrumented by psycopg2)
- Custom attributes on each span

## Project Structure

```
otelannotation/
├── app.py              # Flask app with OpenTelemetry setup
├── otel_config.py      # OpenTelemetry configuration
├── services.py         # Business logic with decorator-based instrumentation
├── routes.py           # API routes
├── models.py           # Database models
├── database.py         # Database connection
├── config.py           # Application configuration
├── requirements.txt    # Python dependencies
└── OOP_APPROACH.md     # Detailed OOP implementation notes
```

## How It Works

### 1. Decorator Creates New Span

```python
# services.py
@tracer.start_as_current_span("user_service.validate_user_data")
def validate_user_data(self, data):
    """Decorator creates a NEW child span"""
    span = trace.get_current_span()  # Gets the span created by decorator
    span.set_attribute("apm.operation", "user_validation")
    span.set_attribute("apm.validation_type", "required_fields")
    
    # Validation logic
    errors = []
    if not data.get('username'):
        errors.append("username is required")
    
    span.set_attribute("apm.validation_passed", len(errors) == 0)
    span.set_attribute("apm.error_count", len(errors))
    
    return len(errors) == 0, errors
```

### 2. Nested Span Hierarchy

```python
@tracer.start_as_current_span("user_service.create_user_with_validation")
def create_user_with_validation(self, data):
    """Parent span"""
    span = trace.get_current_span()
    span.set_attribute("apm.operation", "create_user")
    
    # Child span 1 - created by decorator
    is_valid, errors = self.validate_user_data(data)
    
    # Child span 2 - created by decorator
    enriched_data = self.enrich_user_data(data)
    
    # Child span 3 - created by decorator
    user = self.persist_user(enriched_data)
    
    return user
```

### 3. OOP Approach

```python
class UserService:
    """User service with comprehensive OpenTelemetry instrumentation"""
    
    def __init__(self):
        """Initialize the UserService instance"""
        self.tracer = tracer
        self.service_name = "UserService"
    
    # All methods use 'self' - pure OOP
    @tracer.start_as_current_span("user_service.get_user")
    def get_user_by_username_enriched(self, username):
        # Method implementation
        pass
```

## What Gets Captured?

Each decorated method creates a **new span** with:

- ✅ Operation name (`apm.operation`)
- ✅ Service information (`apm.service`)
- ✅ Method parameters (`apm.username_requested`)
- ✅ Validation results (`apm.validation_passed`, `apm.error_count`)
- ✅ Data enrichment (`apm.full_name`, `apm.data_completeness_percent`)
- ✅ Operation results (`apm.user_found`, `apm.result`)
- ✅ Individual method durations (automatic via span timing)

## Advantages

| Aspect | Decorator-Based (This) | API-Based |
|--------|------------------------|-----------|
| Span Hierarchy | Nested (2-3 levels) | Flat |
| Method Timing | ✅ Individual timings | ❌ No separate timings |
| Service Layer Visibility | ✅ Excellent | ⚠️ Limited |
| Overhead | Medium | Lower |
| Best For | Service layer methods | Controllers/Routes |

## API Documentation

Swagger UI available at: http://localhost:5000/swagger

## 🐛 Troubleshooting

### Common Issues

#### 1. Port 5000 Already in Use

**Error:** `Address already in use`

**Solution:**
```bash
# Find process using port 5000
lsof -i :5000

# Kill the process
kill -9 <PID>

# Or change the port in config.py
```

#### 2. Database Connection Error

**Error:** `could not connect to server`

**Solution:**
```bash
# Check PostgreSQL status
sudo service postgresql status

# Start PostgreSQL
sudo service postgresql start

# Verify database exists
psql -U postgres -l | grep user_management
```

#### 3. Virtual Environment Not Activating

**Solution:**
```bash
# Remove old venv
rm -rf vOtelAnnotation

# Create new venv
python -m venv vOtelAnnotation

# Activate
source vOtelAnnotation/bin/activate

# Install dependencies
pip install -r requirements.txt
```

#### 4. Spans Not Appearing in Jaeger

**Solution:**
```bash
# Check Jaeger is running
docker ps | grep jaeger

# Check Jaeger logs
docker logs jaeger

# Restart Jaeger
docker restart jaeger

# Verify OTLP endpoint
curl http://localhost:4317
```

#### 5. Import Errors

**Error:** `ModuleNotFoundError: No module named 'opentelemetry'`

**Solution:**
```bash
# Ensure venv is activated
source vOtelAnnotation/bin/activate

# Reinstall dependencies
pip install -r requirements.txt

# Verify installation
pip list | grep opentelemetry
```

## 📊 Comparison with Other Methods

| Aspect | Method 1 (This) | Method 2 (API) | Method 3 (Manual) |
|--------|----------------|----------------|-------------------|
| Span Creation | ✅ Decorator | ❌ None | ✅ Context Manager |
| Span Count | Medium (3-4) | Low (2) | High (6+) |
| Hierarchy | Nested (2-3 levels) | Flat | Deep (5+ levels) |
| Overhead | Medium | **Lowest** | Highest |
| Code Complexity | Low | **Very Low** | High |
| Best For | Service methods | Controllers | Complex workflows |

See [../README.md](../README.md) for detailed comparison.

## 📚 References

- [Main Repository README](../README.md)
- [OpenTelemetry Python Documentation](https://opentelemetry.io/docs/languages/python/)
- [Complete Guide to All 3 Approaches](../docs/COMPLETE_GUIDE_ALL_3_APPROACHES.md)
- [Python Custom Attribute POC](../Python_Custom_Attribute_POC.md)

## 🔗 Related Projects

- [otelapi/](../otelapi/) - Method 2: API-Based implementation
- [oteltracer/](../oteltracer/) - Method 3: Manual Tracer implementation

---

**This implementation is production-ready and demonstrates best practices for decorator-based OpenTelemetry instrumentation in Python.**

