# Custom/Business Specific Attribute Injection Strategies for PHP Runtime

> **Document Type:** Proof of Concept (POC)
> **Project:** PHP Custom Attribute
> **Last Verified:** January 13, 2026
> **Status:** Verified & Implemented
> **Testing Environment PHP Version:** 8.3.6

---

## 1. Overview

This document details the findings and implementation strategies for injecting custom business attributes into OpenTelemetry traces in a PHP runtime environment. Across all methods described below, traces were generated correctly, attributes were appended to the correct spans, and a wide range of data types (strings, integers, floats, booleans, arrays) were supported and visible in the UI.

Reference implementations were verified using Sample PHP applications located in the `otelapi` and `oteltracer` directories.

---

## 2. Approach 1: API-Based Span Enrichment (Recommended Approach)

This approach uses the core OpenTelemetry API to programmatically add attributes to the currently active span at any point in the code execution.

### 2.1 Description

This method relies on `Span::getCurrent()->setAttribute()`. To simplify usage and ensure type safety, we implemented a utility class `MotadataDynamicInstrumentation`.

**Strengths:**
*   **Dynamic:** Attributes can be added at any point (start, middle, or end of method).
*   **Flexible:** Can capture local variables, database results, and calculated values.
*   **Span-Agnostic:** Works regardless of how the span was created (auto-instrumentation or manual).

**Limitations:**
*   Requires an active span. Attribute injection is limited to OpenTelemetry-instrumented execution paths; in non-instrumented or unsupported contexts (such as background threads without OTel context), no span exists and attributes are therefore ignored unless a new span is explicitly created.

### 2.2 Prerequisites

**Dependencies:**
The core OpenTelemetry SDK and API packages are required.

**Composer:**
```bash
composer require open-telemetry/sdk
composer require open-telemetry/exporter-otlp
```

**composer.json:**
```json
{
  "require": {
    "php": ">=8.0",
    "open-telemetry/sdk": "^1.10",
    "open-telemetry/exporter-otlp": "^1.3"
  }
}
```

### 2.3 Client-Side Implementation

Clients should include the `MotadataDynamicInstrumentation` utility class in their project to handle null-safety and naming conventions.

**Step 1: Add the Utility Class**
(See `otelapi/src/Helpers/MotadataDynamicInstrumentation.php` in the project for full source).

**Step 2: Instrument Code**
```php
use App\Helpers\MotadataDynamicInstrumentation;

function handleOrder($orderId) {
    // ... business logic ...
    $user = $database->getUser();

    // Inject attributes dynamically at runtime
    // Note: The utility automatically adds the 'apm.' prefix if missing.
    MotadataDynamicInstrumentation::setInt("user.id", $user->id);
    MotadataDynamicInstrumentation::setString("user.email", $user->email);
    MotadataDynamicInstrumentation::setFloat("order.total", calculateTotal());
    MotadataDynamicInstrumentation::setStringArray("order.items", getItemNames());
}
```

### 2.4 MotadataDynamicInstrumentation Utility Reference

This section explains the internal behavior of the `MotadataDynamicInstrumentation` utility class used in the API-Based instrumentation method.

#### What is happening inside `MotadataDynamicInstrumentation`?

The `MotadataDynamicInstrumentation` class acts as a **safe wrapper** around the standard OpenTelemetry `Span::getCurrent()->setAttribute()` API. Its primary goal is to prevent runtime exceptions and enforce consistency without cluttering business logic.

#### Key Internal Mechanisms:

1.  **Automatic Prefixing:**
    *   Every attribute key passed to the utility is checked.
    *   If it doesn't already start with `apm.`, the prefix is automatically prepended.
    *   *Example:* `setString("user.id", ...)` becomes `apm.user.id` in the trace.

2.  **Null Safety:**
    *   The class explicitly checks for `null` keys and values.
    *   If a key or value is `null`, the operation is **silently ignored**. No exceptions are thrown, ensuring that telemetry code never crashes the application.

3.  **Type Handling:**
    *   **Boolean** values are handled by the `set()` method.
    *   **Integer** values are handled by the `setInt()` method.
    *   **Float** values are handled by the `setFloat()` method.
    *   **String** values are handled by the `setString()` method.
    *   **Arrays** are handled by type-specific methods: `setBoolArray()`, `setIntArray()`, `setFloatArray()`, and `setStringArray()`.
    *   Empty arrays are silently ignored (not added to the span) to reduce noise in telemetry data.

