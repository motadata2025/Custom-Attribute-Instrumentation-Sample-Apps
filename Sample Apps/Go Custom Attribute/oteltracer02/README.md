# OtelTracer02 - Simple OpenTelemetry Demo Application

## Overview

**OtelTracer02** is a lightweight, single-file demonstration application that showcases OpenTelemetry custom attribute injection in Go. This project provides a simple web interface with buttons to trigger traced operations, making it ideal for quick testing and demonstrations.

## Purpose

This project demonstrates:

- ✅ **Simple custom attribute injection** using `tracer.Start()`
- ✅ **Interactive web UI** for triggering traced operations
- ✅ **External API calls** with custom tracing
- ✅ **All supported attribute data types** (string, int64, float64, bool, and their slice variants)
- ✅ **Minimal setup** - single file, no database required

## Features

### 1. Interactive Web Interface

A simple HTML page with buttons to trigger traced operations:

- **"Click to Call External API"** - Triggers an external API call with custom tracing
- **"Test All Attributes"** - Demonstrates all supported attribute data types

### 2. Custom Attribute Types Demonstration

The application demonstrates all OpenTelemetry attribute types supported in Go:

**Primitive Types:**
- `attribute.Bool()` - Boolean values
- `attribute.Int64()` - 64-bit integers
- `attribute.Float64()` - 64-bit floating point numbers
- `attribute.String()` - String values

**Slice Types:**
- `attribute.BoolSlice()` - Array of booleans
- `attribute.Int64Slice()` - Array of integers
- `attribute.Float64Slice()` - Array of floats
- `attribute.StringSlice()` - Array of strings

### 3. External API Integration

Calls JSONPlaceholder API (free test API) with comprehensive tracing:

```go
span.SetAttributes(
    attribute.String("apm.external.api.url", apiURL),
    attribute.String("apm.external.api.method", "GET"),
    attribute.Int64("apm.external.api.duration_ms", duration.Milliseconds()),
    attribute.Int("apm.external.api.status_code", resp.StatusCode),
)
```

## Architecture

### Technology Stack

- **Language**: Go 1.23.12
- **Web Framework**: Standard `net/http`
- **Observability**: OpenTelemetry 1.24.0
- **External API**: JSONPlaceholder (https://jsonplaceholder.typicode.com)

### Project Structure

```
oteltracer02/
├── main.go           # Single-file application with all functionality
├── go.mod            # Go module dependencies
└── go.sum            # Dependency checksums
```

## Installation & Setup

### Prerequisites

- Go 1.23.12 or higher
- OpenTelemetry eBPF auto-instrumentation agent (for production use)

### Build & Run

1. **Install dependencies**:
   ```bash
   go mod download
   ```

2. **Run the application**:
   ```bash
   go run main.go
   ```

3. **Or build and run**:
   ```bash
   go build -o oteltracer02
   ./oteltracer02
   ```

4. **Access the application**:
   ```
   http://localhost:8082
   ```

## Usage

### Web Interface

1. Open `http://localhost:8082` in your browser
2. Click **"Click to Call External API"** to trigger an external API call
3. Click **"Test All Attributes"** to test all attribute data types
4. View the JSON response in the browser

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Home page with interactive buttons |
| `/api/call` | GET | Triggers external API call with custom tracing |
| `/api/test-attributes` | GET | Tests all attribute data types |

### Testing with cURL

```bash
# Test external API call
curl http://localhost:8082/api/call

# Test all attribute types
curl http://localhost:8082/api/test-attributes
```

## Custom Attributes Reference

### Button Click Handler Attributes

```go
attribute.String("user.action", "button_click")
attribute.String("operation", "external_api_call")
attribute.String("apm.custom.attribute", "demo_value")
attribute.String("app.component", "api_handler")
attribute.String("apm.business.operation", "fetch_post_data")
attribute.Bool("apm.error", true)  // On error
attribute.String("apm.error.message", err.Error())  // On error
```

### External API Call Attributes

```go
attribute.String("apm.external.api.url", apiURL)
attribute.String("apm.external.api.method", "GET")
attribute.String("apm.custom.request.id", "req-12345")
attribute.String("apm.external.api.provider", "jsonplaceholder")
attribute.String("apm.data.type", "post")
attribute.Int64("apm.external.api.duration_ms", duration.Milliseconds())
attribute.Int("apm.external.api.status_code", resp.StatusCode)
attribute.String("apm.external.api.status", resp.Status)
attribute.Int64("apm.external.api.response.content_length", resp.ContentLength)
attribute.Int("apm.external.api.response.body_size_bytes", len(body))
```

### Test Attributes (All Data Types)

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

## Trace Structure

When you click the "Call External API" button, the following trace structure is created:

```
HTTP GET / (auto-instrumented by eBPF)
└── handle_api_button_click (manual span)
    └── call_external_api (manual span)
        └── HTTP GET https://jsonplaceholder.typicode.com/posts/1 (auto-instrumented)
```

## Key Implementation Details

### Tracer Initialization

```go
var tracer trace.Tracer

func init() {
    // Get the global tracer
    // Auto-instrumentation will set up the tracer provider
    tracer = otel.Tracer("go-otel-demo")
}
```

### Creating Custom Spans

```go
ctx, span := tracer.Start(ctx, "operation_name")
defer span.End()

span.SetAttributes(
    attribute.String("key", "value"),
)
```

### Error Handling with Tracing

```go
if err != nil {
    span.SetAttributes(
        attribute.Bool("apm.error", true),
        attribute.String("apm.error.message", err.Error()),
    )
    span.RecordError(err)
    return nil, err
}
```

## Advantages of This Demo

1. **Single File** - Easy to understand and modify
2. **No Database** - No external dependencies except the test API
3. **Interactive UI** - Visual feedback for testing
4. **Comprehensive Examples** - Shows all attribute types
5. **Real External Calls** - Demonstrates distributed tracing

## Use Cases

- **Quick Testing** - Test OpenTelemetry setup quickly
- **Learning** - Understand custom attribute injection
- **Demonstrations** - Show tracing capabilities to stakeholders
- **Development** - Prototype new tracing patterns

## Related Documentation

- **Production-Ready Implementation**: `../otelapi/README.md`
- **Main POC Document**: `../Go_Custom_Attribute_POC.md`
- **Methods Comparison**: `../Methods.md`

## License

This is a proof-of-concept demonstration project.

