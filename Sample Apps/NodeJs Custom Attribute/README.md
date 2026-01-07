# OpenTelemetry Custom Attributes - Node.js POC

> **Proof of Concept demonstrating custom attribute injection strategies for OpenTelemetry in Node.js applications**

## 📋 Overview

This repository contains a comprehensive proof-of-concept (POC) demonstrating how to add custom business attributes to OpenTelemetry traces in Node.js applications. It includes two fully functional demo applications, each showcasing different OpenTelemetry instrumentation methods.

**Verified Environment:**
- Node.js v24.12
- OpenTelemetry API v1.9.0
- PostgreSQL v12+
- Last Verified: January 6, 2026

## 🎯 Project Structure

```
NodeJs Custom Attribute/
├── otelapi/                    # Method 1: Active Span Enrichment Demo
├── oteltracer/                 # Method 2: Manual Span Creation Demo
├── Testing Snapshots/          # Visual proof of working implementations
├── NodeJs_Custom_Attribute_POC.md       # Detailed POC documentation
├── THE_4_METHODS.md            # Comprehensive guide to all 4 methods
└── README.md                   # This file
```

## 🚀 Demo Applications

### 1. **otelapi** - Method 1: Active Span Enrichment
Demonstrates adding custom attributes to **existing spans** created by auto-instrumentation.

**Key Features:**
- ✅ Enriches auto-instrumented HTTP, Express, and PostgreSQL spans
- ✅ Utility class: `MotadataDynamicInstrumentation` for simplified attribute injection
- ✅ Automatic `apm.` prefix for all custom attributes
- ✅ Type-safe attribute handling (string, number, boolean, arrays)
- ✅ Null-safe implementation prevents runtime errors
- ✅ Test endpoints for data type validation

**Use Cases:**
- Adding business context to HTTP requests
- Enriching database query spans with user information
- Quick wins with minimal code changes

**Port:** 8080 (default)

### 2. **oteltracer** - Method 2: Manual Span Creation
Demonstrates creating **new custom spans** with full lifecycle control using the Tracer API.

**Key Features:**
- ✅ Full control over span creation, hierarchy, and lifecycle
- ✅ Service class: `TracerService` for centralized span management
- ✅ Support for span events, status codes, and exception recording
- ✅ Helper methods for common attribute patterns
- ✅ Nested span support for complex operations

**Use Cases:**
- Tracking custom business operations
- Creating detailed trace hierarchies
- Measuring specific code block performance
- Advanced instrumentation scenarios

**Port:** 8080 (default)

## 📚 Documentation

### Quick Start Guides
- **[NodeJs_Custom_Attribute_POC.md](./NodeJs_Custom_Attribute_POC.md)** - Detailed POC with implementation strategies
- **[THE_4_METHODS.md](./THE_4_METHODS.md)** - Comprehensive guide covering all 4 OpenTelemetry methods

### Application-Specific Documentation
- **[otelapi/README.md](./otelapi/README.md)** - Method 1 demo setup and usage
- **[oteltracer/README.md](./oteltracer/README.md)** - Method 2 demo setup and usage
- **[otelapi/docs/](./otelapi/docs/)** - Detailed OpenTelemetry documentation
- **[oteltracer/docs/](./oteltracer/docs/)** - Method 2 specific guides

## 🔧 Quick Start

### Prerequisites
- Node.js v14 or higher (tested on v24.12)
- PostgreSQL v12 or higher
- npm or yarn

### Setup Instructions

#### 1. Clone and Navigate
```bash
cd "NodeJs Custom Attribute"
```

#### 2. Choose Your Demo

**Option A: Method 1 (Active Span Enrichment)**
```bash
cd otelapi
npm install
cp .env.example .env
# Edit .env with your database credentials
psql -U your_user -d your_db -f db/init.sql
npm run dev
```

**Option B: Method 2 (Manual Span Creation)**
```bash
cd oteltracer
npm install
cp .env.example .env
# Edit .env with your database credentials
psql -U your_user -d your_db -f db/init.sql
npm run dev
```

#### 3. Access the Applications
- **API:** http://localhost:8080
- **Swagger UI:** http://localhost:8080/swagger
- **Health Check:** http://localhost:8080/health

## 🧪 Testing

Both applications include test endpoints to verify OpenTelemetry integration:

### otelapi (Method 1)
```bash
# Test data types
curl http://localhost:8080/datatypes/test

# Test custom attributes
curl http://localhost:8080/attributes/test

# CRUD operations with tracing
curl http://localhost:8080/users
```

### oteltracer (Method 2)
```bash
# CRUD operations with custom spans
curl http://localhost:8080/users
```

View traces in your observability backend (Jaeger, Zipkin, SigNoz, etc.)

## 📊 The 4 Methods Comparison

| Method | Span Created | Code Change | Best For | Complexity |
|--------|--------------|-------------|----------|------------|
| **1. Active Span Enrichment** | ❌ | Low | Business KPIs, user context | ⭐ Low |
| **2. Span Creation** | ✅ | High | Custom workflows, duration tracking | ⭐⭐ Medium |
| **3. Baggage Propagation** | ❌ | Medium | Distributed tracing, correlation IDs | ⭐⭐⭐ High |
| **4. SpanProcessor** | ❌ | None (SDK) | Environment metadata, global attributes | ⭐⭐ Medium |

See [THE_4_METHODS.md](./THE_4_METHODS.md) for detailed comparison and implementation guides.

## 🎓 Key Learnings

### ✅ Verified Capabilities
- All OpenTelemetry primitive types supported (string, number, boolean)
- Homogeneous arrays supported (string[], number[], boolean[])
- Both methods work seamlessly with auto-instrumentation
- Null-safe implementations prevent production issues
- Automatic attribute prefixing ensures consistency

### ⚠️ Important Notes
- Method 1 requires active spans (auto-instrumentation must be enabled)
- Method 2 requires manual span lifecycle management (always call `span.end()`)
- Avoid high-cardinality attributes (unique values per request)
- Use semantic conventions for standard attributes
- Namespace custom attributes (e.g., `apm.*`, `business.*`)

## 📸 Testing Snapshots

Visual proof of working implementations available in `Testing Snapshots/`:
- NodeJS Active Span Enrichment.png
- NodeJS Tracer based Span Creation.png

## 🤝 Contributing

This is a POC repository. For improvements or issues, please refer to the official OpenTelemetry documentation.

## 📖 Additional Resources

- [OpenTelemetry Official Docs](https://opentelemetry.io/docs/)
- [Node.js SDK Documentation](https://opentelemetry.io/docs/languages/js/)
- [Semantic Conventions](https://opentelemetry.io/docs/specs/semconv/)

## 📄 License

ISC

