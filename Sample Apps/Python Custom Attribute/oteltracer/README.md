# OpenTelemetry Manual Tracer Implementation (Method 3)

[![Python](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/)
[![OpenTelemetry](https://img.shields.io/badge/OpenTelemetry-1.28%2B-orange.svg)](https://opentelemetry.io/)
[![Port](https://img.shields.io/badge/port-5002-green.svg)](http://localhost:5002)

> **Method 3: Manual Tracer & Span Creation** - Full control over complex multi-step workflows

## 📋 Table of Contents

- [Overview](#-overview)
- [Key Features](#-key-features)
- [When to Use This Method](#-when-to-use-this-method)
- [Quick Start](#-quick-start)
- [Complex Workflows](#-complex-workflows)
- [How It Works](#-how-it-works)
- [Project Structure](#-project-structure)
- [What Gets Captured](#-what-gets-captured)
- [Advantages](#-advantages)
- [Troubleshooting](#-troubleshooting)

## 🎯 Overview

This project demonstrates **Method 3: Manual Tracer & Span Creation** - providing full control over span lifecycle with complex multi-step workflows.

This approach is ideal for critical business processes that require detailed step-by-step visibility, such as payment processing, order fulfillment, or data pipelines. It creates deep span hierarchies (5+ levels) with rich telemetry at each step.

### Key Features

- ✅ **Manual span creation** - `tracer.start_as_current_span()` context manager
- ✅ **Complex nested hierarchies** - Multi-level span trees (5+ levels deep)
- ✅ **Full lifecycle control** - Explicit span management with Python's `with` statement
- ✅ **Rich telemetry** - Events and attributes at each workflow step
- ✅ **Perfect for workflows** - Multi-step business processes
- ✅ **Step-by-step tracking** - Identify exactly which step succeeded or failed
- ✅ **Async support** - Works with Python's async/await

## 🎯 When to Use This Method

### ✅ Use Method 3 When:

- You have **complex multi-step workflows** (payment processing, order fulfillment)
- You need **detailed visibility** into each step of a process
- You require **step-by-step error tracking** to identify failure points
- You're implementing **critical business logic** that needs comprehensive monitoring
- You need **custom span hierarchies** with specific parent-child relationships
- You're working with **async/concurrent operations**
- You need **compliance/audit trails** with detailed operation logs

### ❌ Don't Use Method 3 When:

- You have simple CRUD operations
- You need minimal overhead (use Method 2 instead)
- You're working with high-frequency, low-latency endpoints
- Your operations are single-step without complex logic

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
python -m venv vOtelTracerEnv

# Activate virtual environment
source vOtelTracerEnv/bin/activate  # Linux/macOS
# OR
vOtelTracerEnv\Scripts\activate     # Windows
```

### Step 4: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 5: Run the Application

```bash
python app.py
```

The application will start on `http://localhost:5002`

**Expected Output:**
```
 * Running on http://127.0.0.1:5002
 * Debug mode: on
OpenTelemetry instrumentation initialized
Service: PythonCustomAttributesTracer
```

### Step 6: Test the API

Each endpoint demonstrates a different complex workflow:

```bash
# Create a user (5-step workflow)
curl -X POST http://localhost:5002/api/users \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "email": "john@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "age": 30
  }'

# Get all users (3-step workflow with stats)
curl http://localhost:5002/api/users

# Get specific user (3-step validation workflow)
curl http://localhost:5002/api/users/john_doe

# Update user (5-step change tracking workflow)
curl -X PUT http://localhost:5002/api/users/john_doe \
  -H "Content-Type: application/json" \
  -d '{"age": 31}'

# Delete user (4-step backup & cleanup workflow)
curl -X DELETE http://localhost:5002/api/users/john_doe
```

### Step 7: View Traces in Jaeger

1. Open http://localhost:16686
2. In the **Service** dropdown, select: `PythonCustomAttributesTracer`
3. Click **"Find Traces"** button
4. Click on any trace to view details
5. Observe the **deep span hierarchies** with multiple nested levels

**What you'll see:**
- HTTP span (auto-instrumented by Flask)
- Workflow root span (manually created)
- Multiple step spans (5+ levels deep)
- Events marking workflow progress
- Detailed attributes at each step
- Clear parent-child relationships

## Project Structure

```
oteltracer/
├── app.py                      # Flask app with OpenTelemetry setup
├── otel_config.py              # OpenTelemetry configuration
├── services.py                 # Complex workflows with manual tracer
├── routes.py                   # API routes
├── models.py                   # Database models
├── database.py                 # Database connection
├── config.py                   # Application configuration
├── requirements.txt            # Python dependencies
└── MANUAL_TRACER_APPROACH.md   # Detailed documentation
```

## Complex Workflows

### 1. Create User (5 Steps)
```
user_workflow.create_user
├── validate_required_fields
├── validate_data_types
├── enrich_user_data
├── persist_to_db
└── post_creation_tasks
```

### 2. Update User (5 Steps)
```
user_workflow.update_user
├── fetch_existing
├── detect_changes
├── validate_changes
├── apply_updates
└── audit_changes
```

### 3. Delete User (4 Steps)
```
user_workflow.delete_user
├── validate_deletion
├── backup_user_data
├── delete_from_db
└── cleanup_tasks
```

### 4. Get All Users (3 Steps)
```
user_workflow.get_all_users
├── fetch_from_db
├── enrich_data
└── calculate_stats
```

### 5. Get User with Validation (3 Steps)
```
user_workflow.get_user_validated
├── validate_input
├── fetch_user
└── validate_result
```

## How It Works

### Manual Span Creation

```python
# Get tracer instance (module level)
from opentelemetry import trace
tracer = trace.get_tracer(__name__)

# Create parent span
with tracer.start_as_current_span("user_workflow.create_user") as parent:
    parent.set_attribute("workflow.type", "create_user")
    parent.add_event("Workflow started")
    
    # Create child span 1
    with tracer.start_as_current_span("user_workflow.validate") as child1:
        child1.set_attribute("validation.type", "required_fields")
        # Validation logic
        child1.add_event("Validation completed")
    
    # Create child span 2
    with tracer.start_as_current_span("user_workflow.persist") as child2:
        child2.set_attribute("db.operation", "INSERT")
        # Database logic
        child2.add_event("Persisted successfully")
    
    parent.set_attribute("workflow.result", "success")
    parent.add_event("Workflow completed")
```

## What Gets Captured?

Each workflow step captures:

- ✅ **Step-specific attributes** - Operation type, validation results, etc.
- ✅ **Events** - Start/completion events for each step
- ✅ **Errors** - Validation failures, database errors
- ✅ **Computed values** - Change detection, statistics
- ✅ **Audit information** - Backup data, change logs

## Advantages Over Other Methods

| Aspect | Manual Tracer (This) | API-Based | Annotation-Based |
|--------|---------------------|-----------|------------------|
| Span Hierarchy | Deep (5+ levels) | Flat | Simple (2-3 levels) |
| Workflow Visibility | Excellent | None | Good |
| Step-by-Step Tracking | ✅ Yes | ❌ No | ⚠️ Limited |
| Debugging | Easy | Hard | Medium |
| Overhead | Higher | Lower | Medium |

## When to Use This Approach

✅ **Complex multi-step workflows** - Payment processing, order fulfillment  
✅ **Need to track each step separately** - Identify which step failed  
✅ **Async/concurrent operations** - Parallel processing  
✅ **Critical business logic** - Need detailed visibility  
✅ **Custom span hierarchies** - Specific parent-child relationships  

## API Documentation

Swagger UI available at: http://localhost:5000/swagger

## 🐛 Troubleshooting

### Common Issues

#### 1. Port 5002 Already in Use

**Error:** `Address already in use`

**Solution:**
```bash
# Find process using port 5002
lsof -i :5002

# Kill the process
kill -9 <PID>

# Or change the port in config.py
```

#### 2. Too Many Spans / Overwhelming Traces

**Problem:** Traces are too complex to navigate

**Solution:**
```python
# Reduce span depth for less critical operations
# Only use deep hierarchies for critical workflows

# Example: Conditional instrumentation
if is_critical_transaction(amount):
    with tracer.start_as_current_span("detailed_workflow"):
        # Detailed instrumentation
        pass
else:
    # Simple processing without extra spans
    pass
```

#### 3. Orphan Spans

**Problem:** Spans not properly nested

**Solution:**
```python
# Always use context managers (with statement)
# This ensures proper span lifecycle

# ✅ CORRECT
with tracer.start_as_current_span("parent") as parent:
    with tracer.start_as_current_span("child") as child:
        # Child is properly nested under parent
        pass

# ❌ WRONG - Don't manually manage spans
span = tracer.start_span("parent")
# ... code ...
span.end()  # Easy to forget or miss on exceptions
```

#### 4. Database Connection Error

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

#### 5. Import Errors

**Error:** `ModuleNotFoundError: No module named 'opentelemetry'`

**Solution:**
```bash
# Ensure venv is activated
source vOtelTracerEnv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt

# Verify installation
pip list | grep opentelemetry
```

## 📊 Comparison with Other Methods

| Aspect | Method 3 (This) | Method 1 (Decorator) | Method 2 (API) ⭐ |
|--------|----------------|---------------------|-------------------|
| Span Creation | ✅ Context Manager | ✅ Decorator | ❌ None |
| Span Count | **High (6+)** | Medium (3-4) | Low (2) |
| Hierarchy | **Deep (5+ levels)** | Nested (2-3) | Flat |
| Overhead | **Highest** | Medium | Lowest |
| Code Complexity | **High** | Low | Very Low |
| Workflow Visibility | **Excellent** | Limited | None |
| Best For | **Complex workflows** | Service methods | Most use cases |
| Recommended | ⚠️ Rarely | ⚠️ Sometimes | ✅ YES |

See [../README.md](../README.md) for detailed comparison.

## 📚 References

- [Main Repository README](../README.md)
- [OpenTelemetry Python Documentation](https://opentelemetry.io/docs/languages/python/)
- [Complete Guide to All 3 Approaches](../docs/COMPLETE_GUIDE_ALL_3_APPROACHES.md)
- [Python Custom Attribute POC](../Python_Custom_Attribute_POC.md)
- [FINDINGS Document](../FINDINGS_PYTHON_CUSTOM_ATTRIBUTES.md)

## 🔗 Related Projects

- [otelannotation/](../otelannotation/) - Method 1: Decorator-Based implementation
- [otelapi/](../otelapi/) - Method 2: API-Based implementation ⭐ RECOMMENDED

---

**This implementation demonstrates advanced OpenTelemetry patterns for complex multi-step workflows. Use it when you need detailed step-by-step visibility into critical business processes.**

