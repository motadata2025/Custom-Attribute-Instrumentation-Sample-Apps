# Custom/Business Specific Attribute Injection Strategies for Python Runtime

> **Document Type:** Proof of Concept (POC)
> **Project:** Python Custom Attribute
> **Last Verified:** December 23, 2025
> **Status:** Verified & Implemented
> **Python Version:** 3.12.3

---

## 1. Overview

This document details the findings and implementation strategies for injecting custom business attributes into OpenTelemetry traces in a Python runtime environment. Across all methods described below, traces were generated correctly, attributes were appended to the correct spans, and a wide range of data types (strings, numbers, booleans, lists) were supported and visible in the UI.

Reference implementations were verified using dummy Python applications.

---

## 2. Approach 1: Decorator-Based Instrumentation

This approach uses OpenTelemetry Python decorators to automatically create new spans and enrich them with custom attributes.

### 2.1 Description
*   **`@tracer.start_as_current_span()`**: Creates a new child span for the decorated function. Useful for breaking down business logic into smaller traceable units.
*   **`trace.get_current_span().set_attribute()`**: Inside decorated methods, this adds business-specific attributes to the span created by the decorator.

**Strengths:**
*   Clear parent–child span hierarchy.
*   Automatic span lifecycle management.

**Limitations:**
*   Attributes can only be captured for values available during function execution.
*   Creates additional spans, which may increase span volume and overhead.

### 2.2 Prerequisites
**Dependencies:**
Ensure the `opentelemetry-api` and `opentelemetry-sdk` libraries are installed.

**Pip:**
```bash
pip install opentelemetry-api opentelemetry-sdk
```

### 2.3 Client-Side Implementation

**Example:**
```python
from opentelemetry import trace

tracer = trace.get_tracer(__name__)

@tracer.start_as_current_span("process_user")
def process_user(user_id, is_vip):
    current_span = trace.get_current_span()
    current_span.set_attribute("apm.user.id", user_id)
    current_span.set_attribute("apm.user.is_vip", is_vip)
    # Method logic...
```

---

## 3. Approach 2: API-Based Span Enrichment (Recommended Approach)

This approach uses the OpenTelemetry Python API to enrich the currently active span without creating new spans. To simplify usage and ensure type safety, we implemented a utility class `MotadataDynamicInstrumentation`.

### 3.1 Description
This method relies on `trace.get_current_span().set_attribute()`.

**Strengths:**
*   **Dynamic:** Attributes can be added at any point during function execution.
*   **Efficient:** Does not create new spans; enriches spans created by auto-instrumentation (HTTP, DB, etc.).
*   **Minimal Overhead:** Ideal for high-throughput paths.
*   **Flexible:** Works with auto-instrumentation, decorator-based spans, or manually created spans.

**Limitations:**
*   Requires an active recording span. If the request is not traced (for example, unsupported frameworks or missing auto-instrumentation), `get_current_span()` returns a non-recording default span, and custom attributes are ignored and not exported.

### 3.2 Prerequisites
**Dependencies:**
The core API library is required.

**Pip:**
```bash
pip install opentelemetry-api
```

### 3.3 Client-Side Implementation
Clients should include the `MotadataDynamicInstrumentation` utility class in their project to handle null-safety and naming conventions.

**Step 1: Add the Utility Class**
(See `otelapi/util/MotadataDynamicInstrumentation.py` in the project for full source).

**Step 2: Instrument Code**
```python
from otelapi.util.MotadataDynamicInstrumentation import MotadataDynamicInstrumentation

def handle_order(order_id):
    # ... business logic ...
    
    # Inject attributes dynamically at runtime
    # Note: The utility automatically adds the 'apm.' prefix if missing.
    MotadataDynamicInstrumentation.set("order.id", order_id)
    MotadataDynamicInstrumentation.set("order.total", calculate_total())
    MotadataDynamicInstrumentation.set_string_list("order.items", get_item_names())
```

### 3.4 MotadataDynamicInstrumentation Utility Reference

This section explains the internal behavior of the `MotadataDynamicInstrumentation` utility class used in the API-Based instrumentation method.

