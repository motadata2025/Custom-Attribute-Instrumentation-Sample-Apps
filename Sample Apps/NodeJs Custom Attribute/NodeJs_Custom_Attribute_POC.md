# Custom/Business Specific Attribute Injection Strategies for Node.js Runtime

> **Document Type:** Proof of Concept (POC)
> **Project:** Node.js Custom Attribute
> **Last Verified:** January 6, 2026
> **Status:** Verified & Implemented
> **Testing Environment Node.js Version:** 24.12

---

## 1. Overview

This document details the findings and implementation strategies for injecting custom business attributes into OpenTelemetry traces in a Node.js runtime environment. All methods described below have been verified with working implementations, demonstrating that traces are generated correctly, custom/business attributes are appended to the appropriate spans, multiple data types are supported (string, number, boolean, arrays), and all attributes are visible in the observability UI.

Reference implementations were verified using sample Node.js Express applications with PostgreSQL integration.

**Key Findings:**
- ✅ Two primary approaches validated: API-Based Span Enrichment and Manual Tracer-Based Span Creation
- ✅ All OpenTelemetry-compatible data types supported (primitives and homogeneous arrays)
- ✅ Automatic attribute prefixing with `apm.` namespace for consistency
- ✅ Null-safe implementations prevent runtime exceptions
- ✅ Compatible with auto-instrumentation and manual instrumentation
- ✅ Production-ready utility classes provided for both approaches

---

## 2. Approach 1: API-Based Span Enrichment (Recommended Approach)

This approach uses the OpenTelemetry Node.js API to enrich the currently active span without creating new spans, using `trace.getActiveSpan().setAttribute()`.

### 2.1 Description

This method relies on `trace.getActiveSpan()` to retrieve the currently active span and add attributes dynamically at any point during execution. To simplify usage and ensure consistency, we implemented a utility class `MotadataDynamicInstrumentation`.

**How It Works:**
1. Auto-instrumentation (HTTP, Express, PostgreSQL, etc.) creates spans automatically
2. Your business logic retrieves the active span using `trace.getActiveSpan()`
3. Custom attributes are added to the existing span without altering the trace structure
4. The utility class handles null-safety, type validation, and automatic prefixing

**Strengths:**
*   **Minimal Code Changes:** Add attributes with simple one-line calls
*   **Dynamic:** Attributes can be added at any point during function execution (start, middle, or end)
*   **Non-Intrusive:** Does not create new spans; enriches spans created by auto-instrumentation (HTTP, DB, etc.)
*   **Flexible:** Works seamlessly with auto-instrumentation, manually created spans, or custom instrumentation
*   **Type-Safe:** Utility class validates types and prevents runtime errors
*   **Consistent Naming:** Automatic `apm.` prefix ensures naming conventions

**Limitations:**
*   Requires an active recording span. If the request is not traced (for example, unsupported frameworks or missing auto-instrumentation), `getActiveSpan()` returns `undefined` or a non-recording span, and custom attributes are ignored and not exported.
*   Cannot control span lifecycle (start/end times, span hierarchy)
*   Limited to enriching existing spans; cannot create new trace hierarchies

### 2.2 Prerequisites

**Dependencies:**
Ensure the `@opentelemetry/api` package is added to your project.

**NPM:**
```bash
npm install @opentelemetry/api
```

**Package.json:**
```json
{
  "dependencies": {
    "@opentelemetry/api": "^1.9.0"
  }
}
```

### 2.3 Client-Side Implementation

Clients should include the `MotadataDynamicInstrumentation` utility class in their project to handle null-safety and naming conventions.

**Step 1: Add the Utility Class**
(See `otelapi/util/MotadataDynamicInstrumentation.js` in the project for full source).

