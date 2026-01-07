# Project Comparison Guide

Detailed comparison of all three projects in this repository.

## Overview Table

| Aspect | OtelAPI | OtelTracer | OtelTracer02 |
|--------|---------|------------|--------------|
| **Status** | ✅ Working | ❌ Non-Working | ✅ Working |
| **Approach** | Explicit Span Creation | Active Span Enrichment | Explicit Span Creation |
| **Primary Method** | `tracer.Start()` | `trace.SpanFromContext()` | `tracer.Start()` |
| **Works with eBPF** | ✅ Yes | ❌ No | ✅ Yes |
| **Database** | PostgreSQL | PostgreSQL | None |
| **Complexity** | High (Production) | High (Production) | Low (Demo) |
| **Files** | 7 files | 7 files | 1 file |
| **Port** | 8080 | 8081 | 8082 |
| **Web UI** | No | No | Yes |
| **Swagger Docs** | Yes | Yes | No |
| **Best For** | Production reference | Understanding limitations | Quick demos |

---

## Detailed Comparison

### 1. OtelAPI ✅ (Recommended)

**Purpose**: Production-ready reference implementation

**Key Features**:
- ✅ Complete CRUD REST API
- ✅ PostgreSQL database integration
- ✅ Multi-layer tracing (Handler → Repository → Database)
- ✅ Swagger/OpenAPI documentation
- ✅ Custom attributes at every layer
- ✅ Proper error handling
- ✅ Environment configuration

**Architecture**:
```
HTTP Request (eBPF auto-instrumented)
└── CreateUser Handler Span (manual)
    └── CreateUser Repository Span (manual)
        └── SQL INSERT (eBPF auto-instrumented)
```

**Custom Attributes Example**:
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

**When to Use**:
- Building production applications
- Need complete CRUD examples
- Want to see multi-layer tracing
- Require database integration patterns

**Pros**:
- Production-ready code structure
- Comprehensive examples
- Well-documented
- Shows best practices

**Cons**:
- Requires PostgreSQL setup
- More complex to understand initially
- Longer setup time

---

### 2. OtelTracer ❌ (Educational)

**Purpose**: Demonstrates why active span enrichment doesn't work with eBPF

**Key Features**:
- ❌ Attempts to use `trace.SpanFromContext()`
- ❌ Custom attributes are NOT captured
- ✅ Shows the limitation clearly
- ✅ Includes debug logging
- ✅ Same API structure as OtelAPI

**Architecture**:
```
HTTP Request (eBPF auto-instrumented)
└── [Attempted enrichment - FAILS]
    └── SQL Query (eBPF auto-instrumented)
```

