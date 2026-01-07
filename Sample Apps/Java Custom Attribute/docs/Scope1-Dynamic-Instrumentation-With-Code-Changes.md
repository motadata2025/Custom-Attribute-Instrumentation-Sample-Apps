# Scope 1: Dynamic Instrumentation WITH Client Code Changes

> **Document Type:** Implementation Guide  
> **Status:** POC Research  
> **Last Updated:** December 5, 2025  
> **Recommendation:** ✅ **PREFERRED APPROACH**

---

## Overview

This document covers the implementation of **dynamic custom attributes** when client code modifications are permitted. This approach provides **maximum flexibility** for capturing business-specific context in OpenTelemetry spans.

---

## Architecture Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           CLIENT APPLICATION                                 │
│  ┌─────────────────┐    ┌──────────────────┐    ┌─────────────────────┐     │
│  │ Business Logic  │───▶│ DynamicAttribute │───▶│ Span.current()      │     │
│  │ (Order, User,   │    │ Injector         │    │ .setAttribute()     │     │
│  │  Transaction)   │    │ (Your SDK)       │    │                     │     │
│  └─────────────────┘    └──────────────────┘    └──────────┬──────────┘     │
│                                                             │                │
└─────────────────────────────────────────────────────────────┼────────────────┘
                                                              │
                                                              ▼
┌─────────────────┐     ┌──────────────┐     ┌────────────┐  │  ┌──────────┐
│ Java Agent      │────▶│ OTEL         │────▶│ Cache      │──┼─▶│ Your     │
│ (Auto-Instr)    │     │ Collector    │     │ File       │  │  │ Backend  │
└─────────────────┘     └──────────────┘     └────────────┘  │  └──────────┘
                                                              │
                                              Custom attributes flow with spans
```

---

## Why This Approach?

| Criteria | Rating | Notes |
|----------|--------|-------|
| Dynamic Attribute Support | ✅ Excellent | Full runtime flexibility |
| Business Context Access | ✅ Excellent | Direct access to app variables |
| Runtime Changes | ✅ Excellent | Immediate effect, no restart |
| Type Safety | ✅ Good | Handles String, Long, Double, Boolean |
| Implementation Effort | ✅ Low | Simple helper class |
| Maintenance | ✅ Low | Lives with client code |

---

## Implementation

### Step 1: Add Dependency

**Maven:**
```xml
<dependency>
    <groupId>io.opentelemetry</groupId>
    <artifactId>opentelemetry-api</artifactId>
    <version>1.56.0</version>
</dependency>
```

**Gradle:**
```groovy
implementation 'io.opentelemetry:opentelemetry-api:1.56.0'
```

---

### Step 2: Create Dynamic Attribute Injector (SDK for Clients)

```java
package com.yourcompany.telemetry;

import io.opentelemetry.api.trace.Span;
import java.util.Map;
import java.util.List;

/**
 * Dynamic Attribute Injector - Provides runtime injection of business attributes
 * into OpenTelemetry spans without compile-time constraints.
 * 
 * USAGE: Clients can add/remove attributes at any time without code changes.
 */
public class DynamicAttributeInjector {

    private static final String ATTRIBUTE_PREFIX = "business.";

    /**
     * Inject a single business attribute into the current span
     */
    public static void addAttribute(String key, Object value) {
        Span currentSpan = Span.current();
        if (currentSpan == null || value == null) return;
        
        String prefixedKey = ATTRIBUTE_PREFIX + key;
        setAttributeByType(currentSpan, prefixedKey, value);
    }

    /**
     * Inject multiple business attributes from a Map (fully dynamic)
     * Clients can change the Map contents at runtime without any code changes
     */
    public static void addAttributes(Map<String, Object> attributes) {
        if (attributes == null || attributes.isEmpty()) return;
        
        Span currentSpan = Span.current();
        if (currentSpan == null) return;

        for (Map.Entry<String, Object> entry : attributes.entrySet()) {
            String prefixedKey = ATTRIBUTE_PREFIX + entry.getKey();
            setAttributeByType(currentSpan, prefixedKey, entry.getValue());
        }
    }

    /**
     * Handle different value types dynamically
     */
    private static void setAttributeByType(Span span, String key, Object value) {
        if (value instanceof String) {
            span.setAttribute(key, (String) value);
        } else if (value instanceof Long) {
            span.setAttribute(key, (Long) value);
        } else if (value instanceof Integer) {
            span.setAttribute(key, ((Integer) value).longValue());
        } else if (value instanceof Double) {
            span.setAttribute(key, (Double) value);
        } else if (value instanceof Float) {
            span.setAttribute(key, ((Float) value).doubleValue());
        } else if (value instanceof Boolean) {
            span.setAttribute(key, (Boolean) value);
        } else {
            // Fallback: convert to string
            span.setAttribute(key, value.toString());
        }
    }
}
```

---

### Step 3: Client Usage Examples

#### Example 1: Simple Single Attribute
```java
// In client's business logic
DynamicAttributeInjector.addAttribute("order.id", "ORD-12345");
DynamicAttributeInjector.addAttribute("customer.tier", "premium");
```

#### Example 2: Dynamic Map (Recommended for Flexibility)
```java
// Build dynamic attributes - can come from config, database, or runtime logic
Map<String, Object> businessContext = new HashMap<>();
businessContext.put("order.id", order.getId());
businessContext.put("customer.id", customer.getId());
businessContext.put("transaction.amount", transaction.getAmount());
businessContext.put("is.priority", customer.isPriority());

