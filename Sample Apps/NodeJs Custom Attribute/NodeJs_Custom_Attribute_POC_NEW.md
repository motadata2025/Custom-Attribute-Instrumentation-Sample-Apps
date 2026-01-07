# Custom/Business Specific Attribute Injection Strategies for Node.js Runtime

> **Document Type:** Proof of Concept (POC)
> **Project:** Node.js Custom Attribute
> **Last Verified:** January 6, 2026
> **Status:** Verified & Implemented
> **Testing Environment Node.js Version:** 18+

---

## 1. Overview

This document details the findings and implementation strategies for injecting custom business attributes into OpenTelemetry traces in a Node.js runtime environment. Across all methods described below, traces were generated correctly, attributes were appended to the correct spans, and a wide range of data types (strings, numbers, booleans, arrays) were supported and visible in the UI.

---

## 2. Approach 1: API-Based Span Enrichment (Recommended Approach)

This approach uses the core OpenTelemetry API to programmatically add attributes to the currently active span at any point in the code execution.

### 2.1 Description
This method relies on `trace.getActiveSpan().setAttribute()`. To simplify usage and ensure type safety, we implemented a utility class `MotadataDynamicInstrumentation`.

**Strengths:**
*   **Dynamic:** Attributes can be added at any point (start, middle, or end of method).
*   **Flexible:** Can capture local variables, database results, and calculated values.
*   **Span-Agnostic:** Works regardless of how the span was created (auto-instrumentation, annotation, or manual).

**Limitations:**
*   Requires an active span. Attribute injection is limited to OpenTelemetry-instrumented execution paths; in non-instrumented or unsupported contexts (such as background threads without OTel context), no span exists and attributes are therefore ignored unless a new span is explicitly created.

### 2.2 Prerequisites
**Dependencies:**
The core API library is required.

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

2.  **Null Safety:**
    *   The class explicitly checks for `null` and `undefined` keys and values.
    *   If a key or value is `null` or `undefined`, the operation is **silently ignored**. No exceptions are thrown, ensuring that telemetry code never crashes the application.

3.  **Type Handling:**
    *   **Strings, Numbers, Booleans** are handled directly by the `set()` method.
    *   **Arrays** are handled by type-specific methods: `setBooleanList`, `setNumberList`, and `setStringList`.
    *   Empty arrays are silently ignored (not added to the span).

4.  **Active Span Check:**
    *   Before setting any attribute, the utility checks if an active span exists using `trace.getActiveSpan()`.
    *   If no active span exists, the operation is silently ignored.

5.  **Error Suppression:**
    *   All internal OTEL calls are wrapped in `try-catch` blocks that swallow exceptions. This guarantees that even if the OTEL API fails (e.g., span is closed), the application flow remains uninterrupted.

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

---