4.  **Error Suppression:**
    *   All internal calls are wrapped in `try-catch` blocks that swallow exceptions. This guarantees that even if the OpenTelemetry API fails, the application flow remains uninterrupted.

#### Minimal Code Reference

```php
// Simplified view of what happens internally
public static function setString(?string $key, ?string $value): void
{
    if ($key === null || $value === null) return; // 1. Null check
    try {
        $finalKey = str_starts_with($key, "apm.") ? $key : "apm." . $key; // 2. Prefixing
        $span = Span::getCurrent(); // 3. Get active span
        if ($span->isRecording()) {
            $span->setAttribute($finalKey, $value); // 4. OTEL Call
        }
    } catch (\Throwable $exception) {
        // 5. Safety: Ignore all errors
    }
}
```

**Reference Implementation:**
See `otelapi/src/Helpers/MotadataDynamicInstrumentation.php` for the complete implementation.

**Usage Example:**
See `otelapi/src/Controllers/UserController.php` and `otelapi/src/Controllers/DatatypeTestController.php` for practical usage examples.

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
The core OpenTelemetry SDK and API packages are required.

**Composer:**
```bash
composer require open-telemetry/sdk
composer require open-telemetry/exporter-otlp
```

**composer.json:**
```json
{
  "require": {
    "php": ">=8.0",
    "open-telemetry/sdk": "^1.10",
    "open-telemetry/exporter-otlp": "^1.3"
  }
}
```

### 3.3 Client-Side Implementation

The client must obtain a tracer and manage span lifecycle explicitly.

**Example: Creating a Child Span**
```php
use OpenTelemetry\API\Globals;
use OpenTelemetry\API\Trace\SpanKind;
use OpenTelemetry\Context\Context;

class OrderService {
    public function processOrder() {
        // Get tracer from global provider
        $tracer = Globals::tracerProvider()->getTracer('motadata.custom.instrumentatio');

        // Create span with parent context
        $validationSpan = $tracer
            ->spanBuilder('user.validation')
            ->setParent(Context::getCurrent())
            ->setSpanKind(SpanKind::KIND_INTERNAL)
            ->startSpan();

        // Set custom attributes
        $validationSpan->setAttribute('apm.user.username', $username);
        $validationSpan->setAttribute('apm.operation.type', 'validation');

        // Activate the span
        $scope = $validationSpan->storeInContext(Context::getCurrent())->activate();

        try {
            // ... business logic ...
            $validationSpan->setAttribute('apm.validation.result', 'passed');
        } finally {
            // CRITICAL: Must end the span!
            $validationSpan->end();
            $scope->detach();
        }
    }
}
```

### 3.4 Advanced Configuration: SpanKind and Root Spans

When manually creating spans, you have fine-grained control over the span's characteristics.

#### Creating a Root Span (New Trace)
By default, `spanBuilder()` creates a child of the currently active span. To start a completely new trace (a "root" span), use `setParent(false)`.

```php
use OpenTelemetry\API\Globals;
use OpenTelemetry\API\Trace\SpanKind;
use OpenTelemetry\Context\Context;

$tracer = Globals::tracerProvider()->getTracer('my-service', '1.0.0');

// Create a root span (new trace, no parent)
$span = $tracer
    ->spanBuilder('background-job')
    ->setParent(false)
    ->setSpanKind(SpanKind::KIND_INTERNAL)
    ->startSpan();

$scope = $span->storeInContext(Context::getCurrent())->activate();

try {
    $span->setAttribute('apm.job.type', 'cleanup');
    // ... business logic ...
} finally {
    $span->end();
    $scope->detach();
}
```

#### SpanKind Reference
The `SpanKind` enum specifies the relationship between spans in addition to the parent/child relationship. This helps visualization tools understand the nature of the operation.

| SpanKind | Description |
| :--- | :--- |
| **KIND_INTERNAL** | Default value. Indicates that the span is used internally within the application (e.g., a method call). |
| **KIND_SERVER** | Indicates that the span covers server-side handling of an RPC or other remote request. |
| **KIND_CLIENT** | Indicates that the span covers the client-side wrapper around an RPC or other remote request. |
| **KIND_PRODUCER** | Indicates that the span describes a producer sending a message to a broker. There is no direct critical path latency relationship between producer and consumer spans. |
| **KIND_CONSUMER** | Indicates that the span describes a consumer receiving a message from a broker. |