// Inject all at once
DynamicAttributeInjector.addAttributes(businessContext);
```

#### Example 3: Configuration-Driven Attributes
```java
// Load attribute definitions from external config (can change without code deploy)
Properties config = loadFromConfigServer(); // or file, database, etc.

Map<String, Object> dynamicAttrs = new HashMap<>();
for (String key : config.stringPropertyNames()) {
    if (key.startsWith("telemetry.attribute.")) {
        String attrName = key.replace("telemetry.attribute.", "");
        dynamicAttrs.put(attrName, config.getProperty(key));
    }
}

DynamicAttributeInjector.addAttributes(dynamicAttrs);
```

---

## Dynamic Attribute Schema

Clients can define their attribute schema in a configuration file that can be updated at runtime:

**attributes-schema.json:**
```json
{
  "version": "1.0",
  "attributes": [
    {
      "name": "order.id",
      "type": "string",
      "source": "method_param",
      "description": "Unique order identifier"
    },
    {
      "name": "customer.tier",
      "type": "string",
      "source": "runtime",
      "allowed_values": ["basic", "premium", "enterprise"]
    },
    {
      "name": "transaction.amount",
      "type": "double",
      "source": "runtime",
      "description": "Transaction amount in USD"
    }
  ]
}
```

---

## Best Practices

### 1. Attribute Naming Convention
```java
// Use dot notation with business prefix
DynamicAttributeInjector.addAttribute("order.id", orderId);        // ✅ Good
DynamicAttributeInjector.addAttribute("ORDER_ID", orderId);        // ❌ Avoid
```

### 2. Avoid High Cardinality
```java
// ❌ Bad - unique per request (high cardinality)
DynamicAttributeInjector.addAttribute("request.uuid", UUID.randomUUID().toString());

// ✅ Good - bounded values
DynamicAttributeInjector.addAttribute("request.type", "checkout");
DynamicAttributeInjector.addAttribute("customer.segment", "enterprise");
```

### 3. Handle Null Values
```java
// The SDK handles nulls gracefully, but be explicit
if (customer != null) {
    DynamicAttributeInjector.addAttribute("customer.id", customer.getId());
}
```

### 4. Sensitive Data
```java
// ❌ Never include PII or sensitive data
DynamicAttributeInjector.addAttribute("customer.ssn", ssn);           // NEVER!
DynamicAttributeInjector.addAttribute("payment.card_number", cardNo); // NEVER!

// ✅ Use anonymized or hashed values
DynamicAttributeInjector.addAttribute("customer.id_hash", hashCustomerId(customerId));
```

---

## Integration Points

### Where to Call the Injector

| Location | Use Case | Example |
|----------|----------|---------|
| Controller/API Entry | Request-level context | User ID, Request Type |
| Service Layer | Business operation context | Order ID, Transaction Type |
| Repository Layer | Data access context | Query Type, Table Name |
| Exception Handlers | Error context | Error Code, Error Category |

### Example: Spring Controller Integration
```java
@RestController
public class OrderController {

    @PostMapping("/orders")
    public Order createOrder(@RequestBody OrderRequest request) {
        // Inject business context at entry point
        Map<String, Object> context = Map.of(
            "order.type", request.getType(),
            "customer.id", request.getCustomerId(),
            "items.count", request.getItems().size()
        );
        DynamicAttributeInjector.addAttributes(context);

        return orderService.createOrder(request);
    }
}
```

---

## Verification

### Verify Attributes in Spans

After implementation, verify attributes appear in your traces:

1. **Check OTEL Collector logs** (enable debug mode)
2. **Check your cache file** for attribute presence
3. **Verify in your UI** that business attributes are visible

### Expected Span Output
```json
{
  "traceId": "abc123...",
  "spanId": "def456...",
  "name": "OrderController.createOrder",
  "attributes": {
    "business.order.type": "standard",
    "business.customer.id": "CUST-789",
    "business.items.count": 3,
    "http.method": "POST",
    "http.url": "/orders"
  }
}
```

---

## References

- [Span.current() - GitHub Source](https://github.com/open-telemetry/opentelemetry-java/blob/main/api/all/src/main/java/io/opentelemetry/api/trace/Span.java)
- [OpenTelemetry API Documentation](https://opentelemetry.io/docs/languages/java/api/)
- [Semantic Conventions](https://opentelemetry.io/docs/specs/semconv/)

---

## Summary

| Aspect | Details |
|--------|---------|
| **Approach** | `Span.current().setAttribute()` with helper SDK |
| **Flexibility** | ✅ Full dynamic support |
| **Runtime Changes** | ✅ Immediate, no restart needed |
| **Business Data Access** | ✅ Full access to application variables |
| **Implementation Effort** | Low - single helper class |
| **Recommended For** | All cases where code changes are permitted |

