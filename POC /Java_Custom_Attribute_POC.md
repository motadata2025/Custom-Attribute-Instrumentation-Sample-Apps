# Custom/Business Specific Attribute Injection Strategies for Java Runtime

> **Document Type:** Proof of Concept (POC)
> **Project:** Java Custom Attribute
> **Last Verified:** December 11, 2025
> **Status:** Verified & Implemented
> **Testing Environment Java Version:** 21

---

## 1. Overview

This document details the findings and implementation strategies for injecting custom business attributes into OpenTelemetry traces in a Java runtime environment. Across all methods described below, traces were generated correctly, attributes were appended to the correct spans, and a wide range of data types (strings, numbers, booleans, lists) were supported and visible in the UI.

Reference implementations were verified using Sample Java applications.

---

## 2. Approach 1: Annotation-Based Instrumentation

This approach uses declarative annotations to automatically generate spans and capture method parameters as attributes. It is the least intrusive method for capturing input data.

### 2.1 Description
*   **`@WithSpan`**: Creates a new child span for the annotated method. Useful for breaking down operations into smaller traceable units.
*   **`@AddingSpanAttributes`**: Does not create a new span. Instead, it enriches the *currently active* span (e.g., one created by an upstream HTTP server). Suitable for adding business metadata without altering the trace structure.
*   **`@SpanAttribute`**: Applied to method parameters to automatically map input values as attributes on the span.

**Strengths:**
*   Clean, declarative code.
*   Automatic span creation and context propagation.

**Limitations:**
*   Can only capture attributes available at method entry (parameters).
*   Cannot capture values computed *inside* the method body or return values easily.

### 2.2 Prerequisites
**Dependencies:**
Ensure the `opentelemetry-instrumentation-annotations` library is added to your project.

**Maven:**
```xml
<dependency>
  <groupId>io.opentelemetry.instrumentation</groupId>
  <artifactId>opentelemetry-instrumentation-annotations</artifactId>
  <version>2.11.0</version>
</dependency>
```

**Gradle:**
```groovy
implementation 'io.opentelemetry.instrumentation:opentelemetry-instrumentation-annotations:2.11.0'
```

### 2.3 Client-Side Implementation
The client simply annotates their methods. No manual span lifecycle management is required.

**Example 1: Creating a new span with parameters**
```java
import io.opentelemetry.instrumentation.annotations.WithSpan;
import io.opentelemetry.instrumentation.annotations.SpanAttribute;

public class UserService {

    @WithSpan("process-user")
    public void processUser(
        @SpanAttribute("apm.user.id") String userId,
        @SpanAttribute("apm.user.is_vip") boolean isVip
    ) {
        // Method logic...
        // 'apm.user.id' and 'apm.user.is_vip' are automatically added to the 'process-user' span.
    }
}
```

**Example 2: Enriching an existing span**
```java
import io.opentelemetry.instrumentation.annotations.AddingSpanAttributes;
import io.opentelemetry.instrumentation.annotations.SpanAttribute;

public class PaymentHandler {

    @AddingSpanAttributes
    public void validatePayment(@SpanAttribute("apm.payment.amount") double amount) {
        // Adds 'apm.payment.amount' to the CURRENT active span (e.g., the Controller span).
        // Does NOT create a new span.
    }
}
```

---

## 3. Approach 2: API-Based Span Enrichment (Recommended Approach)

This approach uses the core OpenTelemetry API to programmatically add attributes to the currently active span at any point in the code execution.

### 3.1 Description
This method relies on `Span.current().setAttribute()`. To simplify usage and ensure type safety, we implemented a utility class `MotadataDynamicInstrumentation`.

**Strengths:**
*   **Dynamic:** Attributes can be added at any point (start, middle, or end of method).
*   **Flexible:** Can capture local variables, database results, and calculated values.
*   **Span-Agnostic:** Works regardless of how the span was created (auto-instrumentation, annotation, or manual).

**Limitations:**
*   Requires an active span. Attribute injection is limited to OpenTelemetry-instrumented execution paths; in non-instrumented or unsupported contexts (such as background threads without OTel context), no span exists and attributes are therefore ignored unless a new span is explicitly created.

### 3.2 Prerequisites
**Dependencies:**
The core API and Context libraries are required.