**Reference:** [OpenTelemetry PHP Instrumentation](https://opentelemetry.io/docs/languages/php/instrumentation/)

### 3.5 API Methods Reference

This section provides a detailed reference for the key interfaces and methods used in manual instrumentation.

#### `Tracer` Interface
*Full Documentation: [OpenTelemetry PHP Instrumentation - Acquiring a Tracer](https://opentelemetry.io/docs/languages/php/instrumentation/#acquiring-a-tracer)*

| Method | Description |
| :--- | :--- |
| `spanBuilder(name)` | Creates a new span builder. Returns a `SpanBuilder` instance that can be configured before starting the span. **Recommended for most use cases.** |

#### `Span` Interface
*Full Documentation: [OpenTelemetry PHP Instrumentation - Create Spans](https://opentelemetry.io/docs/languages/php/instrumentation/#create-spans)*

| Method | Description |
| :--- | :--- |
| `setAttribute(key, value)` | Adds or updates a single attribute on the span. Supports string, int, float, bool, and arrays. |
| `setAttributes(attributes)` | Adds or updates multiple attributes at once from an associative array. |
| `addEvent(name, attributes?)` | Adds a time-stamped event (log) to the span. Useful for capturing significant moments within a span's lifetime. |
| `recordException(exception, attributes?)` | Records details of an exception as a special, structured event on the span. Includes stack trace and error details. |
| `setStatus(statusCode, description?)` | Sets the final status of the span (OK or ERROR). An ERROR status will typically cause the trace to be highlighted. |
| `updateName(name)` | Updates the span's name after it has started. Use sparingly. |
| `end(endTime?)` | Marks the end of the span's execution. **This is mandatory for every span you start manually.** Failure to call `end()` will result in memory leaks and broken traces. |
| `isRecording()` | Returns `true` if the span is recording and sending data. Useful for avoiding expensive attribute calculations if the trace is not being sampled. |
| `spanContext()` | Returns the immutable `SpanContext` (containing the Trace ID and Span ID) of this span. |

---

## 4. Data Type Support Summary

Both methods support standard OpenTelemetry attribute types. The `MotadataDynamicInstrumentation` utility specifically handles type safety and automatic prefixing.

| Category | Supported PHP Types | Behavior |
| :--- | :--- | :--- |
| **Text** | `string` | Stored as String. |
| **Integer** | `int` | Stored as Integer (64-bit signed). |
| **Float** | `float` | Stored as Float (IEEE 754 double precision). |
| **Boolean** | `bool` | Stored as Boolean. |
| **Lists** | `array<bool>`, `array<int>`, `array<float>`, `array<string>` | Stored as Arrays (homogeneous only). |

**Note:** OpenTelemetry PHP SDK requires homogeneous arrays (all elements must be of the same type).

**Reference:** See `otelapi/src/Controllers/DatatypeTestController.php` for comprehensive datatype testing examples.


---

## 5. Runtime Execution (Initialization)

The method of initializing the instrumentation remains **identical to Zero-Code Instrumentation**. You must still initialize OpenTelemetry at application startup.

The only difference is that the **client application code has been modified** to capture specific attributes using the methods described above.

---

## 6. Resources & Verification

**GitHub Repository:** [**Sample PHP Application**](https://github.com/motadata2025/Custom-Attribute-Instrumentation-Sample-Apps/tree/main/Sample%20Apps/PHP%20Custom%20Attribute)

**Verification Snapshots:** [**View Testing Snapshots on GitHub**](https://github.com/motadata2025/Custom-Attribute-Instrumentation-Sample-Apps/tree/main/Sample%20Apps/PHP%20Custom%20Attribute/Testing%20Snapshots)

**Custom Attribute Supported Datatype:** [**Supported Data Types**](https://motadataindia-my.sharepoint.com/:x:/r/personal/shiven_patel_motadata_com/_layouts/15/Doc.aspx?sourcedoc=%7BA95ADCCD-C7B9-4612-9BC9-5CFE1693A12D%7D&file=Custom%20Attribute%20Support.xlsx&action=default&mobileredirect=true&DefaultItemOpen=1&wdOrigin=APPHOME-WEB.DIRECT%2CAPPHOME-WEB.FILEBROWSER.RECENT&wdPreviousSession=08f9a629-a27d-48d1-84b4-ae788cafe875&wdPreviousSessionSrc=AppHomeWeb&ct=1765894539141)

---

> **Disclaimer:**
> This documentation and the associated findings are based on sample tests performed on sample PHP applications. Implementation details in a production environment may vary depending on specific framework versions, existing instrumentation, and architectural constraints. Naming conventions, dependency versions, and integration points should be adapted as needed.
