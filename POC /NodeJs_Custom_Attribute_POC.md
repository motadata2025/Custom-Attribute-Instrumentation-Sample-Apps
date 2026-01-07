# Custom/Business Specific Attribute Injection Strategies for Node.js Runtime

> **Document Type:** Proof of Concept (POC)
> **Project:** Node.js Custom Attribute
> **Last Verified:** December 29, 2026
> **Status:** Verified & Implemented
> **Testing Environment Node.js Version:** 24.12

---

## 1. Overview

This document details the findings and implementation strategies for injecting custom business attributes into OpenTelemetry traces in a Node.js runtime environment. Across all methods described below, traces were generated correctly, attributes were appended to the correct spans, and a wide range of data types (strings, numbers, booleans, arrays) were supported and visible in the UI.

Reference implementations were verified using Sample Node.js applications.

---

## 2. Approach 1: API-Based Span Enrichment (Recommended Approach)

This approach uses the core OpenTelemetry API to programmatically add attributes to the currently active span at any point in the code execution.

### 2.1 Description

This method relies on `trace.getActiveSpan().setAttribute()`. To simplify usage and ensure type safety, we implemented a utility class `MotadataDynamicInstrumentation`.

**Strengths:**
*   **Dynamic:** Attributes can be added at any point (start, middle, or end of method).
*   **Flexible:** Can capture local variables, database results, and calculated values.
*   **Span-Agnostic:** Works regardless of how the span was created (auto-instrumentation or manual).

**Limitations:**
*   Requires an active span. Attribute injection is limited to OpenTelemetry-instrumented execution paths; in non-instrumented or unsupported contexts (such as background threads without OTel context), no span exists and attributes are therefore ignored unless a new span is explicitly created.

### 2.2 Prerequisites

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

### 2.3 Client-Side Implementation

Clients should include the `MotadataDynamicInstrumentation` utility class in their project to handle null-safety and naming conventions.

**Step 1: Add the Utility Class**
(See `otelapi/util/MotadataDynamicInstrumentation.js` in the project for full source).

**Step 2: Instrument Code**
```javascript
const MotadataDynamicInstrumentation = require('./util/MotadataDynamicInstrumentation');

function handleOrder(orderId) {
    // ... business logic ...
    const user = database.getUser();

    // Inject attributes dynamically at runtime
    // Note: The utility automatically adds the 'apm.' prefix if missing.
    MotadataDynamicInstrumentation.set("user.id", user.id);
    MotadataDynamicInstrumentation.set("user.email", user.email);
    MotadataDynamicInstrumentation.set("order.total", calculateTotal());
    MotadataDynamicInstrumentation.setStringList("order.items", getItemNames());
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

2.  **Null Safety:**
    *   The class explicitly checks for `null` and `undefined` keys and values.
    *   If a key or value is `null` or `undefined`, the operation is **silently ignored**. No exceptions are thrown, ensuring that telemetry code never crashes the application.

3.  **Type Handling:**
    *   **Strings, Numbers, Booleans** are handled directly by the `set()` method with automatic type detection.
    *   **Arrays** are handled by type-specific methods: `setBooleanList()`, `setNumberList()`, and `setStringList()`.
    *   Empty arrays are silently ignored (not added to the span) to reduce noise in telemetry data.

4.  **Error Suppression:**
    *   All internal calls are wrapped in `try-catch` blocks that swallow exceptions. This guarantees that even if the OpenTelemetry API fails, the application flow remains uninterrupted.

#### Minimal Code Reference

```javascript
// Simplified view of what happens internally
static set(key, value) {
    if (key == null || value == null) return; // 1. Null check
    try {
        const finalKey = key.startsWith("apm.") ? key : "apm." + key; // 2. Prefixing
        const span = trace.getActiveSpan(); // 3. Get active span
        if (span) {
            span.setAttribute(finalKey, value); // 4. OTEL Call
        }
    } catch (exception) {
        // 5. Safety: Ignore all errors
    }
}
```

---

## 3. Approach 2: Manual Tracer and Span Creation

This approach involves manually obtaining a `Tracer` instance and managing the span lifecycle (start, scope, end) explicitly.

### 3.1 Description

This provides the most control, allowing developers to create new root traces, manage complex parent-child relationships, and handle asynchronous context propagation.

**Strengths:**
*   **Complete Control:** Can create new root spans (separate traces) or custom hierarchies.
*   **Precise Lifecycle:** Exact control over when a span starts and ends.

**Limitations:**
*   **Verbose:** Requires significant boilerplate code.
*   **Complex:** Requires careful lifecycle handling to ensure spans are ended, otherwise memory leaks or broken traces may occur.

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

The client must obtain a tracer and manage span lifecycle explicitly.

**Example: Creating a Root Span**
```javascript
const { trace, SpanStatusCode } = require('@opentelemetry/api');