**Attempted Pattern (Doesn't Work)**:
```go
// This returns a non-recording no-op span
span := trace.SpanFromContext(r.Context())

// These attributes are NOT captured
span.SetAttributes(
    attribute.String("apm.operation", "get_user"),
)
```

**Debug Output**:
```
WARNING: Span is not recording, custom attributes won't be added
DEBUG: Span Context - TraceID: 00000000000000000000000000000000
DEBUG: Span Context - SpanID: 0000000000000000
```

**When to Use**:
- Understanding why active span enrichment fails
- Learning about eBPF limitations
- Comparing with the working approach
- Educational purposes

**Pros**:
- Clear demonstration of limitation
- Includes helpful debug logging
- Same structure as OtelAPI for easy comparison
- Well-documented why it fails

**Cons**:
- Doesn't work with eBPF (by design)
- Requires PostgreSQL setup
- Not useful for production

---

### 3. OtelTracer02 ✅ (Quick Demo)

**Purpose**: Simple, fast demonstration of custom attributes

**Key Features**:
- ✅ Single-file application
- ✅ No database required
- ✅ Interactive web UI with buttons
- ✅ External API call demonstration
- ✅ All attribute data types shown
- ✅ Minimal setup

**Architecture**:
```
HTTP GET / (eBPF auto-instrumented)
└── handle_api_button_click (manual)
    └── call_external_api (manual)
        └── HTTP GET external API (eBPF auto-instrumented)
```

**Custom Attributes Example**:
```go
tracer := otel.Tracer("go-otel-demo")
ctx, span := tracer.Start(ctx, "handle_api_button_click")
defer span.End()

span.SetAttributes(
    attribute.String("user.action", "button_click"),
    attribute.String("apm.custom.attribute", "demo_value"),
    attribute.Int64("apm.external.api.duration_ms", duration.Milliseconds()),
)
```

**All Data Types Demonstrated**:
```go
// Primitives
attribute.Bool("apm.test.bool", true)
attribute.Int64("apm.test.int64", 9876543210)
attribute.Float64("apm.test.float64", 123.456)
attribute.String("apm.test.string", "hello world")

// Slices
attribute.BoolSlice("apm.test.bool_slice", []bool{true, false, true})
attribute.Int64Slice("apm.test.int64_slice", []int64{10, 20, 30})
attribute.Float64Slice("apm.test.float64_slice", []float64{1.5, 2.5, 3.5})
attribute.StringSlice("apm.test.string_slice", []string{"apple", "banana", "cherry"})
```

**When to Use**:
- Quick testing and demos
- Learning custom attribute basics
- No database available
- Need interactive UI
- Want to see all data types

**Pros**:
- Fastest setup (1 minute)
- No database required
- Interactive web interface
- Single file - easy to understand
- Shows all attribute types

**Cons**:
- Not production-ready
- Limited functionality
- No database integration
- No Swagger docs

---

## Feature Matrix

| Feature | OtelAPI | OtelTracer | OtelTracer02 |
|---------|---------|------------|--------------|
| **Custom Attributes Work** | ✅ | ❌ | ✅ |
| **CRUD Operations** | ✅ | ✅ | ❌ |
| **Database Integration** | ✅ | ✅ | ❌ |
| **Swagger Documentation** | ✅ | ✅ | ❌ |
| **Web UI** | ❌ | ❌ | ✅ |
| **Multi-layer Tracing** | ✅ | ❌ | ✅ |
| **Error Handling** | ✅ | ✅ | ✅ |
| **Environment Config** | ✅ | ✅ | ❌ |
| **All Data Types Demo** | ❌ | ❌ | ✅ |
| **External API Calls** | ❌ | ❌ | ✅ |
| **Single File** | ❌ | ❌ | ✅ |
| **Production Ready** | ✅ | ❌ | ❌ |

---

## Code Comparison

### Creating a Span with Custom Attributes

**OtelAPI (Working)**:
```go
tracer := otel.Tracer("otelapi")
ctx, span := tracer.Start(r.Context(), "CreateUser")
defer span.End()

span.SetAttributes(
    attribute.String("apm.operation", "create_user"),
    attribute.String("apm.user.username", req.Username),
)
```

**OtelTracer (Non-Working)**:
```go
// ❌ Returns non-recording span with eBPF
span := trace.SpanFromContext(r.Context())

// ❌ Attributes are lost
span.SetAttributes(
    attribute.String("apm.operation", "get_user"),
)
```

**OtelTracer02 (Working)**:
```go
tracer := otel.Tracer("go-otel-demo")
ctx, span := tracer.Start(ctx, "handle_api_button_click")
defer span.End()

span.SetAttributes(
    attribute.String("user.action", "button_click"),
)
```

---

## Use Case Recommendations

### Choose OtelAPI if you need:
- Production-ready code examples
- Database integration patterns
- Multi-layer tracing architecture
- REST API with CRUD operations
- Swagger/OpenAPI documentation
- Complete application structure

### Choose OtelTracer if you want to:
- Understand eBPF limitations
- Learn what NOT to do
- Compare working vs non-working approaches
- See debug logging for troubleshooting
- Educational purposes

### Choose OtelTracer02 if you want:
- Quick demo in under 1 minute
- No database setup
- Interactive web interface
- See all attribute data types
- Simple, single-file example
- External API call tracing

---

## Learning Path

**Recommended Order**:

1. **Start with OtelTracer02** (5 minutes)
   - Get immediate results
   - Understand the basic pattern
   - See all data types

2. **Read the Documentation** (15 minutes)
   - Go_Custom_Attribute_POC.md
   - Methods.md
   - This comparison guide

3. **Explore OtelAPI** (30 minutes)
   - Production patterns
   - Multi-layer tracing
   - Database integration

4. **Review OtelTracer** (10 minutes)
   - Understand the limitation
   - See why it doesn't work
   - Compare with OtelAPI

---

## Summary

| Project | Status | Best For | Setup Time |
|---------|--------|----------|------------|
| **OtelAPI** | ✅ Working | Production reference | 3 minutes |
| **OtelTracer** | ❌ Non-Working | Learning limitations | 3 minutes |
| **OtelTracer02** | ✅ Working | Quick demos | 1 minute |

**Key Takeaway**: Use `tracer.Start()` to create new spans with custom attributes. Don't use `trace.SpanFromContext()` with eBPF auto-instrumentation.

---

**Last Updated**: January 6, 2026