**Maven:**
```xml
<dependency>
  <groupId>io.opentelemetry</groupId>
  <artifactId>opentelemetry-api</artifactId>
  <version>1.45.0</version>
</dependency>
<dependency>
  <groupId>io.opentelemetry</groupId>
  <artifactId>opentelemetry-context</artifactId>
  <version>1.45.0</version>
</dependency>
```

**Gradle:**
```groovy
implementation 'io.opentelemetry:opentelemetry-api:1.45.0'
implementation 'io.opentelemetry:opentelemetry-context:1.45.0'
```

### 3.3 Client-Side Implementation
Clients should include the `MotadataDynamicInstrumentation` utility class in their project to handle null-safety and naming conventions.

**Step 1: Add the Utility Class**
(See `src/OtelApi/util/MotadataDynamicInstrumentation.java` in the project for full source).

**Step 2: Instrument Code**
```java
import OtelApi.util.MotadataDynamicInstrumentation;

public void handleOrder(String orderId) {
    // ... business logic ...
    User user = database.getUser();

    // Inject attributes dynamically at runtime
    // Note: The utility automatically adds the 'apm.' prefix if missing.
    MotadataDynamicInstrumentation.set("user.id", user.getId());
    MotadataDynamicInstrumentation.set("user.email", user.getEmail());
    MotadataDynamicInstrumentation.set("order.total", calculateTotal());
    MotadataDynamicInstrumentation.setStringList("order.items", getItemNames());
}
```

### 3.4 MotadataDynamicInstrumentation Utility Reference

This section explains the internal behavior of the `MotadataDynamicInstrumentation` utility class used in the API-Based instrumentation method.

#### What is happening inside `MotadataDynamicInstrumentation`?

The `MotadataDynamicInstrumentation` class acts as a **safe wrapper** around the standard OpenTelemetry `Span.current().setAttribute()` API. Its primary goal is to prevent runtime exceptions and enforce consistency without cluttering business logic.

#### Key Internal Mechanisms:

1.  **Automatic Prefixing:**
    *   Every attribute key passed to the utility is checked.
    *   If it doesn't already start with `apm.`, the prefix is automatically prepended.
    *   *Example:* `set("user.id", ...)` becomes `apm.user.id` in the trace.

2.  **Null Safety:**
    *   The class explicitly checks for `null` keys and values.
    *   If a key or value is `null`, the operation is **silently ignored**. No exceptions are thrown, ensuring that telemetry code never crashes the application.

3.  **Type Handling & Widening:**
    *   **Integers** are automatically converted to `long` (as OpenTelemetry only supports `long` for integer types).
    *   **Floats** are automatically converted to `double`.
    *   **Boxed Types** (Integer, Double, Boolean) are safely unboxed, with null checks to prevent `NullPointerException`.

4.  **List Support:**
    *   Type-specific list methods are provided: `setBooleanList`, `setDoubleList`, `setIntegerList`, `setLongList`, and `setStringList`.
    *   Each method uses the correct OpenTelemetry `AttributeKey` type (e.g., `stringArrayKey`, `longArrayKey`).
    *   `setIntegerList` automatically converts `List<Integer>` to `List<Long>` to satisfy OTEL requirements.

5.  **Error Suppression:**
    *   All internal OTEL calls are wrapped in `try-catch` blocks that swallow exceptions. This guarantees that even if the OTEL API fails (e.g., span is closed), the application flow remains uninterrupted.

#### Minimal Code Reference

```java
// Simplified view of what happens internally
public static void set(String key, String value) {
    if (key == null || value == null) return; // 1. Null check
    try {
        String finalKey = key.startsWith("apm.") ? key : "apm." + key; // 2. Prefixing
        Span.current().setAttribute(finalKey, value); // 3. OTEL Call
    } catch (Exception ignored) {
        // 4. Safety: Ignore all errors
    }
}
```

---

## 4. Approach 3: Manual Tracer and Span Creation

This approach involves manually obtaining a `Tracer` instance and managing the span lifecycle (start, scope, end) explicitly.

### 4.1 Description
This provides the most control, allowing developers to create new root traces, manage complex parent-child relationships, and handle asynchronous context propagation.

