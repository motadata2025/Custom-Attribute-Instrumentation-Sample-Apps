## PTEL / OpenTelemetry: Two Core Ways to Add Custom Attributes to Traces

In OpenTelemetry (and PTEL), **all custom attribute injection boils down to just two fundamental approaches**:

1. **Enrich an existing span**
2. **Create a span using a tracer (with or without parent context)**

Everything else is a variation of these.

---

# ✅ Approach 1️⃣ Active Span Enrichment (Same Span)

## What it means

You **do NOT create a new span**.
You **add custom attributes** to the **currently active span** created by auto-instrumentation.

That active span could be:

* HTTP server span
* Database span
* gRPC server span
* Messaging consumer span

You are simply **enriching** what already exists.

---

## What happens in the trace

```
HTTP GET /orders
└── (same span)
    ├── http.method = GET
    ├── http.route = /orders
    ├── user.id = 12345      👈 added by you
    ├── tenant.id = acme     👈 added by you
```

✔ No new span
✔ No trace structure change
✔ Only metadata is added

---

## When to use

✅ Add business metadata
✅ Want **zero visual noise** in the trace
✅ Want behavior closest to:

* Java annotations
* .NET `Activity.Current`

---

## Generic PTEL / OTEL Pseudo-Code

```pseudo
span = Span.current()

if span is valid:
    span.setAttribute("user.id", "12345")
    span.setAttribute("tenant.id", "acme")
    span.setAttribute("order.type", "priority")
```

✔ Works only while a span is **active**
✔ Most commonly used and **recommended default**

---

## Pros / Cons

**Pros**

* Very fast
* Very simple
* No additional span overhead

**Cons**

* Cannot represent a separate logical operation
* Requires an active span

---

# ✅ Approach 2️⃣ Tracer-Based Span Creation

*(Same Trace **or** New Trace — depending on context)*

## What it means

You **explicitly create a span using a tracer** and attach custom attributes to it.

This **single approach covers BOTH cases**:

* Creating a **child span in the same trace**
* Creating a **root span that starts a new trace**

👉 The **only difference is whether parent context is provided or not**.

---

## Case A: Tracer-Based Span (Same Trace – Child Span)

### What happens in the trace

```
HTTP POST /checkout
└── checkout.request
    └── validate.payment     👈 tracer-created child span
        ├── payment.method = UPI
        ├── amount = 999
        ├── currency = INR
```

✔ Same trace ID
✔ Parent–child relationship preserved
✔ Represents a **logical business step**

---

### When to use

✅ Business workflows
✅ Auditing steps
✅ Domain-specific operations
✅ You want **visibility in the trace UI**

---

### Pseudo-Code (Same Trace)

```pseudo
tracer = TracerProvider.getTracer("business-tracer")

span = tracer.startSpan(
    name = "validate.payment",
    parent = Context.current()   // 👈 SAME TRACE
)

span.setAttribute("payment.method", "UPI")
span.setAttribute("amount", 999)
span.setAttribute("currency", "INR")

span.end()
```

---

## Case B: Tracer-Based Span (New Trace – Root Span)

### What happens in the trace

```
Trace A:
HTTP GET /orders
└── db.query

Trace B: (independent)
daily.report.job
├── report.type = sales
├── execution.mode = batch
```

✔ New trace ID
✔ No parent span
✔ Completely independent execution

---

### When to use

✅ Background jobs
✅ Scheduled / cron tasks
✅ Batch processing
✅ Async workers not tied to requests

---

### Pseudo-Code (New Trace)

```pseudo
tracer = TracerProvider.getTracer("background-tracer")

span = tracer.startSpan(
    name = "daily.report.job",
    parent = NONE   // 👈 NEW TRACE
)

span.setAttribute("report.type", "sales")
span.setAttribute("execution.mode", "batch")

span.end()
```

---

## Key Rule (Very Important)

> **Tracer always creates spans.
> Context decides whether it is the same trace or a new trace.**

Same API.
Different semantics.

---

# 🔁 Final Comparison

| Approach                     | Span Created | Trace Impact | Typical Use     |
| ---------------------------- | ------------ | ------------ | --------------- |
| Approach 1                   | ❌ No         | Same span    | Add metadata    |
| Approach 2 (with context)    | ✅ Yes        | Same trace   | Business steps  |
| Approach 2 (without context) | ✅ Yes        | New trace    | Background jobs |
