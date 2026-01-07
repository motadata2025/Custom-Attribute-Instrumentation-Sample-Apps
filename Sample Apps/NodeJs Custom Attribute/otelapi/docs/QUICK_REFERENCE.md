# OpenTelemetry Custom Attributes - Quick Reference

## The 4 Methods

### 1️⃣ Active Span Enrichment
**Add to existing spans**

```javascript
const { trace } = require('@opentelemetry/api');

const span = trace.getActiveSpan();
if (span) {
  span.setAttribute('user.id', userId);
  span.setAttribute('order.amount', amount);
}
```

**Use when:** Adding business context to auto-instrumented spans

---

### 2️⃣ Manual Tracer and Span Creation
**Create new spans with full control**

```javascript
const { trace } = require('@opentelemetry/api');
const tracer = trace.getTracer('my-service');

// Simple span (no children)
const span = tracer.startSpan('operation');
span.setAttribute('key', 'value');
span.end();

// Active span (with children)
tracer.startActiveSpan('operation', (span) => {
  span.setAttribute('key', 'value');
  // Child spans created here
  span.end();
});
```

**Use when:** Measuring specific operations, creating hierarchies

---

### 3️⃣ Baggage Propagation
**Cross-service context**

```javascript
const { context, propagation } = require('@opentelemetry/api');

// Set baggage
const baggage = propagation.createBaggage({
  'tenant.id': { value: tenantId },
  'user.id': { value: userId }
});

context.with(
  propagation.setBaggage(context.active(), baggage),
  () => {
    // Baggage propagates to downstream services
  }
);

// Read baggage
const baggage = propagation.getBaggage(context.active());
const tenantId = baggage?.getEntry('tenant.id')?.value;
```

**Use when:** Propagating data across services  
**⚠️ WARNING:** Never put sensitive data in baggage!

---

### 4️⃣ SpanProcessor
**Zero-code centralized injection**

```javascript
class CustomSpanProcessor {
  onStart(span) {
    span.setAttribute('app.version', process.env.APP_VERSION);
    span.setAttribute('app.environment', process.env.NODE_ENV);
  }
  onEnd() {}
  shutdown() { return Promise.resolve(); }
  forceFlush() { return Promise.resolve(); }
}

provider.addSpanProcessor(new CustomSpanProcessor());
```

**Use when:** Adding attributes to ALL spans without code changes

---

## Decision Tree

```
Need to add attributes?
│
├─ To existing spans? → Method 1: Active Span Enrichment
│
├─ Create new operation? → Method 2: Explicit Span Creation
│
├─ Across services? → Method 3: Baggage Propagation
│
└─ To ALL spans? → Method 4: SpanProcessor
```

---

## Comparison Table

| Method | Span Created | Code Change | Best For |
|--------|--------------|-------------|----------|
| Active Span | ❌ | Low | Business KPIs |
| Manual Tracer | ✅ | High | Custom workflows |
| Baggage | ❌ | Medium | Cross-service data |
| SpanProcessor | ❌ | None | Environment metadata |

---

## Best Practices Checklist

✅ Always check if span exists: `if (span) { ... }`  
✅ Always end spans: Use `try/finally` or `startActiveSpan`  
✅ Use semantic conventions: `http.method`, `db.system`, etc.  
✅ Namespace custom attributes: `business.*`, `app.*`  
✅ Never put sensitive data in baggage  
✅ Manage cardinality - avoid unique values  
✅ Use appropriate types: string, number, boolean, array  

---

## Common Patterns

### Pattern 1: Enrich HTTP Request
```javascript
app.use((req, res, next) => {
  const span = trace.getActiveSpan();
  if (span) {
    span.setAttribute('user.id', req.user?.id);
    span.setAttribute('tenant.id', req.headers['x-tenant-id']);
    span.setAttribute('request.id', req.id);
  }
  next();
});
```

### Pattern 2: Error Handling
```javascript
try {
  const result = await operation();
  span.setAttribute('result.success', true);
} catch (error) {
  span.recordException(error);
  span.setStatus({ code: SpanStatusCode.ERROR });
  span.setAttribute('result.success', false);
  throw error;
} finally {
  span.end();
}
```

### Pattern 3: Baggage to Span
```javascript
const span = trace.getActiveSpan();
const baggage = propagation.getBaggage(context.active());

if (span && baggage) {
  baggage.getAllEntries().forEach(([key, entry]) => {
    span.setAttribute(`baggage.${key}`, entry.value);
  });
}
```

---

## Common Pitfalls

❌ Forgetting to end spans  
❌ Not checking if span exists  
❌ Expecting baggage to auto-add to spans  
❌ High cardinality attributes  
❌ Sensitive data in baggage  
❌ Using `startSpan` when you need hierarchy  

---

## Resources

📖 [Full Documentation](./OPENTELEMETRY_CUSTOM_ATTRIBUTES.md)  
🌐 [OpenTelemetry Docs](https://opentelemetry.io/docs/)  
📚 [Semantic Conventions](https://opentelemetry.io/docs/specs/semconv/)  
💬 [Community Slack](https://cloud-native.slack.com/archives/C01N7PP1THC)