**Strengths:**
*   **Complete Control:** Can create new root spans (separate traces) or custom hierarchies.
*   **Precise Lifecycle:** Exact control over when a span starts and ends.

**Limitations:**
*   **Verbose:** Requires significant boilerplate code.
*   **Complex:** Requires careful `try-finally` blocks to ensure spans are closed, otherwise memory leaks or broken traces may occur.

### 4.2 Prerequisites
**Dependencies:**
The core API and Context libraries are required.

**Maven:**
```xml
<dependency>
  <groupId>io.opentelemetry</groupId>
  <artifactId>opentelemetry-api</artifactId>
  <version>1.45.0</version>
</dependency>
<dependency>
  <groupId>io.opentelemetry</groupId>
  <artifactId>opentelemetry-context</artifactId>
  <version>1.45.0</version>
</dependency>
```

**Gradle:**
```groovy
implementation 'io.opentelemetry:opentelemetry-api:1.45.0'
implementation 'io.opentelemetry:opentelemetry-context:1.45.0'
```

### 4.3 Client-Side Implementation
The client must obtain a tracer and wrap code in scope management blocks.

**Example: Creating a Root Span**
```java
import io.opentelemetry.api.GlobalOpenTelemetry;
import io.opentelemetry.api.trace.Span;
import io.opentelemetry.api.trace.Tracer;
import io.opentelemetry.api.trace.SpanKind;
import io.opentelemetry.context.Scope;

public class OrderService {
    private static final Tracer tracer = GlobalOpenTelemetry.getTracer("motadata.custom.instrumentation");

    public void processOrder() {
        // Create a new span
        Span span = tracer.spanBuilder("manual-process-order")
            .setSpanKind(SpanKind.SERVER) // Define the type of span
            .setNoParent() // Explicitly create a new root trace (no parent)
            .startSpan();

        // Make it the "current" span
        try (Scope scope = span.makeCurrent()) {
            span.setAttribute("apm.custom.manual.attr", "value");

            // ... business logic ...

        } catch (Exception e) {
            span.recordException(e);
            throw e;
        } finally {
            // CRITICAL: Must end the span!
            span.end();
        }
    }
}
```

### 4.4 Advanced Configuration: SpanKind and Root Spans

When manually creating spans, you have fine-grained control over the span's characteristics.

#### Creating a Root Span (`setNoParent`)
By default, `startSpan()` creates a child of the currently active span. To start a completely new trace (a "root" span), use `.setNoParent()`.

