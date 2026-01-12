# PHP OpenTelemetry Custom Attributes Demo

This repository contains **two independent PHP applications** demonstrating different approaches to adding custom attributes and observability to your applications using OpenTelemetry.

## 📁 Projects Overview

### 1. **otelapi** - Active Span Enrichment
**Package:** `otelapi/user-management-api`  
**Port:** `8080`  
**Approach:** Active Span Enrichment (Recommended)

Demonstrates how to add custom attributes to **existing spans** created by OpenTelemetry auto-instrumentation. This is the **recommended approach** for most use cases.

**Key Features:**
- ✅ No new spans created
- ✅ Adds business metadata to existing spans
- ✅ Zero visual noise in traces
- ✅ Simple and clean implementation
- ✅ Uses `Span::getCurrent()` to enrich active spans

**Use Cases:**
- Adding user IDs, tenant IDs, or business context to traces
- Enriching HTTP request spans with custom metadata
- Adding application-specific attributes without creating new spans
- Testing all OpenTelemetry supported datatypes (bool, int, float, string, arrays)

**Special Endpoints:**
- `GET /test/datatypes` - Tests all supported OpenTelemetry attribute datatypes

[📖 Read otelapi Documentation](./otelapi/README.md)

---

### 2. **oteltracer** - Manual Tracing & Custom Spans
**Package:** `oteltracer/user-management-tracer`  
**Port:** `8082`  
**Approach:** Manual Tracing with Custom Spans

Demonstrates how to create **custom spans** manually for detailed observability and complex tracing scenarios.

**Key Features:**
- ✅ Full control over span lifecycle
- ✅ Create custom spans for specific operations
- ✅ Detailed observability for complex workflows
- ✅ Parent-child span relationships
- ✅ Custom span names and attributes

**Use Cases:**
- Background job processing
- Complex multi-step workflows
- Service-to-service communication
- Performance profiling of specific code blocks

[📖 Read oteltracer Documentation](./oteltracer/README.md)

---

## 🚀 Quick Start

### Prerequisites
- PHP 8.0 or higher
- PostgreSQL 12 or higher
- Composer

### Running Both Applications

1. **Start otelapi (Active Span Enrichment)**
   ```bash
   cd otelapi
   composer install --no-dev
   php -S localhost:8080 public/index.php
   ```
   Access at: http://localhost:8080

2. **Start oteltracer (Manual Tracing)**
   ```bash
   cd oteltracer
   composer install --no-dev
   php -S localhost:8082 public/index.php
   ```
   Access at: http://localhost:8082

### Test the APIs

```bash
# Test otelapi health
curl http://localhost:8080/health

# Test otelapi datatype support
curl http://localhost:8080/test/datatypes

# Test oteltracer health
curl http://localhost:8082/health
```

---

## 📊 Comparison

| Feature | **otelapi** (Active Span) | **oteltracer** (Manual Tracing) |
|---------|---------------------------|----------------------------------|
| **Complexity** | Low | Medium-High |
| **Span Creation** | Uses existing spans | Creates new spans |
| **Visual Noise** | Minimal | Can be significant |
| **Use Case** | Adding metadata | Complex workflows |
| **Recommended For** | Most applications | Advanced scenarios |
| **Learning Curve** | Easy | Moderate |

---

## 🎯 Which Approach Should You Use?

### Use **Active Span Enrichment** (otelapi) when:
- ✅ You want to add business context to existing traces
- ✅ You're using auto-instrumentation
- ✅ You want minimal code changes
- ✅ You want clean, simple traces

### Use **Manual Tracing** (oteltracer) when:
- ✅ You need fine-grained control over spans
- ✅ You're tracing complex, multi-step workflows
- ✅ You need custom parent-child relationships
- ✅ You're building background job systems

---

## 📚 Project Structure

```
PHP Custom Attribute/
├── README.md                 # This file
├── methods.md                # OpenTelemetry methods reference
├── otelapi/                  # Active Span Enrichment project
│   ├── composer.json         # Independent dependencies
│   ├── vendor/               # Independent vendor directory
│   ├── src/
│   ├── public/
│   └── README.md
└── oteltracer/               # Manual Tracing project
    ├── composer.json         # Independent dependencies
    ├── vendor/               # Independent vendor directory
    ├── src/
    ├── public/
    └── README.md
```

**Note:** Each project has its own `composer.json`, `composer.lock`, and `vendor/` directory. They are completely independent and can be deployed separately.

---

## 🔧 Development

Both projects share the same database schema but run independently on different ports.

### Database Setup
```bash
psql -U postgres -d postgres -f otelapi/database/migrations/001_create_php_user_tbl.sql
```

---

## 📖 Additional Resources

- [OpenTelemetry PHP Documentation](https://opentelemetry.io/docs/languages/php/)
- [OpenTelemetry Semantic Conventions](https://opentelemetry.io/docs/specs/semconv/)
- [methods.md](./methods.md) - Detailed OpenTelemetry methods reference

---

## 📝 License

MIT