#### What is happening inside `MotadataDynamicInstrumentation`?

The `MotadataDynamicInstrumentation` class acts as a **safe wrapper** around the standard OpenTelemetry `trace.get_current_span().set_attribute()` API. Its primary goal is to prevent runtime exceptions and enforce consistency without cluttering business logic.

#### Key Internal Mechanisms:

1.  **Automatic Prefixing:**
    *   Every attribute key passed to the utility is checked.
    *   If it doesn't already start with `apm.`, the prefix is automatically prepended.
    *   *Example:* `set("user.id", ...)` becomes `apm.user.id` in the trace.

2.  **Null Safety:**
    *   The class explicitly checks for `None` keys and values.
    *   If a key or value is `None`, the operation is **silently ignored**. No exceptions are thrown, ensuring that telemetry code never crashes the application.

3.  **Type Handling:**
    *   Supports scalar types (`bool`, `int`, `float`, `str`) and list types (`bool`, `int`, `float`, `str`).
    *   Ensures that lists are properly formatted before being passed to OpenTelemetry.

4.  **Error Suppression:**
    *   All internal OTEL calls are wrapped in `try-except` blocks that swallow exceptions. This guarantees that even if the OTEL API fails (e.g., span is closed), the application flow remains uninterrupted.

#### Minimal Code Reference

```python
# Simplified view of what happens internally
class MotadataDynamicInstrumentation:
    _PREFIX = "apm."

    @staticmethod
    def set(key: str, value: any) -> None:
        if key is None or value is None:
            return
        
        # 1. Prefixing
        final_key = key if key.startswith(MotadataDynamicInstrumentation._PREFIX) else MotadataDynamicInstrumentation._PREFIX + key
        
        try:
            # 2. OTEL Call
            span = trace.get_current_span()
            if span.is_recording():
                span.set_attribute(final_key, value)
        except Exception:
            # 3. Safety: Ignore all errors
            pass
```

---

## 4. Approach 3: Manual Tracer and Span Creation

This approach involves manually obtaining a `Tracer` instance and managing the span lifecycle (start, context, end) explicitly using Python context managers.

### 4.1 Description
This provides the most control, allowing developers to create new root traces, manage complex parent-child relationships, and handle asynchronous context propagation. It is suitable for complex workflows where automatic or decorator-based instrumentation does not correctly capture logical business boundaries or execution flow.

**Strengths:**
*   **Complete Control:** Can create new root spans (separate traces) or custom hierarchies.
*   **Precise Lifecycle:** Exact control over when a span starts and ends through context managers.
*   **Complex Workflows:** Supports complex, multi-step or long-running business workflows.
*   **Flexibility:** Business attributes, events, and exception handling can be added at any stage of execution.

**Limitations:**
*   **Verbose:** Requires more boilerplate code compared to other methods.
*   **Lifecycle Management:** Requires careful context manager usage to ensure spans are properly closed, otherwise memory leaks or broken traces may occur.
*   **Overhead:** Higher span volume and potential performance overhead compared to API-based span enrichment.

### 4.2 Prerequisites
**Dependencies:**
The core API library is required.

**Pip:**
```bash
pip install opentelemetry-api
```

### 4.3 Client-Side Implementation
The client must obtain a tracer and wrap code in context manager blocks.

**Example: Creating a Child Span**
```python
from opentelemetry import trace
from opentelemetry.trace import SpanKind, Status, StatusCode

tracer = trace.get_tracer("motadata.custom.instrumentation", "1.0.0")

def process_order():
    # Create a new span using context manager
    with tracer.start_as_current_span(
        "manual-process-order",
        kind=SpanKind.INTERNAL  # Define the type of span
    ) as span:
        span.set_attribute("apm.custom.manual.attr", "value")
        span.set_attribute("apm.order.id", "12345")

        try:
            # ... business logic ...
            span.set_status(Status(StatusCode.OK))
        except Exception as e:
            span.record_exception(e)
            span.set_status(Status(StatusCode.ERROR, str(e)))
            raise
```

