# Go Custom Attribute Instrumentation with OpenTelemetry

## Overview

This repository contains a comprehensive proof-of-concept (POC) demonstrating **custom business attribute injection** strategies for OpenTelemetry in Go runtime environments, specifically focusing on **eBPF-based auto-instrumentation**.

## 🎯 Key Findings

When using eBPF-based OpenTelemetry auto-instrumentation in Go:

- ❌ **Active Span Enrichment** (`trace.SpanFromContext()`) **does NOT work**
- ✅ **Explicit Span Creation** (`tracer.Start()`) **WORKS perfectly**

### Why Active Span Enrichment Fails

eBPF auto-instrumentation creates spans at the **kernel/eBPF level**, outside the Go runtime. These spans are:

- Not stored in `context.Context` in an accessible way
- Not retrievable via `trace.SpanFromContext()`
- Owned entirely by the eBPF agent, not the Go application

**Result**: `trace.SpanFromContext()` returns a non-recording no-op span with invalid TraceID/SpanID.

### The Working Solution

Create **new child spans** using `tracer.Start()` that automatically link to auto-instrumented parent spans through context propagation:

```go
tracer := otel.Tracer("my-service")
ctx, span := tracer.Start(ctx, "BusinessOperation")
defer span.End()

span.SetAttributes(
    attribute.String("apm.operation", "create_order"),
    attribute.String("apm.order.id", orderID),
)
```

## 📁 Repository Structure

```
.
├── README.md                          # This file - main documentation
├── Go_Custom_Attribute_POC.md         # Detailed POC findings and implementation guide
├── Methods.md                         # Comparison of instrumentation methods
├── TestingSnapshots/                  # Visual verification screenshots
│   ├── Go Tracer Based Custom Attribute Injection.png
│   └── Go Tracer Based Supported Datatype Custom Attribute Injection.png.png
├── otelapi/                           # ✅ WORKING: Explicit span creation approach
│   ├── README.md                      # Detailed project documentation
│   ├── main.go                        # Application entry point
│   ├── handlers.go                    # HTTP handlers with custom spans
│   ├── repository.go                  # Database operations with custom spans
│   ├── database.go                    # Database connection management
│   ├── models.go                      # Data models
│   ├── go.mod                         # Dependencies
│   ├── NotPossible.md                 # Technical explanation of eBPF limitation
│   └── docs/                          # Swagger documentation
├── oteltracer/                        # ❌ NON-WORKING: Active span enrichment attempt
│   ├── README.md                      # Detailed project documentation
│   ├── main.go                        # Application entry point
│   ├── handlers.go                    # HTTP handlers attempting span enrichment
│   ├── repository.go                  # Database operations attempting span enrichment
│   ├── database.go                    # Database connection management
│   ├── models.go                      # Data models
│   ├── go.mod                         # Dependencies
│   └── docs/                          # Swagger documentation
└── oteltracer02/                      # ✅ WORKING: Simple demo application
    ├── README.md                      # Detailed project documentation
    ├── main.go                        # Single-file demo with web UI
    └── go.mod                         # Dependencies
```

## 🚀 Projects

### 1. OtelAPI (Recommended - Production Ready)

**Status**: ✅ **WORKING**

A complete user management REST API demonstrating the **correct approach** for custom attribute injection.

**Key Features**:
- Full CRUD operations with PostgreSQL
- Multi-layer tracing (Handler → Repository → Database)
- Swagger/OpenAPI documentation
- Production-ready architecture

**Port**: 8080

[📖 Read Full Documentation](otelapi/README.md)

### 2. OtelTracer (Educational - Shows Limitation)

**Status**: ❌ **NON-WORKING** (By Design)

Demonstrates why active span enrichment doesn't work with eBPF auto-instrumentation.

**Purpose**:
- Proof of limitation
- Educational reference
- Comparison with working approach

**Port**: 8081

[📖 Read Full Documentation](oteltracer/README.md)

### 3. OtelTracer02 (Quick Demo)

**Status**: ✅ **WORKING**

A lightweight, single-file demo application with interactive web UI.

**Key Features**:
- No database required
- Interactive buttons for testing
- Demonstrates all attribute data types
- External API call tracing

**Port**: 8082

[📖 Read Full Documentation](oteltracer02/README.md)

## 📚 Documentation

### Core Documents