**Step 2: Instrument Code**
```javascript
const MotadataDynamicInstrumentation = require('./util/MotadataDynamicInstrumentation');

async function handleOrder(orderId) {
  // ... business logic ...
  const user = await database.getUser();

  // Inject attributes dynamically at runtime
  // Note: The utility automatically adds the 'apm.' prefix if missing.
  MotadataDynamicInstrumentation.set('user.id', user.id);
  MotadataDynamicInstrumentation.set('user.email', user.email);
  MotadataDynamicInstrumentation.set('order.total', calculateTotal());
  MotadataDynamicInstrumentation.setStringList('order.items', getItemNames());
}
```

### 2.4 MotadataDynamicInstrumentation Utility Reference

This section explains the internal behavior of the `MotadataDynamicInstrumentation` utility class used in the API-Based instrumentation method.

#### What is happening inside `MotadataDynamicInstrumentation`?

The `MotadataDynamicInstrumentation` class acts as a **safe wrapper** around the standard OpenTelemetry `trace.getActiveSpan().setAttribute()` API. Its primary goal is to prevent runtime exceptions and enforce consistency without cluttering business logic.

#### Key Internal Mechanisms:

1.  **Automatic Prefixing:**
    *   Every attribute key passed to the utility is checked.
    *   If it doesn't already start with `apm.`, the prefix is automatically prepended.
    *   *Example:* `set("user.id", ...)` becomes `apm.user.id` in the trace.
    *   This ensures consistent naming conventions across all custom attributes.

2.  **Null Safety:**
    *   The class explicitly checks for `null` and `undefined` keys and values.
    *   If a key or value is `null` or `undefined`, the operation is **silently ignored**. No exceptions are thrown, ensuring that telemetry code never crashes the application.
    *   This is critical for production environments where telemetry should never impact application stability.

3.  **Type Handling:**
    *   **Strings, Numbers, Booleans** are handled directly by the `set()` method with automatic type detection.
    *   **Arrays** are handled by type-specific methods: `setBooleanList()`, `setNumberList()`, and `setStringList()`.
    *   Empty arrays are silently ignored (not added to the span) to reduce noise in telemetry data.
    *   Type validation ensures only OpenTelemetry-compatible types are used.

4.  **Active Span Check:**
    *   Before setting any attribute, the utility checks if an active span exists using `trace.getActiveSpan()`.
    *   If no active span exists, the operation is silently ignored.
    *   This prevents errors in non-instrumented code paths or background threads.

5.  **Error Suppression:**
    *   All internal calls are wrapped in `try-catch` blocks that swallow exceptions. This guarantees that even if the OpenTelemetry API fails, the application flow remains uninterrupted.
    *   Errors are silently logged (optional) but never propagated to the caller.

#### API Methods

| Method | Parameters | Description |
|--------|-----------|-------------|
| `set(key, value)` | `key: string`, `value: string\|number\|boolean` | Sets a primitive attribute on the active span |
| `setStringList(key, value)` | `key: string`, `value: string[]` | Sets a string array attribute |
| `setNumberList(key, value)` | `key: string`, `value: number[]` | Sets a number array attribute |
| `setBooleanList(key, value)` | `key: string`, `value: boolean[]` | Sets a boolean array attribute |

#### Minimal Code Reference

```javascript
// Simplified view of what happens internally
static set(key, value) {
  if (typeof value === 'string') {
    this.safeSet(key, value, (prefixed) => {
      const span = trace.getActiveSpan(); // 1. Get active span
      if (span) {                         // 2. Check if span exists
        span.setAttribute(prefixed, value); // 3. Set attribute
      }
    });
  }
  // Similar for number and boolean types
}

static safeSet(key, value, setter) {
  try {
    if (key == null || value == null) return; // 4. Null check
    const prefixed = this.prefixKey(key);     // 5. Prefixing
    if (prefixed == null) return;
    setter(prefixed);                         // 6. Execute setter
  } catch (exception) {
    // 7. Safety: Ignore all errors
  }
}
```

**Full Implementation:** See `otelapi/util/MotadataDynamicInstrumentation.js` in the reference project.

---

## 3. Approach 2: Manual Tracer and Span Creation

This approach involves manually obtaining a `Tracer` instance and managing the span lifecycle (start, scope, end) explicitly using `tracer.startActiveSpan()` or `tracer.startSpan()`.

