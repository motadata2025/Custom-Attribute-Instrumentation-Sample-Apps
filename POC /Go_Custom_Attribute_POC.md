# Custom/Business Specific Attribute Injection Strategies for Go Runtime

> **Document Type:** Proof of Concept (POC)
> **Project:** Go Custom Attribute
> **Last Verified:** January 1, 2025
> **Status:** Verified & Implemented
> **Testing Environment Go Version:** 1.23.12
---

## 1. Overview

This document details the findings and implementation strategies for injecting custom business attributes into OpenTelemetry traces in a Go runtime environment.

### Key Architectural Observation:

In the Go eBPF auto-instrumentation model, spans are created and managed outside the Go runtime, specifically at the kernel and eBPF layer. Due to this architecture:

*   **Auto-instrumented spans do not exist as mutable span objects inside the Go application runtime.**
*   These spans are not stored or propagated via `context.Context`.
*   Application-level OpenTelemetry APIs cannot access or modify these spans.

As a result:

*   `trace.SpanFromContext(ctx)` returns a non-recording, no-op span.
*   Calling `SetAttributes()` on this span has no effect.
*   The actual span lifecycle is owned entirely by the eBPF agent, not the Go SDK.
*   The Go runtime has no reference to the real auto-instrumented span.

Observed behavior when calling `trace.SpanFromContext(ctx)`:

*   TraceID = 00000000000000000000000000000000
*   SpanID  = 0000000000000000
*   **Span is non-recording and invalid.**

This behavior is expected and by design in eBPF-based auto-instrumentation.

