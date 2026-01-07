# OtelTracer - Active Span Enrichment Demonstration (eBPF Limitation)

## Overview

**OtelTracer** is a demonstration project that attempts to inject custom business attributes using the **Active Span Enrichment** approach (`trace.SpanFromContext()`). This project serves as a **proof of limitation** showing why this approach **does NOT work** with eBPF-based OpenTelemetry auto-instrumentation in Go.

## ⚠️ Important Notice

**This approach does NOT work with eBPF auto-instrumentation.**

- ❌ `trace.SpanFromContext()` returns a **non-recording no-op span**
- ❌ Custom attributes added via `SetAttributes()` are **not captured**
- ❌ TraceID and SpanID are all zeros (invalid span)
- ✅ **Use the `otelapi` project instead** for the working approach

## Purpose

This project exists to:

1. **Demonstrate the limitation** of active span enrichment with eBPF
2. **Provide evidence** that `SpanFromContext()` doesn't work as expected
3. **Show the attempted implementation** for comparison with the working approach
4. **Document why** this architectural limitation exists

## Why This Doesn't Work

### Technical Explanation

In eBPF-based OpenTelemetry auto-instrumentation:

1. **Spans are created at the kernel/eBPF level**, not in the Go runtime
2. **Spans are NOT stored in `context.Context`** in a way accessible to the application
3. **`trace.SpanFromContext(ctx)` returns a no-op span** with invalid TraceID/SpanID
4. **The Go application has no reference** to the actual auto-instrumented span

### Observed Behavior

When calling `trace.SpanFromContext(r.Context())`:

```
DEBUG: Span Context - TraceID: 00000000000000000000000000000000
DEBUG: Span Context - SpanID: 0000000000000000
DEBUG: IsSampled: false
DEBUG: IsValid: false
```

This is **expected behavior** and **by design** in eBPF auto-instrumentation.

## Architecture

### Technology Stack

- **Language**: Go 1.23.12
- **Database**: PostgreSQL
- **Web Framework**: Standard `net/http`
- **Documentation**: Swagger/OpenAPI
- **Observability**: OpenTelemetry 1.24.0

### Project Structure

```
oteltracer/
├── main.go           # Application entry point with .env loading
├── handlers.go       # HTTP handlers attempting active span enrichment
├── repository.go     # Database operations attempting active span enrichment
├── database.go       # Database connection and schema management
├── models.go         # Data models and request/response structures
├── go.mod            # Go module dependencies
└── docs/             # Auto-generated Swagger documentation
```

## Key Differences from OtelAPI

| Aspect | OtelTracer (This Project) | OtelAPI (Working) |
|--------|---------------------------|-------------------|
| Approach | Active Span Enrichment | Explicit Span Creation |
| Method | `trace.SpanFromContext()` | `tracer.Start()` |
| Works with eBPF | ❌ No | ✅ Yes |
| Creates new spans | No | Yes |
| Custom attributes captured | ❌ No | ✅ Yes |

## Code Example (Non-Working)

### Handler Implementation

```go
func (h *UserHandler) GetUser(w http.ResponseWriter, r *http.Request) {
    // Attempt to get the active span
    span := trace.SpanFromContext(r.Context())
    
    // This span is non-recording and invalid!
    if !span.IsRecording() {
        log.Printf("WARNING: Span is not recording")
    }
    
    // These attributes are NOT captured
    span.SetAttributes(
        attribute.String("apm.http.method", r.Method),
        attribute.String("apm.operation", "get_user"),
    )
    
    // Business logic continues...
}
```

### What Happens

1. `SpanFromContext()` returns a no-op span
2. `IsRecording()` returns `false`
3. `SetAttributes()` is called but has no effect
4. Attributes do **not** appear in traces

## Installation & Setup

### Prerequisites

- Go 1.23.12 or higher
- PostgreSQL database

### Environment Variables

Create a `.env` file or set environment variables:

```bash
DB_HOST=localhost
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=postgres
DB_NAME=postgres
PORT=8081
```

### Build & Run

1. **Install dependencies**:
   ```bash
   go mod download
   ```

2. **Generate Swagger documentation** (if modified):
   ```bash
   swag init
   ```

3. **Run the application**:
   ```bash
   go run .
   ```

## API Endpoints

Same as `otelapi`:

- `POST /users` - Create user
- `GET /users/{username}` - Get user
- `GET /users` - Get all users
- `PUT /users/{username}` - Update user
- `DELETE /users/{username}` - Delete user
- `GET /health` - Health check
- `GET /swagger/` - API documentation

## Testing

You can test the API endpoints, but **custom attributes will not appear in traces** when using eBPF auto-instrumentation.

```bash
# Create a user
curl -X POST http://localhost:8081/users \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "full_name": "Test User"
  }'

# Get the user
curl http://localhost:8081/users/testuser
```

## Verification

To verify that this approach doesn't work:

1. Run the application with eBPF auto-instrumentation
2. Make API requests
3. Check the application logs for "WARNING: Span is not recording"
4. Inspect traces in your observability backend
5. Notice that custom `apm.*` attributes are **missing**

## The Solution

**Use the `otelapi` project instead**, which demonstrates the correct approach:

- Create new spans with `tracer.Start()`
- Add custom attributes to the manually created spans
- Manual spans become children of auto-instrumented spans
- All attributes are properly captured

## Related Documentation

- **Working Implementation**: `../otelapi/README.md`
- **Main POC Document**: `../Go_Custom_Attribute_POC.md`
- **Methods Comparison**: `../Methods.md`
- **Detailed Technical Explanation**: `NotPossible.md`

## Conclusion

This project demonstrates an **important limitation** of eBPF-based auto-instrumentation in Go:

> **Active span enrichment via `trace.SpanFromContext()` does not work with eBPF auto-instrumentation.**

The only supported approach is **explicit span creation** using `tracer.Start()`, as demonstrated in the `otelapi` project.

## License

This is a proof-of-concept demonstration project.

