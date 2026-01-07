Below is a **fully enriched, self-contained, and final documentation** for **only the two methods**, with **all relevant information consolidated** (concept, flow, behavior, failure cases, guarantees, usage guidance, and examples).

No extra methods. No cross-references. This is **ready for design docs / Jira / product specs**.

---

# Custom Attribute Instrumentation in Go (OpenTelemetry)

## Scope

This document describes **two supported mechanisms** for injecting **business-specific custom attributes** into OpenTelemetry spans in **Go**.
Both methods use only official OpenTelemetry APIs and are safe for production use.

---

## 1️⃣ Active Span Enrichment (Same Span)

### Concept

Active Span Enrichment adds custom business attributes to the **currently active span** available in the execution context.

* No new span is created
* No trace structure is changed
* Only metadata is appended to an existing span

This method performs **pure enrichment**, not instrumentation.

---

### How it works

1. A span is already created by:

    * Auto-instrumentation (HTTP, gRPC, DB, messaging)
    * Upstream manual instrumentation
2. The active span is retrieved from `context.Context`
3. Business attributes are attached using `SetAttributes(...)`
4. Span lifecycle, parent/child relations, and timing remain unchanged

---

### Minimal example (Go)

```go
span := trace.SpanFromContext(ctx)
span.SetAttributes(
    attribute.String("business.user.id", userID),
    attribute.Bool("business.is_premium", true),
)
```

---

### Span & Trace Behavior

| Aspect                      | Behavior     |
| --------------------------- | ------------ |
| New span created            | ❌ No         |
| Trace ID                    | Same         |
| Parent / Child relationship | Unchanged    |
| Span timing                 | Not affected |
| Trace structure             | Unchanged    |

---

### No-Span Scenario

If no span exists in the context:

* `SpanFromContext` returns a **no-op span**
* Attribute calls are safely ignored
* No error or panic occurs
* Attributes are **not recorded**

This behavior is guaranteed by the OpenTelemetry SDK.

---

### Use when

* Enriching request spans created by auto-instrumentation
* Injecting business identifiers (user ID, tenant ID, order ID)
* Adding KPIs, flags, or classifications
* Implementing rule-based or dynamic attribute injection
* Zero trace shape modification is required

---

### Closest equivalent to

* **Java**: `Span.current().setAttribute(...)`
* **.NET**: `Activity.Current?.SetTag(...)`
* **Node.js**: `trace.getSpan(context.active()).setAttribute(...)`

---

### Advantages

* Extremely low overhead
* No increase in span count
* Fully compatible with auto-instrumentation
* Safe to call from any code path
* Ideal for dynamic and zero-code instrumentation

---

### Limitations

* Cannot measure execution duration of a specific operation
* Depends on the presence of an active span

---

## 2️⃣ Explicit Span Creation with Attributes (New Child Span)

### Concept

Explicit Span Creation creates a **new span** to represent a **logical business operation**, and attaches custom attributes to that span.

This method performs **explicit instrumentation** and modifies the trace structure.

---

### How it works

1. A tracer is used to start a new span using `Tracer.Start`
2. The new span:

    * Becomes a **child span** of the currently active span (if present)
    * Inherits the same Trace ID
3. Attributes are attached:

    * At span creation time, or
    * During span execution
4. The span is explicitly ended by the application

---

### Minimal example (Go)

```go
ctx, span := tracer.Start(
    ctx,
    "ProcessOrder",
    trace.WithAttributes(
        attribute.String("order.id", orderID),
        attribute.String("order.type", "express"),
    ),
)
defer span.End()

// business logic
```

---

### Span & Trace Behavior

| Aspect           | Behavior       |
| ---------------- | -------------- |
| New span created | ✅ Yes          |
| Span type        | Child span     |
| Trace ID         | Same as parent |
| Execution timing | Captured       |
| Trace structure  | Modified       |

---

### No-Parent Scenario

If no active span exists in the context:

* The created span becomes a **root span**
* A **new trace** is started automatically

---

### Use when

* Business logic requires its **own timing boundary**
* You need visibility into domain-level operations
* Performance analysis or debugging is required
* Operations are not covered by auto-instrumentation

---

### Closest equivalent to

* **Java**: `tracer.spanBuilder(...).startSpan()`
* **.NET**: `ActivitySource.StartActivity(...)`
* **Node.js**: `tracer.startSpan(...)`

---

### Advantages

* Precise duration and latency measurement
* Clear separation of business operations
* Better trace visualization for complex workflows
* Explicit control over span naming and attributes

---

### Limitations

* Increases overall span volume
* Can clutter traces if overused
* Requires careful sampling and span naming strategy

---

## Side-by-Side Summary

| Dimension              | Active Span Enrichment | Explicit Span Creation |
| ---------------------- | ---------------------- | ---------------------- |
| Creates new span       | No                     | Yes                    |
| Modifies trace shape   | No                     | Yes                    |
| Requires existing span | Yes                    | No                     |
| Captures timing        | No                     | Yes                    |
| Best for attributes    | Yes                    | No                     |
| Best for operations    | No                     | Yes                    |

---

## Conclusion

* **Active Span Enrichment** should be the **default approach** for injecting business-specific custom attributes.
* **Explicit Span Creation** should be used **selectively** for operations that require independent visibility and timing.

Both approaches are fully supported by OpenTelemetry Go and align with production-grade observability practices.

---

If you want next:

* Markdown / PDF export
* Validation rules for attribute types
* Mapping to your **dynamic instrumentation engine**
* Or a **Jira-ready condensed version**