### 3.1 Description

This provides the most control, allowing developers to create new root traces, manage complex parent-child relationships, and handle custom business workflows with precise span boundaries.

**How It Works:**
1. Obtain a `Tracer` instance using `trace.getTracer(name, version)`
2. Use `tracer.startActiveSpan()` to create a new span and make it active
3. Add attributes, events, and exceptions within the span context
4. The span is automatically ended when the callback completes (or manually with `span.end()`)
5. Nested spans are created by calling `startActiveSpan()` within an active span context

**Strengths:**
*   **Complete Control:** Can create new root spans (separate traces) or custom hierarchies
*   **Precise Lifecycle:** Exact control over when a span starts and ends
*   **Supports Complex Workflows:** Ideal for multi-step business processes with nested operations
*   **Custom Events:** Can add events and exceptions at any stage
*   **Works Everywhere:** Useful for instrumenting unsupported libraries or custom business logic
*   **Detailed Tracking:** Track duration of specific operations with high precision
*   **Error Handling:** Built-in exception recording and status management

**Limitations:**
*   **Verbose:** Requires more boilerplate code compared to API-based enrichment
*   **Complex:** Requires careful lifecycle handling to avoid unfinished or orphan spans
*   **Higher Span Volume:** Creates additional spans, which may increase telemetry data volume and costs
*   **Manual Context Management:** Developers must manually manage span context propagation in async scenarios
*   **Learning Curve:** Requires understanding of span lifecycle and context propagation

### 3.2 Prerequisites

**Dependencies:**
The core API package is required.

**NPM:**
```bash
npm install @opentelemetry/api
```

**Package.json:**
```json
{
  "dependencies": {
    "@opentelemetry/api": "^1.9.0"
  }
}
```

### 3.3 Client-Side Implementation

The client must obtain a tracer and use `startActiveSpan()` or `startSpan()` to create custom spans.

#### Option A: Using TracerService Utility (Recommended)

For production use, we recommend using the `TracerService` utility class which provides a simplified API and handles common patterns.

**Step 1: Add the TracerService Utility**
(See `oteltracer/services/tracerService.js` in the project for full source).

**Step 2: Use the Utility in Your Code**
```javascript
const tracerService = require('./services/tracerService');

async function processOrder(orderId) {
  return tracerService.executeInSpan('process-order', async (span) => {
    // Add attributes
    tracerService.addCommonAttributes(span, {
      operation: 'processOrder',
      controller: 'OrderController',
      userId: req.user.id
    });

    span.setAttribute('apm.order.id', orderId);
    span.addEvent('order.processing.started');

    // Business logic
    const order = await fetchOrder(orderId);
    const payment = await processPayment(order);

    // Add success attributes
    tracerService.addSuccessAttributes(span, 200, {
      'apm.payment.status': payment.status,
      'apm.payment.amount': payment.amount
    });

    return payment;
  });
}
```

#### Option B: Direct Tracer API Usage

**Example 1: Creating a Custom Span with startActiveSpan**
```javascript
const { trace, SpanStatusCode } = require('@opentelemetry/api');

// Get a tracer instance
const tracer = trace.getTracer('motadata.custom.instrumentation', '1.0.0');

async function processOrder(orderId) {
  // Create a new active span
  return tracer.startActiveSpan('process-order', async (span) => {
    try {
      // Add attributes
      span.setAttribute('apm.order.id', orderId);
      span.setAttribute('apm.operation', 'processOrder');

      // Add event
      span.addEvent('order.processing.started');

      // Business logic
      const order = await fetchOrder(orderId);
      const payment = await processPayment(order);

      // Add result attributes
      span.setAttribute('apm.payment.status', payment.status);
      span.setAttribute('apm.payment.amount', payment.amount);

      // Add success event
      span.addEvent('order.processing.completed');

      // Set success status
      span.setStatus({ code: SpanStatusCode.OK });

      return payment;
    } catch (error) {
      // Record exception
      span.recordException(error);

      // Set error status
      span.setStatus({
        code: SpanStatusCode.ERROR,
        message: error.message
      });

      // Add error attributes
      span.setAttribute('apm.error.occurred', true);
      span.setAttribute('apm.error.message', error.message);

      throw error;
    } finally {
      // CRITICAL: Always end the span
      span.end();
    }
  });
}
```

