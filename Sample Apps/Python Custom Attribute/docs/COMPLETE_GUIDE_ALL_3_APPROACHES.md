# OpenTelemetry Python: Complete Guide to All 3 Custom Attribute Approaches

> **Comprehensive Guide** - Understanding Decorator-Based, API-Based, and Manual Tracer Methods
> **Last Updated:** December 2024
> **OpenTelemetry Python Version:** 1.39.1+

---

## Table of Contents

1. [Overview](#overview)
2. [Method 1: Decorator-Based (Annotation)](#method-1-decorator-based-annotation)
3. [Method 2: API-Based (Span Enrichment)](#method-2-api-based-span-enrichment)
4. [Method 3: Manual Tracer (Context Manager)](#method-3-manual-tracer-context-manager)
5. [Side-by-Side Code Comparison](#side-by-side-code-comparison)
6. [Trace Structure Comparison](#trace-structure-comparison)
7. [Clear Differences Summary](#clear-differences-summary)
8. [When to Use Each Approach](#when-to-use-each-approach)
9. [Quick Start Guide](#quick-start-guide)

---

## Overview

This repository demonstrates **three different approaches** to adding custom attributes in OpenTelemetry Python instrumentation. All three methods use the same User Management API to show how each approach differs in implementation and resulting trace structure.

### The Three Methods

| Method | Approach | Creates New Spans? | Complexity | Port |
|--------|----------|-------------------|------------|------|
| **Method 1** | Decorator-Based | ✅ Yes | Simple (2-3 levels) | 5000 |
| **Method 2** | API-Based | ❌ No | Flat | 5001 |
| **Method 3** | Manual Tracer | ✅ Yes | Complex (5+ levels) | 5002 |

### Project Structure

```
.
├── otelannotation/          # Method 1: Decorator-Based
│   ├── README.md
│   ├── services.py          # Uses @tracer.start_as_current_span()
│   └── ...
├── otelapi/                 # Method 2: API-Based
│   ├── README.md
│   ├── services.py          # Uses trace.get_current_span()
│   └── ...
├── oteltracer/              # Method 3: Manual Tracer
│   ├── README.md
│   ├── services.py          # Uses context managers
│   └── ...
└── COMPLETE_GUIDE_ALL_3_APPROACHES.md  # This file
```

---

## Method 1: Decorator-Based (Annotation)

### 📍 Location: `otelannotation/`

### Overview

Uses **decorators** to automatically create new child spans for each service method. Similar to Java's `@WithSpan` annotation.

### Key Characteristics

- ✅ **Decorator:** `@tracer.start_as_current_span()`
- ✅ **Creates NEW spans** for each decorated method
- ✅ **Nested hierarchy** of 2-3 levels
- ✅ **OOP approach** with instance methods
- ✅ **Best for:** Service layer methods, tracking individual operation durations

### Implementation Example

```python
from opentelemetry import trace

tracer = trace.get_tracer(__name__)

class UserService:
    def __init__(self):
        self.tracer = tracer
        self.service_name = "UserService"

    @tracer.start_as_current_span("user_service.get_user")
    def get_user_by_username_enriched(self, username):
        """Decorator creates a NEW child span"""
        span = trace.get_current_span()  # Gets the span created by decorator

        # Add custom attributes
        span.set_attribute("apm.operation", "get_user_by_username")
        span.set_attribute("apm.username_requested", username)
        span.set_attribute("apm.service", "UserService")

        # Business logic
        user = User.get_by_username(username)

        # Add result attributes
        span.set_attribute("apm.user_found", user is not None)

        return user
```

### What Happens

1. Decorator creates a **NEW span** named `user_service.get_user`
2. This span becomes a **child** of the current HTTP span
3. Custom attributes are added to this new span
4. Span automatically closes when method returns

### Trace Structure

```
HTTP GET /api/users/john_doe
└── user_service.get_user (NEW span created by decorator)
    ├── apm.operation = "get_user_by_username"
    ├── apm.username_requested = "john_doe"
    ├── apm.service = "UserService"
    ├── apm.user_found = true
    └── DB Query (auto-instrumented)
```

### Advantages

✅ **Individual method timing** - Each method's duration is tracked separately
✅ **Clear service layer visibility** - Easy to see which service methods were called
✅ **Nested hierarchy** - Shows parent-child relationships between operations
✅ **Familiar pattern** - Similar to Java/C# annotation-based approaches

### Disadvantages

⚠️ **More spans** - Increases span volume and storage
⚠️ **Slightly higher overhead** - Creating spans has a small performance cost

---

## Method 2: API-Based (Span Enrichment)

### 📍 Location: `otelapi/`

### Overview

Uses **API calls** to enrich existing auto-instrumented spans without creating new ones. Adds custom attributes directly to HTTP/DB spans.

### Key Characteristics

- ✅ **NO decorators** - Pure API-based approach
- ✅ **NO new spans** - Enriches existing spans
- ✅ **Flat structure** - All attributes on HTTP/DB spans
- ✅ **Lower overhead** - Minimal performance impact
- ✅ **Best for:** Controllers, route handlers, adding business context

### Implementation Example

```python
from opentelemetry import trace

class UserService:
    def get_user_by_username_enriched(self, username):
        """Enriches existing HTTP span - NO new span created"""
        span = trace.get_current_span()  # Gets existing HTTP span

        # Check if span is valid and recording
        if span and span.is_recording():
            # Add custom attributes to existing span
            span.set_attribute("apm.operation", "get_user_by_username")
            span.set_attribute("apm.username_requested", username)
            span.set_attribute("apm.service", "UserService")

        # Business logic
        user = User.get_by_username(username)

        # Add result attributes
        if span and span.is_recording():
            span.set_attribute("apm.user_found", user is not None)

        return user
```

### What Happens

1. `trace.get_current_span()` retrieves the **existing HTTP span**
2. Custom attributes are added to this existing span
3. **NO new span is created**
4. All attributes appear on the HTTP span in Jaeger

### Trace Structure

```
HTTP GET /api/users/john_doe
├── apm.endpoint = "get_user"
├── apm.method = "GET"
├── apm.operation = "get_user_by_username"
├── apm.username_requested = "john_doe"
├── apm.service = "UserService"
├── apm.user_found = true
└── DB Query (auto-instrumented)
```

### Advantages

✅ **Lower span count** - Reduces storage and overhead
✅ **Minimal performance impact** - No span creation cost
✅ **Flat structure** - Simpler traces, easier to query
✅ **Best for high-throughput** - Performance-critical paths

### Disadvantages

⚠️ **No individual method timing** - Can't see duration of specific service methods
⚠️ **Less granular** - All attributes on one span
⚠️ **Requires span checks** - Must verify span is recording

---

## Method 3: Manual Tracer (Context Manager)

### 📍 Location: `oteltracer/`

### Overview

Uses **context managers** to manually create complex nested span hierarchies with full control over span lifecycle. Perfect for multi-step workflows.

### Key Characteristics

- ✅ **Context manager:** `with tracer.start_as_current_span()`
- ✅ **Creates complex hierarchies** - 5+ levels of nesting
- ✅ **Full lifecycle control** - Explicit span management
- ✅ **Rich telemetry** - Events and attributes at each step
- ✅ **Best for:** Multi-step workflows, complex business processes

### Implementation Example

```python
from opentelemetry import trace

tracer = trace.get_tracer(__name__)

class UserService:
    def get_user_with_validation(self, username):
        """Creates complex workflow with nested spans"""

        # Parent span - workflow level
        with tracer.start_as_current_span("user_workflow.get_user_validated") as workflow_span:
            workflow_span.set_attribute("workflow.type", "get_user_validated")
            workflow_span.set_attribute("workflow.username", username)
            workflow_span.add_event("Starting validated user retrieval")

            # Child span 1: Validate input
            with tracer.start_as_current_span("user_workflow.validate_input") as validate_span:
                validate_span.set_attribute("validation.field", "username")
                validate_span.set_attribute("validation.min_length", 3)

                is_valid = len(username) >= 3
                validate_span.set_attribute("validation.result", is_valid)
                validate_span.add_event("Input validation completed")

                if not is_valid:
                    workflow_span.set_attribute("workflow.result", "validation_failed")
                    return None

            # Child span 2: Fetch user from database
            with tracer.start_as_current_span("user_workflow.fetch_user") as fetch_span:
                fetch_span.set_attribute("db.operation", "SELECT")
                fetch_span.set_attribute("db.table", "users")
                fetch_span.add_event("Fetching user from database")

                user = User.get_by_username(username)

                fetch_span.set_attribute("db.found", user is not None)
                fetch_span.add_event("Database fetch completed")

            # Child span 3: Validate result
            with tracer.start_as_current_span("user_workflow.validate_result") as result_span:
                if user is None:
                    result_span.set_attribute("validation.result", "user_not_found")
                    result_span.add_event("User not found in database")
                    workflow_span.set_attribute("workflow.result", "not_found")
                    return None

                result_span.set_attribute("validation.result", "success")
                result_span.add_event("User found and validated")

            workflow_span.set_attribute("workflow.result", "success")
            workflow_span.add_event("Workflow completed successfully")
            return user
```

### What Happens

1. **Parent span** created for entire workflow
2. **Child spans** created for each step (validate, fetch, validate result)
3. Each span has its own **attributes and events**
4. Spans automatically close when exiting context manager
5. Creates a **deep hierarchy** showing workflow progression

### Trace Structure

```
HTTP GET /api/users/john_doe
└── user_workflow.get_user_validated (MANUAL parent span)
    ├── workflow.type = "get_user_validated"
    ├── workflow.username = "john_doe"
    ├── Event: "Starting validated user retrieval"
    │
    ├── user_workflow.validate_input (MANUAL child span 1)
    │   ├── validation.field = "username"
    │   ├── validation.min_length = 3
    │   ├── validation.result = true
    │   └── Event: "Input validation completed"
    │
    ├── user_workflow.fetch_user (MANUAL child span 2)
    │   ├── db.operation = "SELECT"
    │   ├── db.table = "users"
    │   ├── db.found = true
    │   ├── Event: "Fetching user from database"
    │   ├── Event: "Database fetch completed"
    │   └── DB Query (auto-instrumented)
    │
    ├── user_workflow.validate_result (MANUAL child span 3)
    │   ├── validation.result = "success"
    │   └── Event: "User found and validated"
    │
    └── Event: "Workflow completed successfully"
```

### Advantages

✅ **Step-by-step visibility** - See exactly which step succeeded/failed
✅ **Complex workflows** - Perfect for multi-step business processes
✅ **Rich context** - Events provide narrative of what happened
✅ **Full control** - Explicit span lifecycle management
✅ **Debugging** - Easy to identify which step caused issues

### Disadvantages

⚠️ **Most spans** - Highest span volume and storage
⚠️ **More code** - Requires explicit span management
⚠️ **Higher overhead** - Creating many spans has performance cost

---

## Side-by-Side Code Comparison

### Same Operation - Three Different Implementations

#### Scenario: Get User by Username

**Method 1: Decorator-Based**
```python
@tracer.start_as_current_span("user_service.get_user")
def get_user_by_username_enriched(self, username):
    span = trace.get_current_span()
    span.set_attribute("apm.operation", "get_user")
    span.set_attribute("apm.username", username)

    user = User.get_by_username(username)
    span.set_attribute("apm.user_found", user is not None)
    return user
```

**Method 2: API-Based**
```python
def get_user_by_username_enriched(self, username):
    span = trace.get_current_span()

    if span and span.is_recording():
        span.set_attribute("apm.operation", "get_user")
        span.set_attribute("apm.username", username)

    user = User.get_by_username(username)

    if span and span.is_recording():
        span.set_attribute("apm.user_found", user is not None)

    return user
```

**Method 3: Manual Tracer**
```python
def get_user_with_validation(self, username):
    with tracer.start_as_current_span("user_workflow.get_user") as span:
        span.set_attribute("workflow.type", "get_user")
        span.add_event("Starting user retrieval")

        with tracer.start_as_current_span("validate_input") as v_span:
            v_span.set_attribute("validation.field", "username")
            is_valid = len(username) >= 3
            v_span.set_attribute("validation.result", is_valid)
            if not is_valid:
                return None

        with tracer.start_as_current_span("fetch_user") as f_span:
            user = User.get_by_username(username)
            f_span.set_attribute("db.found", user is not None)

        span.add_event("User retrieval completed")
        return user
```

---

## Trace Structure Comparison

### Visual Comparison of Span Hierarchies

#### Method 1: Decorator-Based (Simple Nested)
```
📊 Total Spans: 3

HTTP GET /api/users/john_doe (auto-instrumented)
│
└── 📦 user_service.get_user (decorator-created)
    │   ├── apm.operation = "get_user"
    │   ├── apm.username = "john_doe"
    │   └── apm.user_found = true
    │
    └── 🗄️ DB SELECT users (auto-instrumented)
```

#### Method 2: API-Based (Flat)
```
📊 Total Spans: 2

HTTP GET /api/users/john_doe (auto-instrumented + enriched)
│   ├── apm.endpoint = "get_user"
│   ├── apm.method = "GET"
│   ├── apm.operation = "get_user"
│   ├── apm.username = "john_doe"
│   ├── apm.user_found = true
│   └── apm.result = "success"
│
└── 🗄️ DB SELECT users (auto-instrumented)
```

#### Method 3: Manual Tracer (Deep Nested)
```
📊 Total Spans: 6+

HTTP GET /api/users/john_doe (auto-instrumented)
│
└── 📦 user_workflow.get_user (manual parent)
    │   ├── workflow.type = "get_user"
    │   ├── Event: "Starting user retrieval"
    │   └── Event: "User retrieval completed"
    │
    ├── 🔍 validate_input (manual child 1)
    │   ├── validation.field = "username"
    │   ├── validation.result = true
    │   └── Event: "Validation completed"
    │
    ├── 🗄️ fetch_user (manual child 2)
    │   ├── db.found = true
    │   ├── Event: "Fetching from database"
    │   │
    │   └── 🗄️ DB SELECT users (auto-instrumented)
    │
    └── ✅ validate_result (manual child 3)
        ├── validation.result = "success"
        └── Event: "User validated"
```


---

## Clear Differences Summary

### 🎯 Quick Reference Table

| Feature | Method 1: Decorator | Method 2: API-Based | Method 3: Manual Tracer |
|---------|-------------------|-------------------|----------------------|
| **Syntax** | `@tracer.start_as_current_span()` | `trace.get_current_span()` | `with tracer.start_as_current_span()` |
| **Creates New Spans?** | ✅ Yes | ❌ No | ✅ Yes |
| **Span Hierarchy** | Simple (2-3 levels) | Flat (1 level) | Complex (5+ levels) |
| **Code Complexity** | Low | Very Low | High |
| **Performance Overhead** | Medium | Low | High |
| **Span Count** | Medium | Low | High |
| **Storage Impact** | Medium | Low | High |
| **Method Timing** | ✅ Individual | ❌ No | ✅ Individual + Steps |
| **Workflow Visibility** | ⚠️ Limited | ❌ None | ✅ Excellent |
| **Events Support** | ✅ Yes | ✅ Yes | ✅ Yes (heavily used) |
| **Best Use Case** | Service methods | Controllers/Routes | Multi-step workflows |
| **Similar To** | Java `@WithSpan` | .NET `Activity.Current` | Manual instrumentation |

### 📊 Detailed Comparison

#### 1. Span Creation

**Method 1 (Decorator-Based)**
- ✅ Automatically creates a new span when method is called
- ✅ Span name defined in decorator
- ✅ Span automatically becomes child of current span
- ⚠️ One span per decorated method

**Method 2 (API-Based)**
- ❌ Does NOT create new spans
- ✅ Retrieves existing span (HTTP, DB, etc.)
- ✅ Adds attributes to existing span
- ✅ Zero span creation overhead

**Method 3 (Manual Tracer)**
- ✅ Explicitly creates spans using context manager
- ✅ Full control over span name and hierarchy
- ✅ Can create multiple nested spans in one method
- ⚠️ Requires manual span management

#### 2. Code Structure

**Method 1 (Decorator-Based)**
```python
@tracer.start_as_current_span("span_name")
def my_method(self, param):
    span = trace.get_current_span()
    span.set_attribute("key", "value")
    # Business logic
```

**Method 2 (API-Based)**
```python
def my_method(self, param):
    span = trace.get_current_span()
    if span and span.is_recording():
        span.set_attribute("key", "value")
    # Business logic
```

**Method 3 (Manual Tracer)**
```python
def my_method(self, param):
    with tracer.start_as_current_span("span_name") as span:
        span.set_attribute("key", "value")
        # Business logic
```

#### 3. Trace Complexity

**Method 1 (Decorator-Based)**
- 📊 **Span Count:** Medium (1 span per decorated method)
- 🌳 **Hierarchy:** Simple tree (2-3 levels)
- 📈 **Storage:** Medium
- 🔍 **Debugging:** Good - can see which methods were called

**Method 2 (API-Based)**
- 📊 **Span Count:** Low (uses existing spans)
- 🌳 **Hierarchy:** Flat (all on HTTP/DB spans)
- 📈 **Storage:** Low
- 🔍 **Debugging:** Basic - all attributes on one span

**Method 3 (Manual Tracer)**
- 📊 **Span Count:** High (multiple spans per workflow)
- 🌳 **Hierarchy:** Deep tree (5+ levels)
- 📈 **Storage:** High
- 🔍 **Debugging:** Excellent - step-by-step visibility

#### 4. Performance Impact

**Method 1 (Decorator-Based)**
- ⚡ **Overhead:** Medium
- 💾 **Memory:** Medium (span objects created)
- 🚀 **Throughput:** Good for most applications
- ✅ **Recommended for:** Service layer methods

**Method 2 (API-Based)**
- ⚡ **Overhead:** Low (no span creation)
- 💾 **Memory:** Low (only attributes added)
- 🚀 **Throughput:** Best for high-traffic endpoints
- ✅ **Recommended for:** Performance-critical paths

**Method 3 (Manual Tracer)**
- ⚡ **Overhead:** High (many spans created)
- 💾 **Memory:** High (multiple span objects)
- 🚀 **Throughput:** Lower (but acceptable for workflows)
- ✅ **Recommended for:** Critical business workflows

#### 5. Use Case Fit

**Method 1 (Decorator-Based)**
- ✅ Service layer methods
- ✅ Business logic functions
- ✅ Reusable components
- ✅ When you need individual method timing
- ❌ Not ideal for simple getters/setters

**Method 2 (API-Based)**
- ✅ Route handlers / controllers
- ✅ Adding business context to HTTP requests
- ✅ High-throughput endpoints
- ✅ When span count matters
- ❌ Not ideal when you need method-level timing

**Method 3 (Manual Tracer)**
- ✅ Multi-step workflows (payment, order processing)
- ✅ Complex business processes
- ✅ When you need to track each step separately
- ✅ Async/concurrent operations
- ❌ Not ideal for simple CRUD operations

---

## When to Use Each Approach

### 🎯 Decision Tree

```
Do you need to track a multi-step workflow?
│
├─ YES → Use Method 3 (Manual Tracer)
│         Examples: Payment processing, order fulfillment, data pipelines
│
└─ NO → Do you need individual method timing?
         │
         ├─ YES → Use Method 1 (Decorator-Based)
         │         Examples: Service layer methods, business logic
         │
         └─ NO → Use Method 2 (API-Based)
                   Examples: Route handlers, adding context to HTTP spans
```

### ✅ Method 1: Decorator-Based - Use When

1. **Service Layer Methods**
   - You have distinct business operations
   - Each operation should be timed separately
   - Example: `UserService.create_user()`, `OrderService.process_order()`

2. **Reusable Components**
   - Methods called from multiple places
   - Need to see where time is spent
   - Example: `ValidationService.validate()`, `EnrichmentService.enrich()`

3. **Nested Business Logic**
   - Methods call other methods
   - Want to see the call hierarchy
   - Example: `create_user()` → `validate()` → `enrich()` → `persist()`

4. **Similar to Java/C# Patterns**
   - Team familiar with `@WithSpan` annotations
   - Want consistent approach across languages

### ✅ Method 2: API-Based - Use When

1. **Route Handlers / Controllers**
   - Adding business context to HTTP requests
   - Don't need separate spans for each method
   - Example: Adding user ID, tenant ID to HTTP span

2. **High-Throughput Endpoints**
   - Performance is critical
   - Want to minimize overhead
   - Example: Health checks, metrics endpoints

3. **Simple CRUD Operations**
   - Straightforward database operations
   - Don't need complex tracing
   - Example: `GET /users`, `POST /users`

4. **Reducing Span Volume**
   - Storage costs are a concern
   - Want simpler traces
   - Example: Microservices with high request volume

### ✅ Method 3: Manual Tracer - Use When

1. **Multi-Step Workflows**
   - Complex business processes with distinct steps
   - Need to track each step separately
   - Example: Payment processing (validate → authorize → capture → notify)

2. **Critical Business Logic**
   - Need detailed visibility into what happened
   - Debugging is important
   - Example: Order fulfillment, inventory management

3. **Async/Concurrent Operations**
   - Parallel processing
   - Need to track multiple branches
   - Example: Batch processing, fan-out operations

4. **Compliance/Audit Requirements**
   - Need detailed audit trail
   - Must track every step
   - Example: Financial transactions, healthcare workflows

---

## Quick Start Guide

### Prerequisites

1. **Python 3.8+** installed
2. **PostgreSQL** running on `localhost:5432`
3. **Jaeger** running on `localhost:4317` (OTLP) and `localhost:16686` (UI)

### Start Jaeger

```bash
docker run -d --name jaeger \
  -p 16686:16686 \
  -p 4317:4317 \
  jaegertracing/all-in-one:latest
```

### Run Each Method

#### Method 1: Decorator-Based (Port 5000)

```bash
cd otelannotation
source vOtelAnnotation/bin/activate
pip install -r requirements.txt
python app.py
```

**Service Name:** `PythonCustomAttributesAnnotation`
**URL:** http://localhost:5000

#### Method 2: API-Based (Port 5001)

```bash
cd otelapi
source vOtelApi/bin/activate
pip install -r requirements.txt
python app.py
```

**Service Name:** `PythonCustomAttributesAPI`
**URL:** http://localhost:5001

#### Method 3: Manual Tracer (Port 5002)

```bash
cd oteltracer
source vOtelTracerEnv/bin/activate
pip install -r requirements.txt
python app.py
```

**Service Name:** `PythonCustomAttributesTracer`
**URL:** http://localhost:5002

### Test the APIs

```bash
# Create a user (test all three methods)
curl -X POST http://localhost:5000/api/users \
  -H "Content-Type: application/json" \
  -d '{"username":"john_doe","email":"john@example.com","first_name":"John","last_name":"Doe","age":30}'

curl -X POST http://localhost:5001/api/users \
  -H "Content-Type: application/json" \
  -d '{"username":"jane_doe","email":"jane@example.com","first_name":"Jane","last_name":"Doe","age":28}'

curl -X POST http://localhost:5002/api/users \
  -H "Content-Type: application/json" \
  -d '{"username":"bob_smith","email":"bob@example.com","first_name":"Bob","last_name":"Smith","age":35}'

# Get all users
curl http://localhost:5000/api/users  # Method 1
curl http://localhost:5001/api/users  # Method 2
curl http://localhost:5002/api/users  # Method 3

# Get specific user
curl http://localhost:5000/api/users/john_doe   # Method 1
curl http://localhost:5001/api/users/jane_doe   # Method 2
curl http://localhost:5002/api/users/bob_smith  # Method 3
```

### View Traces in Jaeger

1. Open **Jaeger UI:** http://localhost:16686
2. Select service from dropdown:
   - `PythonCustomAttributesAnnotation` (Method 1)
   - `PythonCustomAttributesAPI` (Method 2)
   - `PythonCustomAttributesTracer` (Method 3)
3. Click **"Find Traces"**
4. Click on a trace to see the span hierarchy
5. **Compare** the different span structures!

---

## Key Takeaways

### 🎯 The Bottom Line

**All three methods can capture the same data** (parameters, instance variables, computed values, return values).

**The difference is HOW the data is organized in traces:**

- **Method 1 (Decorator)** = Creates NEW spans → Nested hierarchy → Individual method timing
- **Method 2 (API-Based)** = Enriches EXISTING spans → Flat structure → Lower overhead
- **Method 3 (Manual Tracer)** = Creates COMPLEX hierarchies → Step-by-step visibility → Full control

### 💡 Best Practices

1. **Mix and Match** - Use different methods in different parts of your application
   - Method 2 for controllers
   - Method 1 for service layer
   - Method 3 for critical workflows

2. **Start Simple** - Begin with Method 2, add Method 1 where needed, use Method 3 sparingly

3. **Monitor Overhead** - Track span volume and adjust approach based on performance

4. **Consistent Naming** - Use consistent attribute names across all methods

5. **Document Decisions** - Document why you chose each approach for different components

### 📚 Additional Resources

- **Main README:** [README.md](../README.md)
- **Detailed Comparison:** [docs/COMPARISON.md](docs/COMPARISON.md)
- **Complete Guide:** [docs/OpenTelemetry_Python_Custom_Attributes_Guide.md](docs/OpenTelemetry_Python_Custom_Attributes_Guide.md)
- **Method 1 README:** [otelannotation/README.md](../otelannotation/README.md)
- **Method 2 README:** [otelapi/README.md](otelapi/README.md)
- **Method 3 README:** [oteltracer/README.md](../oteltracer/README.md)

### 🚀 Next Steps

1. Run all three implementations
2. Generate traces by calling the APIs
3. Compare the traces in Jaeger UI
4. Choose the approach that fits your needs
5. Implement in your own application

---

**Happy Tracing! 🎉**