**Example: Creating a Root Span (New Trace)**
```python
from opentelemetry import trace, context
from opentelemetry.trace import SpanKind, Status, StatusCode

tracer = trace.get_tracer("motadata.custom.instrumentation", "1.0.0")

def process_background_job():
    # Create a new root span (no parent) by using an empty context
    ctx = context.Context()

    with tracer.start_as_current_span(
        "background-job-process",
        context=ctx,
        kind=SpanKind.INTERNAL
    ) as span:
        span.set_attribute("apm.job.type", "data_sync")
        span.set_attribute("apm.job.id", "job-456")

        try:
            # ... business logic ...
            span.set_status(Status(StatusCode.OK))
        except Exception as e:
            span.record_exception(e)
            span.set_status(Status(StatusCode.ERROR, str(e)))
            raise
```

### 4.4 Advanced Configuration: SpanKind and Span Options

When manually creating spans, you have fine-grained control over the span's characteristics.

#### SpanKind Reference
The `SpanKind` enum specifies the relationship between spans in addition to the parent/child relationship. This helps visualization tools understand the nature of the operation.

| SpanKind | Description |
| :--- | :--- |
| **INTERNAL** | Default value. Indicates that the span is used internally within the application (e.g., a method call). |
| **SERVER** | Indicates that the span covers server-side handling of an RPC or other remote request. |
| **CLIENT** | Indicates that the span covers the client-side wrapper around an RPC or other remote request. |
| **PRODUCER** | Indicates that the span describes a producer sending a message to a broker. There is no direct critical path latency relationship between producer and consumer spans. |
| **CONSUMER** | Indicates that the span describes a consumer receiving a message from a broker. |

**Example:**
```python
from opentelemetry.trace import SpanKind

# Server-side span
with tracer.start_as_current_span("handle-request", kind=SpanKind.SERVER) as span:
    # ... handle incoming request ...
    pass

# Client-side span
with tracer.start_as_current_span("http-call", kind=SpanKind.CLIENT) as span:
    # ... make outgoing HTTP request ...
    pass
```

#### Span Configuration Options
You can configure spans with additional options when creating them:

```python
from opentelemetry.trace import Link

# Create span with custom configuration
with tracer.start_as_current_span(
    "complex-operation",
    kind=SpanKind.INTERNAL,
    context=parent_context,  # Set explicit parent context
    attributes={"apm.operation.type": "batch"},  # Set initial attributes
    links=[Link(related_span_context, {"link.type": "follows"})],  # Link to other spans
    start_time=start_timestamp,  # Custom start time (in nanoseconds)
    record_exception=True,  # Auto-record exceptions (default: True)
    set_status_on_exception=True  # Auto-set error status on exception (default: True)
) as span:
    # ... business logic ...
    pass
```

### 4.5 API Methods Reference

This section provides a detailed reference for the key interfaces and methods used in manual instrumentation.