**Example 2: Nested Spans for Complex Workflows**
```javascript
const { trace, SpanStatusCode } = require('@opentelemetry/api');

const tracer = trace.getTracer('order-service', '1.0.0');

async function processCompleteOrder(orderId) {
  return tracer.startActiveSpan('order.complete-workflow', async (parentSpan) => {
    parentSpan.setAttribute('apm.order.id', orderId);
    parentSpan.setAttribute('apm.workflow', 'complete-order');

    try {
      // Child span 1: Validation
      await tracer.startActiveSpan('order.validate', async (span) => {
        span.setAttribute('apm.validation.type', 'inventory');
        const isValid = await validateOrder(orderId);
        span.setAttribute('apm.validation.result', isValid);
        span.setStatus({ code: SpanStatusCode.OK });
        span.end();
      });

      // Child span 2: Payment Processing
      await tracer.startActiveSpan('order.payment', async (span) => {
        span.setAttribute('apm.payment.method', 'credit_card');
        const payment = await processPayment(orderId);
        span.setAttribute('apm.payment.transaction_id', payment.txnId);
        span.setAttribute('apm.payment.amount', payment.amount);
        span.setStatus({ code: SpanStatusCode.OK });
        span.end();
      });

      // Child span 3: Shipping
      await tracer.startActiveSpan('order.shipping', async (span) => {
        span.setAttribute('apm.shipping.carrier', 'FedEx');
        const trackingId = await shipOrder(orderId);
        span.setAttribute('apm.shipping.tracking_id', trackingId);
        span.setStatus({ code: SpanStatusCode.OK });
        span.end();
      });

      parentSpan.setStatus({ code: SpanStatusCode.OK });
    } catch (error) {
      parentSpan.recordException(error);
      parentSpan.setStatus({
        code: SpanStatusCode.ERROR,
        message: error.message
      });
      throw error;
    } finally {
      parentSpan.end();
    }
  });
}
```

### 3.4 Advanced Configuration: SpanKind and Root Spans

When manually creating spans, you have fine-grained control over the span's characteristics.

#### Creating a Root Span (New Trace)
By default, `startActiveSpan()` creates a child of the currently active span. To start a completely new trace (a "root" span), use `.setNoParent()` or `ROOT_CONTEXT`.

```javascript
const { trace, ROOT_CONTEXT, SpanStatusCode } = require('@opentelemetry/api');

const tracer = trace.getTracer('my-service', '1.0.0');

// Create a root span (new trace, no parent)
const span = tracer.startSpan('background-job', {}, ROOT_CONTEXT);

try {
  span.setAttribute('apm.job.type', 'cleanup');
  // ... business logic ...
  span.setStatus({ code: SpanStatusCode.OK });
} finally {
  span.end();
}
```

#### SpanKind Reference
The `SpanKind` enum specifies the relationship between spans in addition to the parent/child relationship. This helps visualization tools understand the nature of the operation.

| SpanKind | Description |
| :--- | :--- |
| **INTERNAL** | Default value. Indicates that the span is used internally within the application (e.g., a method call). |
| **SERVER** | Indicates that the span covers server-side handling of an RPC or other remote request. |
| **CLIENT** | Indicates that the span covers the client-side wrapper around an RPC or other remote request. |
| **PRODUCER** | Indicates that the span describes a producer sending a message to a broker. There is no direct critical path latency relationship between producer and consumer spans. |
| **CONSUMER** | Indicates that the span describes a consumer receiving a message from a broker. |

### 3.5 TracerService Utility Reference

The `TracerService` utility class provides a simplified API for creating and managing spans with common patterns.

#### Available Methods