class OrderService {
    constructor() {
        this.tracer = trace.getTracer("motadata.custom.instrumentation");
    }

    processOrder() {
        // Create a new span
        const span = this.tracer.startSpan("manual-process-order");

        try {
            span.setAttribute("apm.custom.manual.attr", "value");

            // ... business logic ...

        } catch (error) {
            span.recordException(error);
            throw error;
        } finally {
            // CRITICAL: Must end the span!
            span.end();
        }
    }
}
```

### 3.4 Advanced Configuration: SpanKind and Root Spans

When manually creating spans, you have fine-grained control over the span's characteristics.

#### Creating a Root Span (New Trace)
By default, `startSpan()` creates a child of the currently active span. To start a completely new trace (a "root" span), use `ROOT_CONTEXT`.

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

### 3.5 API Methods Reference

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

---

## 4. Data Type Support Summary

Both methods support standard OpenTelemetry attribute types. The `MotadataDynamicInstrumentation` utility specifically handles type safety and automatic prefixing.

| Category | Supported Node.js Types | Behavior |
| :--- | :--- | :--- |
| **Text** | `string` | Stored as String. |
| **Number** | `number` (integer or float) | Stored as Number (IEEE 754 double precision). |
| **Boolean** | `boolean` | Stored as Boolean. |
| **Lists** | `Array<string>`, `Array<number>`, `Array<boolean>` | Stored as Arrays (homogeneous only). |

---

## 5. Runtime Execution (Initialization)

The method of initializing the instrumentation remains **identical to Zero-Code Instrumentation**. You must still initialize OpenTelemetry at application startup.

The only difference is that the **client application code has been modified** to capture specific attributes using the methods described above.

---

## 6. Resources & Verification

**GitHub Repository:** [**Sample Node.js Application**](https://github.com/motadata2025/Custom-Attribute-Instrumentation-Sample-Apps/tree/main/Sample%20Apps/NodeJs%20Custom%20Attribute)

**Verification Snapshots:** [**View Testing Snapshots on GitHub**](https://github.com/motadata2025/Custom-Attribute-Instrumentation-Sample-Apps/tree/main/Sample%20Apps/NodeJs%20Custom%20Attribute/Testing%20Snapshots)

**Custom Attribute Supported Datatype:** [**Supported Data Types**](https://motadataindia-my.sharepoint.com/:x:/r/personal/shiven_patel_motadata_com/_layouts/15/Doc.aspx?sourcedoc=%7BA95ADCCD-C7B9-4612-9BC9-5CFE1693A12D%7D&file=Custom%20Attribute%20Support.xlsx&action=default&mobileredirect=true&DefaultItemOpen=1&wdOrigin=APPHOME-WEB.DIRECT%2CAPPHOME-WEB.FILEBROWSER.RECENT&wdPreviousSession=08f9a629-a27d-48d1-84b4-ae788cafe875&wdPreviousSessionSrc=AppHomeWeb&ct=1765894539141)

---

> **Disclaimer:**
> This documentation and the associated findings are based on sample tests performed on a sample Node.js application. Implementation details in a production environment may vary depending on specific framework versions, existing instrumentation, and architectural constraints. Naming conventions, dependency versions, and integration points should be adapted as needed.