**Reference:** For more details on the limitations of adding custom data to eBPF-generated spans, see **[Dash0 Guide: On Adding More Data](https://www.dash0.com/guides/opentelemetry-go-ebpf-instrumentation?referrer=grok.com#on-adding-more-data).**

---

## 2. Supported Approach: Tracer-Based Manual Span Creation

The only supported approach is to create new child spans for the eBPF-generated parent spans. These manual spans become child spans of the eBPF-generated parent spans (such as HTTP server spans) through context propagation.

### 2.1 Description

This approach provides control over span creation, allowing developers to create child spans that attach to eBPF-generated parent spans and capture business-specific attributes. It is suitable for workflows where business logic needs to be traced separately from the automatic HTTP/database instrumentation.

**Strengths:**
*   **Context Propagation:** Automatically creates child spans under eBPF-generated parent spans through `context.Context`.
*   **Business Attribute Capture:** Allows adding custom attributes to represent business operations.
*   **Trace Correlation:** Manual spans appear in the same trace as auto-instrumented spans.
*   **Flexible Span Lifecycle:** Control over when spans start and end using `defer span.End()`.

**Limitations:**
*   **Cannot Modify eBPF Spans:** Cannot access or modify spans created by eBPF auto-instrumentation.
*   **Child Spans Only:** Cannot create root spans that integrate with eBPF traces (eBPF owns the root).
*   **Requires Code Changes:** Application code must be modified to create manual spans.
*   **Context Dependency:** Requires `context.Context` to be passed through the call chain for proper parent-child relationships.

### 2.2 How This Approach Works

1.  OpenTelemetry eBPF auto-instrumentation creates the parent spans automatically (for example, HTTP or database spans).
2.  The Go application receives a context that carries trace propagation metadata.
3.  The application explicitly starts a new span using the OpenTelemetry Go Tracer API.
4.  Business-specific attributes are attached to this manually created span.
5.  The Auto SDK correlates the manual span with the eBPF-generated parent span using the propagated context.
6.  Both auto-instrumented and manual spans appear correctly in the same trace in the UI.

---

## 3. Implementation

### 3.1 Prerequisites

**Dependencies:**
Ensure the following OpenTelemetry libraries are included in your `go.mod` file.

```go
require (
    go.opentelemetry.io/otel v1.24.0
    go.opentelemetry.io/otel/attribute v1.24.0
    go.opentelemetry.io/otel/trace v1.24.0
)
```

### 3.2 Client-Side Implementation

The client must obtain a tracer and wrap the business logic in a new span.

**Example: Creating a Child Span**

```go
package main

import (
    "context"
    "go.opentelemetry.io/otel"
    "go.opentelemetry.io/otel/attribute"
    "go.opentelemetry.io/otel/codes"
    "go.opentelemetry.io/otel/trace"
)

func processOrder(ctx context.Context, orderID string) error {
    tracer := otel.Tracer("motadata.custom.instrumentation")

    // Create a new child span
    ctx, span := tracer.Start(ctx, "process-order", trace.WithSpanKind(trace.SpanKindInternal))
    defer span.End()

    // Set business attributes
    span.SetAttributes(
        attribute.String("apm.operation", "create_order"),
        attribute.String("apm.order.id", orderID),
        attribute.Int("apm.order.items", 5),
    )

    // Business logic
    err := performOrderProcessing(ctx, orderID)
    if err != nil {
        span.RecordError(err)
        span.SetStatus(codes.Error, err.Error())
        return err
    }

    span.SetStatus(codes.Ok, "Order processed successfully")
    return nil
}
```

**Example: Creating Multiple Nested Spans**

```go
func handleCheckout(ctx context.Context, cartID string) error {
    tracer := otel.Tracer("motadata.custom.instrumentation")

    // Parent span
    ctx, parentSpan := tracer.Start(ctx, "checkout-workflow", trace.WithSpanKind(trace.SpanKindInternal))
    defer parentSpan.End()

    parentSpan.SetAttributes(attribute.String("apm.cart.id", cartID))

    // Child span 1: Validate cart
    ctx, validateSpan := tracer.Start(ctx, "validate-cart", trace.WithSpanKind(trace.SpanKindInternal))
    validateSpan.SetAttributes(attribute.String("apm.validation.type", "cart"))
    if err := validateCart(ctx, cartID); err != nil {
        validateSpan.RecordError(err)
        validateSpan.SetStatus(codes.Error, err.Error())
        validateSpan.End()
        return err
    }
    validateSpan.SetStatus(codes.Ok, "")
    validateSpan.End()

    // Child span 2: Process payment
    ctx, paymentSpan := tracer.Start(ctx, "process-payment", trace.WithSpanKind(trace.SpanKindClient))
    paymentSpan.SetAttributes(attribute.String("apm.payment.method", "credit_card"))
    if err := processPayment(ctx, cartID); err != nil {
        paymentSpan.RecordError(err)
        paymentSpan.SetStatus(codes.Error, err.Error())
        paymentSpan.End()
        return err
    }
    paymentSpan.SetStatus(codes.Ok, "")
    paymentSpan.End()

    parentSpan.SetStatus(codes.Ok, "Checkout completed")
    return nil
}
```

### 3.3 Advanced Configuration: SpanKind and Span Options

When manually creating spans, you have control over the span's characteristics.

#### SpanKind Reference

The `SpanKind` specifies the relationship between spans in addition to the parent/child relationship.

| SpanKind | Description |
| :--- | :--- |
| **SpanKindInternal** | Default value. Indicates that the span is used internally within the application (e.g., a method call). |
| **SpanKindServer** | Indicates that the span covers server-side handling of an RPC or other remote request. |
| **SpanKindClient** | Indicates that the span covers the client-side wrapper around an RPC or other remote request. |
| **SpanKindProducer** | Indicates that the span describes a producer sending a message to a broker. |
| **SpanKindConsumer** | Indicates that the span describes a consumer receiving a message from a broker. |

**Example:**
```go
import "go.opentelemetry.io/otel/trace"

// Internal span (default)
ctx, span := tracer.Start(ctx, "internal-operation", trace.WithSpanKind(trace.SpanKindInternal))
defer span.End()

// Client span for outgoing HTTP call
ctx, span := tracer.Start(ctx, "http-call", trace.WithSpanKind(trace.SpanKindClient))
defer span.End()
```

#### Span Start Options

You can configure spans with additional options when creating them:

```go
import (
    "go.opentelemetry.io/otel/attribute"
    "go.opentelemetry.io/otel/trace"
)

// Create span with custom configuration
ctx, span := tracer.Start(
    ctx,
    "complex-operation",
    trace.WithSpanKind(trace.SpanKindInternal),
    trace.WithAttributes(
        attribute.String("apm.operation.type", "batch"),
        attribute.Int("apm.batch.size", 100),
    ),
    trace.WithLinks(trace.Link{
        SpanContext: relatedSpanContext,
        Attributes: []attribute.KeyValue{
            attribute.String("link.type", "follows"),
        },
    }),
)
defer span.End()
```

### 3.4 API Methods Reference

This section provides a detailed reference for the key interfaces and methods used in manual instrumentation.

#### `Tracer` Interface
*Full Documentation: [go.opentelemetry.io/otel/trace.Tracer](https://pkg.go.dev/go.opentelemetry.io/otel/trace#Tracer)*

| Method | Description |
| :--- | :--- |
| `Start(ctx context.Context, spanName string, opts ...SpanStartOption) (context.Context, Span)` | Creates a span and a context.Context containing the newly-created span. If the provided context contains a Span, the newly-created Span will be a child of that span. Returns both the new context and the Span. The Span must be ended by calling `End()`. |

**SpanStartOption Functions:**

| Option | Description |
| :--- | :--- |
| `WithSpanKind(kind SpanKind)` | Sets the SpanKind of the span. |
| `WithAttributes(attributes ...attribute.KeyValue)` | Sets initial attributes on the span. More efficient than calling `SetAttributes()` after span creation. |
| `WithLinks(links ...Link)` | Adds links to other spans. Links are used to associate spans that are not in a parent-child relationship. |
| `WithNewRoot()` | Specifies that the span should be treated as a root span, ignoring any existing parent span context. |

#### `Span` Interface
*Full Documentation: [go.opentelemetry.io/otel/trace.Span](https://pkg.go.dev/go.opentelemetry.io/otel/trace#Span)*

| Method | Description |
| :--- | :--- |
| `SetAttributes(kv ...attribute.KeyValue)` | Adds or updates attributes on the span. Supports `string`, `bool`, `int`, `int64`, `float64`, and slices of these types. |
| `AddEvent(name string, options ...EventOption)` | Adds a time-stamped event (log) to the span. Useful for capturing significant moments within a span's lifetime. |
| `RecordError(err error, options ...EventOption)` | Records details of an error as a special event on the span. This does not set the span status to Error. |
| `SetStatus(code codes.Code, description string)` | Sets the final status of the span. Use `codes.Ok`, `codes.Error`, or `codes.Unset`. An ERROR status will typically cause the trace to be highlighted. |
| `SetName(name string)` | Updates the span's name after it has started. Use sparingly as it may affect sampling decisions. |
| `End(options ...SpanEndOption)` | Marks the end of the span's execution. **Must be called to complete the span.** Typically used with `defer span.End()`. |
| `IsRecording() bool` | Returns `true` if the span is recording and sending data. Useful for avoiding expensive attribute calculations if the trace is not being sampled. |
| `SpanContext() SpanContext` | Returns the immutable `SpanContext` (containing the Trace ID and Span ID) of this span. |

#### Status Codes
*Full Documentation: [go.opentelemetry.io/otel/codes](https://pkg.go.dev/go.opentelemetry.io/otel/codes)*

| Code | Description |
| :--- | :--- |
| `codes.Unset` | The default status. Indicates that the span status has not been explicitly set. |
| `codes.Ok` | The operation has been validated to have completed successfully. |
| `codes.Error` | The operation contains an error. |

**Example:**
```go
import "go.opentelemetry.io/otel/codes"

// Set OK status
span.SetStatus(codes.Ok, "Operation completed successfully")

// Set ERROR status with description
span.SetStatus(codes.Error, "Database connection failed")
```

---

## 4. Data Type Support Summary

Go supports the standard OpenTelemetry attribute types through the `attribute` package.

| Category | Supported Go Types | Behavior |
| :--- | :--- | :--- |
| **Boolean** | `bool` | Stored as Boolean. |
| **Integer** | `int64` | Stored as **Int64**. |
| **Decimal** | `float64` | Stored as **Float64**. |
| **Text** | `string` | Stored as String. |

---

## 5. Runtime Execution (Agent Attachment)

The method of initializing the instrumentation remains **identical to Zero-Code Instrumentation**. You must still attach the Motadata Go Agent at runtime.

The only difference is that the **client application code has been modified** to capture specific attributes using the methods described above.

---

## 6. Resources & Verification

**GitHub Repository:** [**Sample Go Application**](https://github.com/motadata2025/Custom-Attribute-Instrumentation-Sample-Apps/tree/main/Sample%20Apps/Go%20Custom%20Attribute)

**Verification Snapshots:** [**View Testing Snapshots on GitHub**](https://github.com/motadata2025/Custom-Attribute-Instrumentation-Sample-Apps/tree/main/Sample%20Apps/Go%20Custom%20Attribute/TestingSnapshots)

**Custom Attribute Supported Datatype:** [**Supported Data Types**](https://motadataindia-my.sharepoint.com/:x:/r/personal/shiven_patel_motadata_com/_layouts/15/Doc.aspx?sourcedoc=%7BA95ADCCD-C7B9-4612-9BC9-5CFE1693A12D%7D&file=Custom%20Attribute%20Support.xlsx&action=default&mobileredirect=true&DefaultItemOpen=1&wdOrigin=APPHOME-WEB.DIRECT%2CAPPHOME-WEB.FILEBROWSER.RECENT&wdPreviousSession=08f9a629-a27d-48d1-84b4-ae788cafe875&wdPreviousSessionSrc=AppHomeWeb&ct=1765894539141)

**External Reference - eBPF Limitations:** [**Dash0 Guide: Exploring OpenTelemetry Go Instrumentation via eBPF**](https://www.dash0.com/guides/opentelemetry-go-ebpf-instrumentation?referrer=grok.com#on-adding-more-data)

> **Key Quote:** "One limitation I encountered is the inability to add custom attributes to spans generated by auto-instrumentation. However, it seems this functionality is currently being developed. Once implemented, it will allow developers to retrieve the current span from the context and dynamically add attributes."
>
> This directly addresses the inability to modify auto-instrumented spans (e.g., via `SetAttributes()` on the span from `trace.SpanFromContext(ctx)`), because the real spans are created and managed entirely in the eBPF layer outside the Go runtime/SDK. The guide notes that retrieving and modifying the current span via context is a planned future feature, implying it's not possible yet—aligning with the no-op/non-recording behavior described in Section 1 of this document.

---

> **Disclaimer:**
> This documentation and the associated findings are based on sample tests performed on a sample Go application. Implementation details in a production environment may vary depending on specific framework versions, existing instrumentation, and architectural constraints. Naming conventions, dependency versions, and integration points should be adapted as needed.