| Method | Parameters | Description |
|--------|-----------|-------------|
| `getTracer()` | None | Returns the tracer instance |
| `executeInSpan(name, fn, options)` | `name: string`, `fn: Function`, `options?: Object` | Executes a function within a span, handles lifecycle automatically |
| `createSpan(name, options)` | `name: string`, `options?: Object` | Creates a manual span (non-active) |
| `addCommonAttributes(span, metadata)` | `span: Span`, `metadata: Object` | Adds common APM attributes (operation, controller, userId, etc.) |
| `addSuccessAttributes(span, statusCode, data)` | `span: Span`, `statusCode?: number`, `data?: Object` | Adds success attributes and status |
| `addErrorAttributes(span, error, statusCode)` | `span: Span`, `error: Error`, `statusCode?: number` | Adds error attributes and records exception |

**Full Implementation:** See `oteltracer/services/tracerService.js` in the reference project.

### 3.6 API Methods Reference

This section provides a detailed reference for the key interfaces and methods used in manual instrumentation.

#### `Tracer` Interface
*Full Documentation: [OpenTelemetry Trace API](https://opentelemetry.io/docs/specs/otel/trace/api/)*

| Method | Description |
| :--- | :--- |
| `startActiveSpan(name, fn)` | Creates a new span, makes it active, executes the function, and automatically ends the span when the function completes. **Recommended for most use cases.** |
| `startActiveSpan(name, options, fn)` | Same as above, but with options (kind, attributes, links, etc.). |
| `startActiveSpan(name, options, context, fn)` | Same as above, but with explicit parent context. |
| `startSpan(name, options?, context?)` | Creates a new span but does NOT make it active. You must manually call `span.end()`. Use for background tasks or when you need manual control. |

#### `Span` Interface
*Full Documentation: [OpenTelemetry Span API](https://opentelemetry.io/docs/specs/otel/trace/api/#span)*

| Method | Description |
| :--- | :--- |
| `setAttribute(key, value)` | Adds or updates a single attribute on the span. Supports string, number, boolean, and arrays. |
| `setAttributes(attributes)` | Adds or updates multiple attributes at once from an object. |
| `addEvent(name, attributes?)` | Adds a time-stamped event (log) to the span. Useful for capturing significant moments within a span's lifetime. |
| `recordException(exception, attributes?)` | Records details of an exception as a special, structured event on the span. Includes stack trace and error details. |
| `setStatus(status)` | Sets the final status of the span (OK or ERROR). An ERROR status will typically cause the trace to be highlighted. |
| `updateName(name)` | Updates the span's name after it has started. Use sparingly. |
| `end(endTime?)` | Marks the end of the span's execution. **This is mandatory for every span you start manually.** Failure to call `end()` will result in memory leaks and broken traces. |
| `isRecording()` | Returns `true` if the span is recording and sending data. Useful for avoiding expensive attribute calculations if the trace is not being sampled. |
| `spanContext()` | Returns the immutable `SpanContext` (containing the Trace ID and Span ID) of this span. |

#### `SpanStatusCode` Enum

| Status Code | Description |
| :--- | :--- |
| `UNSET` | Default status. The operation completed without a known error. |
| `OK` | The operation completed successfully. Explicitly indicates success. |
| `ERROR` | The operation failed. Should be accompanied by an error message and typically includes a recorded exception. |

---

## 4. Data Type Support Summary

Both methods support standard OpenTelemetry attribute types. The `MotadataDynamicInstrumentation` utility specifically handles type safety and automatic prefixing.

### 4.1 Supported Types

| Category | Supported Node.js Types | Behavior | Example |
| :--- | :--- | :--- | :--- |
| **Text** | `string` | Stored as String | `'John Doe'` |
| **Number** | `number` (integer or float) | Stored as Number (IEEE 754 double precision) | `42`, `3.14159` |
| **Boolean** | `boolean` | Stored as Boolean | `true`, `false` |
| **String Array** | `Array<string>` | Stored as String Array (homogeneous) | `['admin', 'editor']` |
| **Number Array** | `Array<number>` | Stored as Number Array (homogeneous) | `[1, 2, 3]` |
| **Boolean Array** | `Array<boolean>` | Stored as Boolean Array (homogeneous) | `[true, false]` |

**Important Notes:**
- Node.js does not distinguish between integer and float types at the language level. All numbers are 64-bit floating point (IEEE 754).
- Arrays must be homogeneous (all elements of the same type).
- Empty arrays are valid but may be ignored by some implementations.
- Null and undefined values are not supported and will be silently ignored.

### 4.2 Supported Data Types Examples

```javascript
// ========================================
// PRIMITIVE TYPES (Stable)
// ========================================

// Strings
span.setAttribute('apm.user.name', 'John Doe');
span.setAttribute('apm.user.email', 'john@example.com');
span.setAttribute('apm.http.method', 'POST');

// Numbers (integers)
span.setAttribute('apm.user.age', 30);
span.setAttribute('apm.http.status_code', 200);
span.setAttribute('apm.retry.count', 3);

// Numbers (floats)
span.setAttribute('apm.order.total', 1599.99);
span.setAttribute('apm.response.time_ms', 45.67);
span.setAttribute('apm.cpu.usage_percent', 78.5);

// Booleans
span.setAttribute('apm.user.is_premium', true);
span.setAttribute('apm.cache.hit', false);
span.setAttribute('apm.payment.is_successful', true);

// ========================================
// ARRAY TYPES (Stable)
// ========================================

// String arrays (homogeneous only)
span.setAttribute('apm.user.roles', ['admin', 'editor', 'viewer']);
span.setAttribute('apm.product.tags', ['electronics', 'sale', 'featured']);

// Number arrays (homogeneous only)
span.setAttribute('apm.product.prices', [19.99, 29.99, 39.99]);
span.setAttribute('apm.response.times_ms', [45, 67, 89, 123]);

// Boolean arrays (homogeneous only)
span.setAttribute('apm.feature.flags', [true, false, true, true]);
span.setAttribute('apm.validation.results', [true, true, false]);

// Empty arrays (valid but may be ignored)
span.setAttribute('apm.empty.list', []);
```

### 4.3 Unsupported Types

```javascript
// ❌ Mixed type arrays - NOT ALLOWED
span.setAttribute('mixed', ['string', 123, true]);        // ❌ INVALID

// ❌ Nested arrays
span.setAttribute('nested', [[1, 2], [3, 4]]);            // ❌ INVALID

// ❌ Objects (unless Development status supported by SDK)
span.setAttribute('object', { key: 'value' });            // ⚠️ Check SDK support

// ❌ Functions
span.setAttribute('function', () => {});                  // ❌ INVALID

// ❌ Symbols
span.setAttribute('symbol', Symbol('test'));              // ❌ INVALID

// ❌ Undefined and null
span.setAttribute('undefined', undefined);                // ❌ INVALID (silently ignored)
span.setAttribute('null', null);                          // ❌ INVALID (silently ignored)
```

### 4.4 Type Validation Best Practices

```javascript
// ✅ Good: Validate before setting
const userId = req.user?.id;
if (userId) {
  span.setAttribute('apm.user.id', userId);
}

// ✅ Good: Use default values
span.setAttribute('apm.retry.count', retryCount || 0);

// ✅ Good: Convert to supported types
span.setAttribute('apm.timestamp', new Date().toISOString()); // Convert Date to string

// ❌ Bad: Setting undefined values
span.setAttribute('apm.user.id', req.user?.id); // May be undefined
```

---

## 5. Runtime Execution and Initialization

The method of initializing the instrumentation depends on whether you use **auto-instrumentation** or **manual SDK initialization**. Both reference projects use auto-instrumentation for ease of use.

### 5.1 Auto-Instrumentation (Recommended)

The easiest way to instrument a Node.js application is using the `@opentelemetry/auto-instrumentations-node` package. This automatically instruments common libraries like HTTP, Express, PostgreSQL, etc.

#### Prerequisites

**Installation:**
```bash
npm install @opentelemetry/api
npm install @opentelemetry/auto-instrumentations-node
npm install @opentelemetry/sdk-trace-node
npm install @opentelemetry/sdk-trace-base
npm install @opentelemetry/exporter-trace-otlp-http
npm install @opentelemetry/resources
npm install @opentelemetry/semantic-conventions
```

#### Initialization File

Create a `tracing.js` file in your project root:

```javascript
const { NodeTracerProvider } = require('@opentelemetry/sdk-trace-node');
const { registerInstrumentations } = require('@opentelemetry/instrumentation');
const { getNodeAutoInstrumentations } = require('@opentelemetry/auto-instrumentations-node');
const { BatchSpanProcessor } = require('@opentelemetry/sdk-trace-base');
const { OTLPTraceExporter } = require('@opentelemetry/exporter-trace-otlp-http');
const { Resource } = require('@opentelemetry/resources');
const { SemanticResourceAttributes } = require('@opentelemetry/semantic-conventions');

// Create a tracer provider with resource attributes
const provider = new NodeTracerProvider({
  resource: new Resource({
    [SemanticResourceAttributes.SERVICE_NAME]: process.env.SERVICE_NAME || 'my-nodejs-service',
    [SemanticResourceAttributes.SERVICE_VERSION]: process.env.SERVICE_VERSION || '1.0.0',
    [SemanticResourceAttributes.DEPLOYMENT_ENVIRONMENT]: process.env.NODE_ENV || 'development',
  }),
});

// Configure OTLP exporter
const exporter = new OTLPTraceExporter({
  url: process.env.OTEL_EXPORTER_OTLP_ENDPOINT || 'http://localhost:4318/v1/traces',
  headers: {
    // Add custom headers if needed (e.g., authentication)
  },
});

// Add batch span processor for better performance
provider.addSpanProcessor(new BatchSpanProcessor(exporter, {
  maxQueueSize: 2048,
  maxExportBatchSize: 512,
  scheduledDelayMillis: 5000,
}));

// Register the provider globally
provider.register();

// Register auto-instrumentations
registerInstrumentations({
  instrumentations: [
    getNodeAutoInstrumentations({
      // Enable/disable specific instrumentations
      '@opentelemetry/instrumentation-http': { enabled: true },
      '@opentelemetry/instrumentation-express': { enabled: true },
      '@opentelemetry/instrumentation-pg': { enabled: true },
      '@opentelemetry/instrumentation-fs': { enabled: false }, // Disable file system instrumentation
    }),
  ],
});

console.log('✅ OpenTelemetry tracing initialized');
console.log(`📊 Service: ${process.env.SERVICE_NAME || 'my-nodejs-service'}`);
console.log(`🔗 Exporter: ${process.env.OTEL_EXPORTER_OTLP_ENDPOINT || 'http://localhost:4318/v1/traces'}`);
```

#### Running the Application

**Option 1: Require the tracing file at startup (Recommended)**
```bash
node -r ./tracing.js server.js
```

**Option 2: Import at the top of your main file**
```javascript
// In server.js (MUST be the first import)
require('./tracing');

const express = require('express');
const app = express();

// ... rest of your application
```

**Option 3: Using npm scripts**
```json
{
  "scripts": {
    "start": "node -r ./tracing.js server.js",
    "dev": "nodemon -r ./tracing.js server.js"
  }
}
```

### 5.2 Environment Variables

Configure OpenTelemetry using environment variables:

```bash
# Service identification
export SERVICE_NAME=my-nodejs-service
export SERVICE_VERSION=1.0.0
export NODE_ENV=production

# OTLP Exporter endpoint
export OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4318/v1/traces

# Optional: Sampling configuration
export OTEL_TRACES_SAMPLER=traceidratio
export OTEL_TRACES_SAMPLER_ARG=0.1  # 10% sampling
```

### 5.3 Verification

After starting your application, verify that tracing is working:

1. **Check console output** for initialization messages
2. **Make a test request** to your application
3. **Check your observability backend** (Jaeger, Zipkin, etc.) for traces
4. **Verify custom attributes** are present in the spans