```java
Span rootSpan = tracer.spanBuilder("order.process")
        .setSpanKind(SpanKind.SERVER)
        .setNoParent()  // Creates a new trace (no parent)
        .startSpan();
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

### 4.5 API Methods Reference

This section provides a detailed reference for the key interfaces and methods used in manual instrumentation.

#### `Tracer` Interface
*Full Javadoc: [io.opentelemetry.api.trace.Tracer](https://www.javadoc.io/doc/io.opentelemetry/opentelemetry-api/latest/io/opentelemetry/api/trace/Tracer.html)*

| Method | Description |
| :--- | :--- |
| `spanBuilder(String name)` | Returns a `SpanBuilder` to configure and create a new span with the given name. This is the entry point for creating all manual spans. |

#### `SpanBuilder` Interface
*Full Javadoc: [io.opentelemetry.api.trace.SpanBuilder](https://www.javadoc.io/doc/io.opentelemetry/opentelemetry-api/latest/io/opentelemetry/api/trace/SpanBuilder.html)*

| Method | Description |
| :--- | :--- |
| `setParent(Context context)` | Sets the parent context explicitly. Useful for linking spans across threads or services. |
| `setNoParent()` | Explicitly sets the span as a root span (new trace), ignoring any active parent context. |
| `addLink(SpanContext spanContext)` | Adds a causal link to another span, such as a span in a batch process. |
| `setAttribute(String key, ...)` | Sets a single attribute before the span starts. Overloaded for all primitive types. |
| `setAllAttributes(Attributes attributes)` | Sets multiple attributes at once from a pre-built `Attributes` object. |
| `setSpanKind(SpanKind kind)` | Sets the `SpanKind` (e.g., SERVER, CLIENT) to describe the span's role. |
| `setStartTimestamp(...)` | Sets an explicit start timestamp for the span, overriding the default `now()`. |
| `startSpan()` | Creates and starts the `Span`. The span is created but not yet active in the current context. |

#### `Span` Interface
*Full Javadoc: [io.opentelemetry.api.trace.Span](https://www.javadoc.io/doc/io.opentelemetry/opentelemetry-api/latest/io/opentelemetry/api/trace/Span.html)*

| Method | Description |
| :--- | :--- |
| `setAttribute(String key, ...)` | Adds or updates a single attribute on the span *after* it has started. |
| `setAllAttributes(Attributes attributes)` | Adds or updates multiple attributes at once *after* the span has started. |
| `addEvent(String name, ...)` | Adds a time-stamped event (log) to the span. Useful for capturing significant moments within a span's lifetime. |
| `recordException(Throwable t, ...)` | Records details of an exception as a special, structured event on the span. |
| `setStatus(StatusCode code, ...)` | Sets the final status of the span (e.g., OK, ERROR). An ERROR status will typically cause the trace to be highlighted. |
| `updateName(String name)` | Updates the span's name after it has started. Use sparingly. |
| `end()` | Marks the end of the span's execution. **This is mandatory for every span you start.** Failure to call `end()` will result in memory leaks and broken traces. |
| `makeCurrent()` | Makes this span the active one in the current context, returning a `Scope` that **must be closed** (usually via a `try-with-resources` block). |
| `isRecording()` | Returns `true` if the span is recording and sending data. Useful for avoiding expensive attribute calculations if the trace is not being sampled. |
| `getSpanContext()` | Returns the immutable `SpanContext` (containing the Trace ID and Span ID) of this span. |

---

## 5. Data Type Support Summary

All three methods support standard OpenTelemetry attribute types. The `MotadataDynamicInstrumentation` utility specifically handles type safety and automatic widening.

| Category | Supported Java Types | Behavior |
| :--- | :--- | :--- |
| **Text** | `String` | Stored as String. |
| **Integer** | `int`, `Integer`, `long`, `Long` | All stored as **Long**. |
| **Decimal** | `float`, `Double`, `double` | All stored as **Double**. |
| **Boolean** | `boolean`, `Boolean` | Stored as Boolean. |
| **Lists** | `List<String>`, `List<Long>`, `List<Double>`, `List<Boolean>` | Stored as Arrays. `List<Integer>` is converted to `List<Long>`. |

---

## 6. Runtime Execution (Agent Attachment)

The method of initializing the instrumentation remains **identical to Zero-Code Instrumentation**. You must still attach the Motadata Java Agent at runtime.

The only difference is that the **client application code has been modified** to capture specific attributes using the methods described above.

---

## 7. Resources & Verification

**GitHub Repository:** [**Sample Java Application**](https://github.com/motadata2025/Custom-Attribute-Instrumentation-Sample-Apps/tree/main/Sample%20Apps/Java%20Custom%20Attribute)

**Verification Snapshots:** [**View Testing Snapshots on GitHub**](https://github.com/motadata2025/Custom-Attribute-Instrumentation-Sample-Apps/tree/main/Sample%20Apps/Java%20Custom%20Attribute/Testing%20Snapshots)

**Custom Attribute Supported Datatype:** [**Supported Data Types**](https://motadataindia-my.sharepoint.com/:x:/r/personal/shiven_patel_motadata_com/_layouts/15/Doc.aspx?sourcedoc=%7BA95ADCCD-C7B9-4612-9BC9-5CFE1693A12D%7D&file=Custom%20Attribute%20Support.xlsx&action=default&mobileredirect=true&DefaultItemOpen=1&wdOrigin=APPHOME-WEB.DIRECT%2CAPPHOME-WEB.FILEBROWSER.RECENT&wdPreviousSession=08f9a629-a27d-48d1-84b4-ae788cafe875&wdPreviousSessionSrc=AppHomeWeb&ct=1765894539141)

---

> **Disclaimer:**
> This documentation and the associated findings are based on sample tests performed on a sample Java application. Implementation details in a production environment may vary depending on specific framework versions, existing instrumentation, and architectural constraints. Naming conventions, dependency versions, and integration points should be adapted as needed.