1. **[Go_Custom_Attribute_POC.md](Go_Custom_Attribute_POC.md)**
   - Complete POC findings
   - Implementation strategies
   - Data type support
   - Runtime execution guide

2. **[Methods.md](Methods.md)**
   - Detailed comparison of instrumentation methods
   - Active Span Enrichment vs Explicit Span Creation
   - Use cases and limitations
   - Cross-language equivalents

3. **[otelapi/NotPossible.md](otelapi/NotPossible.md)**
   - Technical deep-dive into eBPF limitation
   - Official OpenTelemetry documentation references
   - Architecture explanation
   - Solution patterns

## 🛠️ Quick Start

### Prerequisites

- **Go**: 1.23.12 or higher
- **PostgreSQL**: For `otelapi` and `oteltracer` projects
- **OpenTelemetry eBPF Agent**: For production tracing (optional for local testing)

### Running the Projects

#### OtelAPI (Recommended)

```bash
cd otelapi
export DB_HOST=localhost DB_PORT=5432 DB_USER=postgres DB_PASSWORD=postgres DB_NAME=postgres
go run .
# Access: http://localhost:8080
# Swagger: http://localhost:8080/swagger/
```

#### OtelTracer02 (Quick Demo)

```bash
cd oteltracer02
go run main.go
# Access: http://localhost:8082
```

#### OtelTracer (Educational)

```bash
cd oteltracer
export DB_HOST=localhost DB_PORT=5432 DB_USER=postgres DB_PASSWORD=postgres DB_NAME=postgres
go run .
# Access: http://localhost:8081
# Note: Custom attributes won't appear in traces with eBPF
```

## 📊 Supported Data Types

| Category | Go Types | Example |
|----------|----------|---------|
| **Text** | `string` | `attribute.String("key", "value")` |
| **Integer** | `int`, `int64` | `attribute.Int64("key", 123)` |
| **Decimal** | `float64` | `attribute.Float64("key", 123.45)` |
| **Boolean** | `bool` | `attribute.Bool("key", true)` |
| **Arrays** | `[]string`, `[]int64`, `[]float64`, `[]bool` | `attribute.StringSlice("key", []string{"a", "b"})` |

## 🔍 Verification

Visual verification screenshots are available in the `TestingSnapshots/` directory:

- Custom attribute injection in traces
- Supported data types demonstration

## 📖 Implementation Guide

### Step 1: Add Dependencies

```go
require (
    go.opentelemetry.io/otel v1.24.0
    go.opentelemetry.io/otel/attribute v1.24.0
    go.opentelemetry.io/otel/trace v1.24.0
)
```

### Step 2: Get a Tracer

```go
import "go.opentelemetry.io/otel"

tracer := otel.Tracer("your-service-name")
```

### Step 3: Create Spans with Custom Attributes

```go
ctx, span := tracer.Start(ctx, "OperationName")
defer span.End()

span.SetAttributes(
    attribute.String("apm.operation", "business_operation"),
    attribute.String("apm.user.id", userID),
    attribute.Int64("apm.order.amount", amount),
)
```

## 🎓 Key Learnings

1. **eBPF Architecture**: Spans are created at kernel level, not in Go runtime
2. **Context Propagation**: Manual spans link to auto-instrumented spans automatically
3. **No TracerProvider Setup**: Auto-instrumentation handles this
4. **Span Hierarchy**: Manual spans become children of auto-instrumented spans
5. **Zero Code vs Code Change**: This approach requires code changes but works reliably

## 🔗 External Resources

- **OpenTelemetry Go Auto SDK**: https://opentelemetry.io/docs/zero-code/go/autosdk/
- **OpenTelemetry Go Instrumentation**: https://github.com/open-telemetry/opentelemetry-go-instrumentation
- **Sample Application**: https://github.com/ShivenPatel19/Go-Custom-Attribute-Instrumentation-with-Code-Change-

## ⚠️ Important Notes

- This approach **requires code changes** (not zero-code)
- Runtime execution still uses eBPF auto-instrumentation
- Manual spans automatically correlate with auto-instrumented spans
- No manual TracerProvider setup required

## 📝 License

This is a proof-of-concept demonstration project for educational and evaluation purposes.

## 👤 Author

**Shiven Patel**
- Email: shiven.patel@motadata.com
- Organization: Motadata

---

**Last Updated**: January 6, 2026
**Go Version**: 1.23.12
**OpenTelemetry Version**: 1.24.0

