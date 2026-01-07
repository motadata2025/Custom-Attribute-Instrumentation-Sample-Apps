# Custom/Business Specific Attribute Injection Strategies for Go Runtime

> **Document Type:** Proof of Concept (POC)
> **Project:** Go Custom Attribute
> **Last Verified:** January 1, 2025
> **Status:** Verified & Implemented

---

## 1. Overview

This document details the findings and implementation strategies for injecting custom business attributes into OpenTelemetry traces in a Go runtime environment.

### Key Architectural Observation:

In the Go eBPF auto-instrumentation model, spans are created and managed outside the Go runtime, specifically at the kernel and eBPF layer. Due to this architecture:

*   Auto-instrumented spans do not exist as mutable span objects inside the Go application runtime.
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
*   Span is non-recording and invalid.

This behavior is expected and by design in eBPF-based auto-instrumentation.

---

## 2. Supported Approach: Tracer-Based Manual Span Creation

The only supported approach is to create new child spans for the eBPF-generated parent spans. These manual spans become child spans of the eBPF-generated parent spans (such as HTTP server spans) through context propagation.

### How This Approach Works

1.  OpenTelemetry eBPF auto-instrumentation creates the parent spans automatically (for example, HTTP or database spans).
2.  The Go application receives a context that carries trace propagation metadata.
3.  The application explicitly starts a new span using the OpenTelemetry Go Tracer API.
4.  Business-specific attributes are attached to this manually created span.
5.  The Auto SDK correlates the manual span with the eBPF-generated parent span using the propagated context.
6.  Both auto-instrumented and manual spans appear correctly in the same trace in the UI.

---

## 3. Implementation

### 3.1 Prerequisites
**Go Version:**
`go 1.23.12`

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

**Minimal Code Reference:**

```go
package main

import (
    "context"
    "go.opentelemetry.io/otel"
    "go.opentelemetry.io/otel/attribute"
)

func businessLogic(ctx context.Context, orderID string) {
    tracer := otel.Tracer("motadata.custom.instrumentation")
    ctx, span := tracer.Start(ctx, "BusinessOperation")
    defer span.End()

    span.SetAttributes(
        attribute.String("apm.operation", "create_order"),
        attribute.String("apm.order.id", orderID),
    )

    // ... your business logic here ...
}
```

---

## 4. Data Type Support Summary

Go supports the standard OpenTelemetry attribute types.

| Category | Supported Go Types |
| :--- | :--- |
| **Text** | `string` |
| **Integer** | `int`, `int64` |
| **Decimal** | `float64` |
| **Boolean** | `bool` |
---

## 5. Runtime Execution (Agent Attachment)

The method of initializing the instrumentation remains **identical to Zero-Code Instrumentation**. You must still attach the Motadata Go Agent at runtime.

The only difference is that the **client application code has been modified** to capture specific attributes using the methods described above.

---

## 6. Resources & Verification

**GitHub Repository:** [**Sample Go Application**](https://github.com/ShivenPatel19/Go-Custom-Attribute-Instrumentation-with-Code-Change-)

**Verification Snapshots:** [**View Testing Snapshots on GitHub**](https://github.com/ShivenPatel19/Go-Custom-Attribute-Instrumentation-with-Code-Change-/tree/main/TestingSnapshots)

**Custom Attribute Supported Datatype:** [**Supported Data Types**](https://motadataindia-my.sharepoint.com/:x:/r/personal/shiven_patel_motadata_com/_layouts/15/Doc.aspx?sourcedoc=%7BA95ADCCD-C7B9-4612-9BC9-5CFE1693A12D%7D&file=Custom%20Attribute%20Support.xlsx&action=default&mobileredirect=true&DefaultItemOpen=1&wdOrigin=APPHOME-WEB.DIRECT%2CAPPHOME-WEB.FILEBROWSER.RECENT&wdPreviousSession=08f9a629-a27d-48d1-84b4-ae788cafe875&wdPreviousSessionSrc=AppHomeWeb&ct=1765894539141)

---

> **Disclaimer:**
> This documentation and the associated findings are based on sample tests performed on a sample Go application. Implementation details in a production environment may vary depending on specific framework versions, existing instrumentation, and architectural constraints. Naming conventions, dependency versions, and integration points should be adapted as needed.