#### `Tracer` Interface
*Full Documentation: [opentelemetry.trace.Tracer](https://opentelemetry-python.readthedocs.io/en/latest/api/trace.html#opentelemetry.trace.Tracer)*

| Method | Description |
| :--- | :--- |
| `start_span(name, context=None, kind=SpanKind.INTERNAL, attributes=None, links=None, start_time=None, ...)` | Starts a span without making it the current span. Returns a `Span` object that must be manually ended. Useful for detached spans. |
| `start_as_current_span(name, context=None, kind=SpanKind.INTERNAL, attributes=None, links=None, start_time=None, ...)` | Context manager that creates a new span and makes it the current span. Automatically ends the span when exiting the context. This is the recommended method for most use cases. |

#### `Span` Interface
*Full Documentation: [opentelemetry.trace.Span](https://opentelemetry-python.readthedocs.io/en/latest/api/trace.html#opentelemetry.trace.span.Span)*

| Method | Description |
| :--- | :--- |
| `set_attribute(key, value)` | Adds or updates a single attribute on the span. Supports `str`, `bool`, `int`, `float`, and sequences of these types. |
| `set_attributes(attributes)` | Adds or updates multiple attributes at once from a dictionary. More efficient than multiple `set_attribute()` calls. |
| `add_event(name, attributes=None, timestamp=None)` | Adds a time-stamped event (log) to the span. Useful for capturing significant moments within a span's lifetime. |
| `record_exception(exception, attributes=None, timestamp=None, escaped=False)` | Records details of an exception as a special, structured event on the span. The `escaped` parameter indicates if the exception escaped the span's scope. |
| `set_status(status, description=None)` | Sets the final status of the span using `Status` object. An ERROR status will typically cause the trace to be highlighted. |
| `update_name(name)` | Updates the span's name after it has started. Use sparingly as it may affect sampling decisions. |
| `end(end_time=None)` | Marks the end of the span's execution. **Automatically called when exiting a context manager.** Can accept an optional end time in nanoseconds. |
| `is_recording()` | Returns `True` if the span is recording and sending data. Useful for avoiding expensive attribute calculations if the trace is not being sampled. |
| `get_span_context()` | Returns the immutable `SpanContext` (containing the Trace ID and Span ID) of this span. |

#### `Status` and `StatusCode`
*Full Documentation: [opentelemetry.trace.Status](https://opentelemetry-python.readthedocs.io/en/latest/api/trace.html#opentelemetry.trace.Status)*

| StatusCode | Description |
| :--- | :--- |
| `StatusCode.UNSET` | The default status. Indicates that the span status has not been explicitly set. |
| `StatusCode.OK` | The operation has been validated by an application developer or operator to have completed successfully. |
| `StatusCode.ERROR` | The operation contains an error. |

**Example:**
```python
from opentelemetry.trace import Status, StatusCode

# Set OK status
span.set_status(Status(StatusCode.OK))

# Set ERROR status with description
span.set_status(Status(StatusCode.ERROR, "Database connection failed"))
```

---

## 5. Data Type Support Summary

All three methods support standard OpenTelemetry attribute types. The `MotadataDynamicInstrumentation` utility specifically handles type safety.

| Category | Supported Python Types | Behavior |
| :--- | :--- | :--- |
| **Text** | `str` | Stored as String. |
| **Integer** | `int` | Stored as **Long**. |
| **Decimal** | `float` | Stored as **Double**. |
| **Boolean** | `bool` | Stored as Boolean. |
| **Lists** | `Sequence[str]`, `Sequence[int]`, `Sequence[float]`, `Sequence[bool]` | Stored as Arrays. |

---

## 6. Runtime Execution (Agent Attachment)

The method of initializing the instrumentation remains **identical to Zero-Code Instrumentation**. You must still attach the Motadata Python Agent at runtime.

The only difference is that the **client application code has been modified** to capture specific attributes using the methods described above.

---

## 7. Resources & Verification

**GitHub Repository:** [**Sample Python Applications**](https://github.com/motadata2025/Custom-Attribute-Instrumentation-Sample-Apps/tree/main/Sample%20Apps/Python%20Custom%20Attribute)

**Verification Snapshots:** [**View Testing Snapshots on GitHub**](https://github.com/motadata2025/Custom-Attribute-Instrumentation-Sample-Apps/tree/main/Sample%20Apps/Python%20Custom%20Attribute/Testing%20Snapshots)

**Custom Attribute Supported Datatype:** [**Supported Data Types**](https://motadataindia-my.sharepoint.com/:x:/r/personal/shiven_patel_motadata_com/_layouts/15/Doc.aspx?sourcedoc=%7BA95ADCCD-C7B9-4612-9BC9-5CFE1693A12D%7D&file=Custom%20Attribute%20Support.xlsx&action=default&mobileredirect=true&DefaultItemOpen=1&wdOrigin=APPHOME-WEB.DIRECT%2CAPPHOME-WEB.FILEBROWSER.RECENT&wdPreviousSession=08f9a629-a27d-48d1-84b4-ae788cafe875&wdPreviousSessionSrc=AppHomeWeb&ct=1765894539141)

---

> **Disclaimer:**
> This documentation and the associated findings are based on sample tests performed on a dummy Python application. Implementation details in a production environment may vary depending on specific framework versions, existing instrumentation, and architectural constraints. Naming conventions, dependency versions, and integration points should be adapted as needed.
