# OpenTelemetry API-Based Implementation (Method 2) ⭐

[![Python](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/)
[![OpenTelemetry](https://img.shields.io/badge/OpenTelemetry-1.28%2B-orange.svg)](https://opentelemetry.io/)
[![Port](https://img.shields.io/badge/port-5001-green.svg)](http://localhost:5001)
[![Recommended](https://img.shields.io/badge/status-RECOMMENDED-brightgreen.svg)](README.md)

> **Method 2: API-Based Span Enrichment** - The recommended approach for most use cases

## 📋 Table of Contents

- [Overview](#-overview)
- [Key Features](#-key-features)
- [Why This Method is Recommended](#-why-this-method-is-recommended)
- [Quick Start](#-quick-start)
- [How It Works](#-how-it-works)
- [MotadataDynamicInstrumentation Utility](#-motadatadynamicinstrumentation-utility)
- [Project Structure](#-project-structure)
- [What Gets Captured](#-what-gets-captured)
- [Advantages](#-advantages)
- [Troubleshooting](#-troubleshooting)

## 🎯 Overview

This project demonstrates **Method 2: API-Based Span Enrichment** - enriching existing auto-instrumented spans without creating new ones.

This is the **RECOMMENDED** approach for most applications because it provides the best balance of functionality, performance, and simplicity. It enriches existing spans created by auto-instrumentation (Flask, psycopg2) with custom business attributes.

### Key Features

- ✅ **NO decorators** - Pure API-based approach
- ✅ **NO new spans** - Enriches existing HTTP/DB spans
- ✅ **Flat span structure** - All attributes on auto-instrumented spans
- ✅ **Lowest overhead** - Minimal performance impact
- ✅ **Full attribute capture** - Parameters, instance vars, computed values, return values
- ✅ **Utility class included** - `MotadataDynamicInstrumentation` for safe attribute setting
- ✅ **Production-ready** - Null-safe, error-suppressing, type-safe

## ⭐ Why This Method is Recommended

1. **Minimal Performance Overhead** - No additional span creation
2. **Simplest Implementation** - Just call utility methods
3. **Flat Trace Structure** - Easy to query and analyze
4. **Lower Storage Costs** - Fewer spans = less storage
5. **High Throughput** - Perfect for high-traffic endpoints
6. **Easy to Maintain** - No complex span lifecycle management
7. **Flexible** - Add attributes anywhere in your code

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

### Step 3: Create Virtual Environment

```bash
# Create virtual environment
python -m venv vOtelApi

# Activate virtual environment
source vOtelApi/bin/activate  # Linux/macOS
# OR
vOtelApi\Scripts\activate     # Windows
```

### Step 4: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 5: Run the Application

```bash
python app.py
```

The application will start on `http://localhost:5001`

**Expected Output:**
```
 * Running on http://127.0.0.1:5001
 * Debug mode: on
OpenTelemetry instrumentation initialized
Service: PythonCustomAttributesAPI
```

### Step 6: Test the API

```bash
# Create a user
curl -X POST http://localhost:5001/api/users \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "email": "john@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "age": 30
  }'

# Get all users
curl http://localhost:5001/api/users

# Get specific user
curl http://localhost:5001/api/users/john_doe

# Update user
curl -X PUT http://localhost:5001/api/users/john_doe \
  -H "Content-Type: application/json" \
  -d '{"age": 31}'

# Delete user
curl -X DELETE http://localhost:5001/api/users/john_doe
```

### Step 7: View Traces in Jaeger

1. Open http://localhost:16686
2. In the **Service** dropdown, select: `PythonCustomAttributesAPI`
3. Click **"Find Traces"** button
4. Click on any trace to view details
5. Observe the **flat span structure** with all attributes on HTTP spans

**What you'll see:**
- HTTP span (auto-instrumented by Flask) with ALL custom attributes
- Database spans (auto-instrumented by psycopg2)
- NO additional service method spans (unlike Method 1)
- Clean, flat structure that's easy to query

## 📁 Project Structure

```
otelapi/
├── app.py                              # Flask app with OpenTelemetry setup
├── otel_config.py                      # OpenTelemetry configuration
├── services.py                         # Business logic with API-based instrumentation
├── routes.py                           # API routes with span enrichment
├── models.py                           # Database models
├── database.py                         # Database connection
├── config.py                           # Application configuration
├── requirements.txt                    # Python dependencies
├── schema.sql                          # Database schema
├── util/                               # Utility classes
│   ├── __init__.py
│   ├── MotadataDynamicInstrumentation.py  # ⭐ Main utility class
│   └── README.md                       # Utility documentation
└── README.md                           # This file
```

## 🔧 MotadataDynamicInstrumentation Utility

This project includes a powerful utility class that makes adding custom attributes safe and easy.

### Quick Example

```python
from otelapi.util.MotadataDynamicInstrumentation import MotadataDynamicInstrumentation

def create_user(username, email, age):
    # Add custom attributes - safe, simple, automatic
    MotadataDynamicInstrumentation.set("user.username", username)
    MotadataDynamicInstrumentation.set("user.email", email)
    MotadataDynamicInstrumentation.set("user.age", age)

    # Business logic...
    user = User.create(username, email, age)

    # Add result attributes
    MotadataDynamicInstrumentation.set("user.created", True)

    return user
```

### Features

- ✅ **Automatic `apm.` prefixing** - No need to add prefix manually
- ✅ **Null-safe** - Silently ignores None values
- ✅ **Error-suppressing** - Never crashes your application
- ✅ **Type-safe** - Supports all OpenTelemetry types
- ✅ **List support** - Methods for bool, int, float, and string lists

### Available Methods

```python
# Scalar values
MotadataDynamicInstrumentation.set("key", value)  # str, int, float, bool

# List values
MotadataDynamicInstrumentation.set_string_list("key", ["a", "b", "c"])
MotadataDynamicInstrumentation.set_int_list("key", [1, 2, 3])
MotadataDynamicInstrumentation.set_float_list("key", [1.1, 2.2, 3.3])
MotadataDynamicInstrumentation.set_bool_list("key", [True, False])
```

### Full Documentation

See [util/README.md](util/README.md) for complete documentation, examples, and best practices.

## How It Works

### 1. Auto-Instrumentation Creates Spans

```python
# otel_config.py
FlaskInstrumentor().instrument_app(app)  # HTTP spans
Psycopg2Instrumentor().instrument()      # DB spans
```

### 2. Routes Enrich HTTP Spans

```python
# routes.py
@user_bp.route('/users/<username>', methods=['GET'])
def get_user(username):
    span = trace.get_current_span()  # Get existing HTTP span
    if span and span.is_recording():
        span.set_attribute("apm.endpoint", "get_user")
        span.set_attribute("apm.username_param", username)
    
    user = user_service.get_user_by_username_enriched(username)
    return jsonify(user), 200
```

### 3. Services Enrich the Same Span

```python
# services.py
def get_user_by_username_enriched(self, username):
    span = trace.get_current_span()  # Same HTTP span
    if span and span.is_recording():
        span.set_attribute("apm.operation", "get_user")
        span.set_attribute("apm.service", "UserService")
    
    user = User.get_by_username(username)
    
    if span and span.is_recording():
        span.set_attribute("apm.user_found", user is not None)
    
    return user
```

## What Gets Captured?

All attributes are added to the **existing HTTP span**:

- ✅ Endpoint information (`apm.endpoint`, `apm.method`)
- ✅ Request parameters (`apm.username_param`)
- ✅ Business logic details (`apm.operation`, `apm.service`)
- ✅ Validation results (`apm.validation_passed`, `apm.error_count`)
- ✅ Data enrichment (`apm.full_name`, `apm.data_completeness_percent`)
- ✅ Operation results (`apm.user_found`, `apm.result`)
- ✅ Audit information (`apm.audit_trail`)

## Advantages Over Decorator-Based

| Aspect | API-Based (This) | Decorator-Based |
|--------|------------------|-----------------|
| Span Count | Lower | Higher |
| Overhead | Minimal | Slightly more |
| Trace Structure | Flat | Nested |
| Best For | Controllers | Service layer |

## API Documentation

Swagger UI available at: http://localhost:5000/swagger

## 🐛 Troubleshooting

### Common Issues

#### 1. Port 5001 Already in Use

**Error:** `Address already in use`

**Solution:**
```bash
# Find process using port 5001
lsof -i :5001

# Kill the process
kill -9 <PID>

# Or change the port in config.py
```

#### 2. Attributes Not Appearing in Jaeger

**Problem:** Custom attributes don't show up in traces

**Solutions:**

1. **Verify span is recording:**
   ```python
   from opentelemetry import trace

   span = trace.get_current_span()
   print(f"Span recording: {span.is_recording()}")  # Should be True
   ```

2. **Check auto-instrumentation:**
   ```python
   # In otel_config.py - ensure this is called
   FlaskInstrumentor().instrument_app(app)
   ```

3. **Verify utility import:**
   ```python
   from otelapi.util.MotadataDynamicInstrumentation import MotadataDynamicInstrumentation
   ```

#### 3. Database Connection Error

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

#### 4. Import Errors

**Error:** `ModuleNotFoundError: No module named 'opentelemetry'`

**Solution:**
```bash
# Ensure venv is activated
source vOtelApi/bin/activate

# Reinstall dependencies
pip install -r requirements.txt

# Verify installation
pip list | grep opentelemetry
```

#### 5. Jaeger Not Receiving Traces

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

## 📊 Comparison with Other Methods

| Aspect | Method 2 (This) ⭐ | Method 1 (Decorator) | Method 3 (Manual) |
|--------|-------------------|---------------------|-------------------|
| Span Creation | ❌ None | ✅ Decorator | ✅ Context Manager |
| Span Count | **Low (2)** | Medium (3-4) | High (6+) |
| Hierarchy | **Flat** | Nested (2-3) | Deep (5+) |
| Overhead | **Lowest** | Medium | Highest |
| Code Complexity | **Very Low** | Low | High |
| Best For | **Most use cases** | Service methods | Complex workflows |
| Recommended | **✅ YES** | ⚠️ Sometimes | ⚠️ Rarely |

See [../README.md](../README.md) for detailed comparison.

## 📚 References

- [Main Repository README](../README.md)
- [MotadataDynamicInstrumentation Utility](util/README.md)
- [OpenTelemetry Python Documentation](https://opentelemetry.io/docs/languages/python/)
- [Complete Guide to All 3 Approaches](../docs/COMPLETE_GUIDE_ALL_3_APPROACHES.md)
- [Python Custom Attribute POC](../Python_Custom_Attribute_POC.md)

## 🔗 Related Projects

- [otelannotation/](../otelannotation/) - Method 1: Decorator-Based implementation
- [oteltracer/](../oteltracer/) - Method 3: Manual Tracer implementation

---

**This is the RECOMMENDED implementation for most production use cases. It provides the best balance of functionality, performance, and simplicity.**

