# OpenTelemetry Python Custom Attributes - Complete Implementation Guide

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![OpenTelemetry](https://img.shields.io/badge/OpenTelemetry-1.28%2B-orange.svg)](https://opentelemetry.io/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

> **Comprehensive demonstration of three different approaches to adding custom business attributes in OpenTelemetry Python instrumentation**

This repository provides production-ready implementations of all three methods for injecting custom attributes into OpenTelemetry traces in Python applications. Each method is demonstrated using the same User Management API, making it easy to compare approaches and choose the right one for your use case.

## 📋 Table of Contents

- [Overview](#-overview)
- [Three Methods Implemented](#-three-methods-implemented)
- [Quick Start](#-quick-start)
- [Prerequisites](#-prerequisites)
- [Installation & Setup](#-installation--setup)
- [Testing the APIs](#-testing-the-apis)
- [Viewing Traces](#-viewing-traces-in-jaeger)
- [Key Differences](#-key-differences)
- [Architecture](#-architecture)
- [Documentation](#-documentation)
- [Troubleshooting](#-troubleshooting)
- [Contributing](#-contributing)

## 🎯 Overview

OpenTelemetry provides multiple ways to add custom business attributes to traces. This repository demonstrates all three approaches with working examples:

1. **Decorator-Based** - Automatic span creation with decorators
2. **API-Based** - Enriching existing spans without creating new ones
3. **Manual Tracer** - Full control over complex multi-step workflows

All implementations use:
- **Flask** web framework
- **PostgreSQL** database
- **OpenTelemetry** auto-instrumentation
- **Jaeger** for trace visualization
- **Flasgger** for Swagger UI

## 🎯 Three Methods Implemented

### Method 1: Decorator-Based (Annotation) - `otelannotation/`
**Best for: Service layer methods and tracking individual operation durations**

- ✅ Uses `@tracer.start_as_current_span()` decorators
- ✅ Creates NEW spans for each service method
- ✅ Simple nested hierarchy (2-3 levels)
- ✅ Object-oriented approach with instance methods
- ✅ Automatic span lifecycle management
- 🚀 **Port: 5000**
- 📊 **Span Count: Medium (3-4 spans)**

### Method 2: API-Based - `otelapi/` ⭐ **RECOMMENDED**
**Best for: Controllers, high-throughput endpoints, and minimal overhead**

- ✅ Uses `trace.get_current_span()` only
- ✅ NO decorators, NO new spans
- ✅ Enriches existing auto-instrumented spans
- ✅ Flat span structure, lowest overhead
- ✅ Includes `MotadataDynamicInstrumentation` utility class
- 🚀 **Port: 5001**
- 📊 **Span Count: Low (2 spans)**

### Method 3: Manual Tracer - `oteltracer/`
**Best for: Complex multi-step workflows and critical business processes**

- ✅ Uses `tracer.start_as_current_span()` context manager
- ✅ Creates complex nested span hierarchies (5+ levels)
- ✅ Full control over span lifecycle
- ✅ Perfect for multi-step workflows
- ✅ Rich telemetry with events and detailed attributes
- 🚀 **Port: 5002**
- 📊 **Span Count: High (6+ spans)**

## 📁 Project Structure

```
Python Custom Attribute/
├── docs/                                    # Comprehensive documentation
│   ├── COMPLETE_GUIDE_ALL_3_APPROACHES.md  # Complete guide to all methods
│   └── ...                                  # Additional guides
│
├── otelannotation/                          # Method 1: Decorator-Based
│   ├── app.py                               # Flask application
│   ├── services.py                          # Service layer with @decorators
│   ├── routes.py                            # API routes
│   ├── otel_config.py                       # OpenTelemetry configuration
│   ├── requirements.txt                     # Python dependencies
│   ├── schema.sql                           # Database schema
│   └── README.md                            # Method 1 documentation
│
├── otelapi/                                 # Method 2: API-Based ⭐
│   ├── app.py                               # Flask application
│   ├── services.py                          # Service layer with API calls
│   ├── routes.py                            # API routes
│   ├── otel_config.py                       # OpenTelemetry configuration
│   ├── util/                                # Utility classes
│   │   ├── MotadataDynamicInstrumentation.py  # Helper utility
│   │   └── README.md                        # Utility documentation
│   ├── requirements.txt                     # Python dependencies
│   ├── schema.sql                           # Database schema
│   └── README.md                            # Method 2 documentation
│
├── oteltracer/                              # Method 3: Manual Tracer
│   ├── app.py                               # Flask application
│   ├── services.py                          # Complex workflows with context managers
│   ├── routes.py                            # API routes
│   ├── otel_config.py                       # OpenTelemetry configuration
│   ├── requirements.txt                     # Python dependencies
│   ├── schema.sql                           # Database schema
│   └── README.md                            # Method 3 documentation
│
├── Testing Snapshots/                       # Screenshots of traces in Jaeger
│   ├── Python API-Based Span Enrichment.png
│   ├── Python Decorator-Based Instrumentation.png
│   └── Python Manual Tracer and Span Creation.png
│
├── FINDINGS_PYTHON_CUSTOM_ATTRIBUTES.md     # Detailed findings document
├── Python_Custom_Attribute_POC.md           # POC documentation
├── Java_Custom_Attribute_POC.md             # Java comparison reference
└── README.md                                # This file
```

## 🚀 Quick Start

### Prerequisites

Before you begin, ensure you have the following installed:

#### Required Software
- **Python 3.8+** (Tested with Python 3.12.3)
  ```bash
  python --version  # Should be 3.8 or higher
  ```

- **PostgreSQL** (Running on localhost:5432)
  ```bash
  # Install PostgreSQL
  # Ubuntu/Debian
  sudo apt-get install postgresql postgresql-contrib

  # macOS
  brew install postgresql

  # Start PostgreSQL
  sudo service postgresql start  # Linux
  brew services start postgresql  # macOS
  ```

- **Docker** (For running Jaeger)
  ```bash
  docker --version
  ```

#### Database Setup
Create the required database:
```bash
# Connect to PostgreSQL
psql -U postgres

# Create database
CREATE DATABASE user_management;

# Exit psql
\q
```

The database schema will be automatically created when you run each application.

## 🔧 Installation & Setup

### Step 1: Start Jaeger (Trace Backend)

Jaeger will collect and visualize your traces:

```bash
# Pull and run Jaeger all-in-one container
docker run -d --name jaeger \
  -e COLLECTOR_OTLP_ENABLED=true \
  -p 16686:16686 \
  -p 4317:4317 \
  -p 4318:4318 \
  jaegertracing/all-in-one:latest

# Verify Jaeger is running
docker ps | grep jaeger

# Access Jaeger UI
# Open http://localhost:16686 in your browser
```

**Ports:**
- `16686` - Jaeger UI
- `4317` - OTLP gRPC receiver
- `4318` - OTLP HTTP receiver

### Step 2: Choose and Run a Method

You can run all three methods simultaneously (they use different ports) or run them individually.

#### Method 1: Decorator-Based (Port 5000)

```bash
# Navigate to the project
cd otelannotation

# Create virtual environment (first time only)
python -m venv vOtelAnnotation

# Activate virtual environment
source vOtelAnnotation/bin/activate  # Linux/macOS
# OR
vOtelAnnotation\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Run the application
python app.py

# Application will start on http://localhost:5000
```

#### Method 2: API-Based (Port 5001) ⭐ **RECOMMENDED**

```bash
# Navigate to the project
cd otelapi

# Create virtual environment (first time only)
python -m venv vOtelApi

# Activate virtual environment
source vOtelApi/bin/activate  # Linux/macOS
# OR
vOtelApi\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Run the application
python app.py

# Application will start on http://localhost:5001
```

#### Method 3: Manual Tracer (Port 5002)

```bash
# Navigate to the project
cd oteltracer

# Create virtual environment (first time only)
python -m venv vOtelTracerEnv

# Activate virtual environment
source vOtelTracerEnv/bin/activate  # Linux/macOS
# OR
vOtelTracerEnv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Run the application
python app.py

# Application will start on http://localhost:5002
```

### Step 3: Verify Installation

Check that the application is running:

```bash
# Test the home endpoint
curl http://localhost:5000/  # Method 1
curl http://localhost:5001/  # Method 2
curl http://localhost:5002/  # Method 3

# Access Swagger UI
# Method 1: http://localhost:5000/swagger
# Method 2: http://localhost:5001/swagger
# Method 3: http://localhost:5002/swagger
```

## 🧪 Testing the APIs

All three implementations provide the same REST API endpoints. Test them to generate traces.

### API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/users` | Create a new user |
| GET | `/api/users` | Get all users |
| GET | `/api/users/<username>` | Get user by username |
| PUT | `/api/users/<username>` | Update user |
| DELETE | `/api/users/<username>` | Delete user |

### Example API Calls

#### Create a User

```bash
# Method 1: Decorator-Based (Port 5000)
curl -X POST http://localhost:5000/api/users \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "email": "john@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "age": 30
  }'

# Method 2: API-Based (Port 5001)
curl -X POST http://localhost:5001/api/users \
  -H "Content-Type: application/json" \
  -d '{
    "username": "jane_doe",
    "email": "jane@example.com",
    "first_name": "Jane",
    "last_name": "Doe",
    "age": 28
  }'

# Method 3: Manual Tracer (Port 5002)
curl -X POST http://localhost:5002/api/users \
  -H "Content-Type: application/json" \
  -d '{
    "username": "bob_smith",
    "email": "bob@example.com",
    "first_name": "Bob",
    "last_name": "Smith",
    "age": 35
  }'
```

#### Get All Users

```bash
curl http://localhost:5000/api/users  # Method 1
curl http://localhost:5001/api/users  # Method 2
curl http://localhost:5002/api/users  # Method 3
```

#### Get Specific User

```bash
curl http://localhost:5000/api/users/john_doe   # Method 1
curl http://localhost:5001/api/users/jane_doe   # Method 2
curl http://localhost:5002/api/users/bob_smith  # Method 3
```

#### Update User

```bash
curl -X PUT http://localhost:5000/api/users/john_doe \
  -H "Content-Type: application/json" \
  -d '{"age": 31}'
```

#### Delete User

```bash
curl -X DELETE http://localhost:5000/api/users/john_doe
```

### Using Swagger UI

Each application includes Swagger UI for interactive API testing:

- **Method 1:** http://localhost:5000/swagger
- **Method 2:** http://localhost:5001/swagger
- **Method 3:** http://localhost:5002/swagger

## 📊 Viewing Traces in Jaeger

### Access Jaeger UI

1. Open your browser and navigate to: **http://localhost:16686**

2. In the **Service** dropdown, select one of:
   - `PythonCustomAttributesAnnotation` (Method 1: Decorator-Based)
   - `PythonCustomAttributesAPI` (Method 2: API-Based)
   - `PythonCustomAttributesTracer` (Method 3: Manual Tracer)

3. Click **"Find Traces"** button

4. Click on any trace to view details

### What to Look For

#### Method 1: Decorator-Based
- **Span Count:** 3-4 spans per request
- **Hierarchy:** Nested structure (2-3 levels deep)
- **Spans:** HTTP span → Service method spans
- **Attributes:** Custom attributes on each service method span

#### Method 2: API-Based ⭐
- **Span Count:** 2 spans per request (lowest)
- **Hierarchy:** Flat structure
- **Spans:** HTTP span → Database span
- **Attributes:** All custom attributes on the HTTP span

#### Method 3: Manual Tracer
- **Span Count:** 6+ spans per request (highest)
- **Hierarchy:** Deep nested structure (5+ levels)
- **Spans:** HTTP span → Workflow span → Step spans
- **Attributes:** Detailed attributes and events on each step

### Comparing Traces

Run the same API call on all three methods and compare:

```bash
# Create user in all three methods
curl -X POST http://localhost:5000/api/users -H "Content-Type: application/json" -d '{"username":"test1","email":"test1@example.com","first_name":"Test","last_name":"One","age":25}'
curl -X POST http://localhost:5001/api/users -H "Content-Type: application/json" -d '{"username":"test2","email":"test2@example.com","first_name":"Test","last_name":"Two","age":26}'
curl -X POST http://localhost:5002/api/users -H "Content-Type: application/json" -d '{"username":"test3","email":"test3@example.com","first_name":"Test","last_name":"Three","age":27}'

# Now compare the traces in Jaeger UI
```

### Screenshots

See the `Testing Snapshots/` folder for example trace visualizations:
- `Python Decorator-Based Instrumentation.png`
- `Python API-Based Span Enrichment.png`
- `Python Manual Tracer and Span Creation.png`

## 🔍 Key Differences

### Detailed Comparison Table

| Aspect | Method 1: Decorator | Method 2: API ⭐ | Method 3: Manual Tracer |
|--------|---------------------|------------------|-------------------------|
| **Span Creation** | ✅ Decorator | ❌ None | ✅ Context Manager |
| **Span Count** | Medium (3-4) | Low (2) | High (6+) |
| **Hierarchy Depth** | Simple (2-3 levels) | Flat (1 level) | Deep (5+ levels) |
| **Control Level** | Medium | Low | Full |
| **Code Complexity** | Low | Very Low | High |
| **Performance Overhead** | Medium | **Lowest** | Highest |
| **Storage Impact** | Medium | **Lowest** | Highest |
| **Method Timing** | ✅ Individual | ❌ No | ✅ Step-by-step |
| **Workflow Visibility** | ⚠️ Limited | ❌ None | ✅ Excellent |
| **Best For** | Service methods | Controllers & APIs | Complex workflows |
| **Use Case** | Standard operations | High-throughput | Multi-step processes |
| **Learning Curve** | Easy | **Easiest** | Moderate |
| **Maintenance** | Easy | **Easiest** | Requires discipline |
| **Similar To (Java)** | `@WithSpan` | `Span.current()` | Manual Tracer |

### When to Use Each Method

#### ✅ Use Method 1 (Decorator-Based) When:
- You want to track individual service method durations
- You need a clear parent-child span hierarchy
- You're instrumenting reusable service layer components
- You want automatic span lifecycle management
- Your team is familiar with decorator patterns

#### ⭐ Use Method 2 (API-Based) When:
- You need minimal performance overhead
- You're working with high-throughput endpoints
- You want to add business context to HTTP requests
- You don't need separate spans for each method
- You want the simplest implementation
- **This is the RECOMMENDED approach for most use cases**

#### 🔧 Use Method 3 (Manual Tracer) When:
- You have complex multi-step workflows (payment processing, order fulfillment)
- You need detailed visibility into each step
- You require step-by-step error tracking
- You're implementing critical business logic
- You need custom span hierarchies
- You're working with async/concurrent operations

## 🏗️ Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Client (curl/browser)                    │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    Flask Application                         │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  OpenTelemetry Auto-Instrumentation                  │  │
│  │  - FlaskInstrumentor (HTTP spans)                    │  │
│  │  - Psycopg2Instrumentor (DB spans)                   │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Routes     │→ │   Services   │→ │   Models     │     │
│  │ (API Layer)  │  │ (Business    │  │ (Database)   │     │
│  │              │  │  Logic)      │  │              │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│         │                  │                  │             │
│         ▼                  ▼                  ▼             │
│  Custom Attributes   Custom Attributes   Auto-instrumented │
└─────────────────────────────┬─────────────────────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │  OTLP Exporter   │
                    │  (gRPC/HTTP)     │
                    └─────────┬────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │  Jaeger Backend  │
                    │  - Collector     │
                    │  - Storage       │
                    │  - UI            │
                    └──────────────────┘
```

### Data Flow

1. **Request arrives** → Flask auto-instrumentation creates HTTP span
2. **Route handler** → Adds custom attributes (Method 2) or creates spans (Method 1, 3)
3. **Service layer** → Business logic with custom instrumentation
4. **Database call** → Auto-instrumentation creates DB span
5. **Response sent** → Span ends, trace exported to Jaeger

## 📚 Documentation

### Main Documentation

- **[README.md](README.md)** - This file (overview and quick start)
- **[FINDINGS_PYTHON_CUSTOM_ATTRIBUTES.md](FINDINGS_PYTHON_CUSTOM_ATTRIBUTES.md)** - Detailed findings and analysis
- **[Python_Custom_Attribute_POC.md](Python_Custom_Attribute_POC.md)** - Proof of Concept documentation
- **[Java_Custom_Attribute_POC.md](Java_Custom_Attribute_POC.md)** - Java comparison reference

### Method-Specific Documentation

- **[otelannotation/README.md](otelannotation/README.md)** - Method 1: Decorator-Based
- **[otelapi/README.md](otelapi/README.md)** - Method 2: API-Based
- **[otelapi/util/README.md](otelapi/util/README.md)** - MotadataDynamicInstrumentation utility
- **[oteltracer/README.md](oteltracer/README.md)** - Method 3: Manual Tracer

### Comprehensive Guides

- **[docs/COMPLETE_GUIDE_ALL_3_APPROACHES.md](docs/COMPLETE_GUIDE_ALL_3_APPROACHES.md)** - Complete guide to all methods

## 🎓 What You'll Learn

By exploring this repository, you will learn:

- ✅ **Three different approaches** to adding custom attributes in OpenTelemetry Python
- ✅ **When to use each method** based on your use case
- ✅ **Span hierarchy differences** and their impact on trace visualization
- ✅ **Performance trade-offs** between different approaches
- ✅ **Best practices** for each instrumentation method
- ✅ **How to use OpenTelemetry** with Flask and PostgreSQL
- ✅ **Trace visualization** in Jaeger
- ✅ **Production-ready patterns** for custom instrumentation

## 🛠️ Technologies Used

| Technology | Version | Purpose |
|------------|---------|---------|
| **Python** | 3.8+ | Programming language |
| **Flask** | 3.0.0 | Web framework |
| **PostgreSQL** | Latest | Database |
| **OpenTelemetry API** | 1.28.2+ | Tracing API |
| **OpenTelemetry SDK** | 1.28.2+ | Tracing SDK |
| **OpenTelemetry Instrumentation** | 0.49b2+ | Auto-instrumentation |
| **Jaeger** | Latest | Trace backend and visualization |
| **Flasgger** | 0.9.7.1 | Swagger UI |
| **psycopg2-binary** | 2.9.9 | PostgreSQL adapter |

## 🐛 Troubleshooting

### Common Issues

#### 1. Port Already in Use

**Error:** `Address already in use`

**Solution:**
```bash
# Find process using the port
lsof -i :5000  # or :5001, :5002

# Kill the process
kill -9 <PID>

# Or change the port in config.py
```

#### 2. Database Connection Error

**Error:** `could not connect to server: Connection refused`

**Solution:**
```bash
# Check if PostgreSQL is running
sudo service postgresql status

# Start PostgreSQL
sudo service postgresql start

# Verify database exists
psql -U postgres -l | grep user_management

# Create database if missing
psql -U postgres -c "CREATE DATABASE user_management;"
```

#### 3. Jaeger Not Receiving Traces

**Error:** No traces appearing in Jaeger UI

**Solution:**
```bash
# Check if Jaeger is running
docker ps | grep jaeger

# Check Jaeger logs
docker logs jaeger

# Verify OTLP port is accessible
curl http://localhost:4317

# Restart Jaeger
docker restart jaeger
```

#### 4. Module Import Errors

**Error:** `ModuleNotFoundError: No module named 'opentelemetry'`

**Solution:**
```bash
# Ensure virtual environment is activated
source vOtelApi/bin/activate  # or appropriate venv

# Reinstall dependencies
pip install -r requirements.txt

# Verify installation
pip list | grep opentelemetry
```

#### 5. Virtual Environment Issues

**Error:** Virtual environment not activating

**Solution:**
```bash
# Remove old virtual environment
rm -rf vOtelApi  # or appropriate venv name

# Create new virtual environment
python -m venv vOtelApi

# Activate and install
source vOtelApi/bin/activate
pip install -r requirements.txt
```

### Getting Help

If you encounter issues not covered here:

1. Check the method-specific README files
2. Review the detailed documentation in `docs/`
3. Check Jaeger logs: `docker logs jaeger`
4. Check application logs in the terminal
5. Verify all prerequisites are installed

## 📝 License

This is a demonstration project for learning OpenTelemetry instrumentation patterns.

## 🤝 Contributing

This repository is for educational purposes. Feel free to:

- Fork the repository
- Experiment with different instrumentation approaches
- Add new examples
- Improve documentation
- Share your findings

## 📞 Support

For questions or issues:

- Review the comprehensive documentation in `docs/`
- Check the troubleshooting section above
- Refer to [OpenTelemetry Python Documentation](https://opentelemetry.io/docs/languages/python/)

## 🔗 Related Resources

- **OpenTelemetry Official Docs:** https://opentelemetry.io/docs/
- **OpenTelemetry Python:** https://opentelemetry.io/docs/languages/python/
- **Jaeger Documentation:** https://www.jaegertracing.io/docs/
- **Flask Documentation:** https://flask.palletsprojects.com/

---

**Made with ❤️ for the OpenTelemetry community**

