# Method 1: Active Span Enrichment - Quick Start Guide

## What is Method 1?
Method 1 adds custom attributes to **existing spans** created by OpenTelemetry auto-instrumentation. You don't create new spans - you enrich the ones that already exist.

## Quick Implementation (3 Steps)

### Step 1: Import the trace API
```javascript
const { trace } = require('@opentelemetry/api');
```

### Step 2: Get the active span
```javascript
const span = trace.getActiveSpan();
```

### Step 3: Add attributes (with null check)
```javascript
if (span) {
  span.setAttribute('apm.operation', 'myOperation');
  span.setAttribute('apm.result.success', true);
}
```

## Complete Example

```javascript
const { trace } = require('@opentelemetry/api');

class MyController {
  static async myMethod(req, res) {
    // Get active span
    const span = trace.getActiveSpan();
    
    // Add request metadata
    if (span) {
      span.setAttribute('apm.operation', 'myMethod');
      span.setAttribute('apm.controller', 'MyController');
      span.setAttribute('apm.method', req.method);
      span.setAttribute('apm.endpoint', req.path);
    }
    
    try {
      // Your business logic
      const result = await doSomething();
      
      // Add success attributes
      if (span) {
        span.setAttribute('apm.result.success', true);
        span.setAttribute('apm.result.count', result.length);
        span.setAttribute('apm.http.status_code', 200);
      }
      
      res.status(200).json({ success: true, data: result });
    } catch (error) {
      // Add error attributes
      if (span) {
        span.setAttribute('apm.result.success', false);
        span.setAttribute('apm.error.occurred', true);
        span.setAttribute('apm.error.message', error.message);
        span.setAttribute('apm.http.status_code', 500);
      }
      
      res.status(500).json({ success: false, error: error.message });
    }
  }
}
```

## Common Attributes Pattern

### Request Start (Always)
```javascript
span.setAttribute('apm.operation', 'operationName');
span.setAttribute('apm.controller', 'ControllerName');
span.setAttribute('apm.method', req.method);
span.setAttribute('apm.endpoint', req.path);
```

### Success Path
```javascript
span.setAttribute('apm.result.success', true);
span.setAttribute('apm.http.status_code', 200);
// Add operation-specific data
span.setAttribute('apm.result.count', items.length);
span.setAttribute('apm.user.id', user.id);
```

### Error Path
```javascript
span.setAttribute('apm.result.success', false);
span.setAttribute('apm.error.occurred', true);
span.setAttribute('apm.error.message', error.message);
span.setAttribute('apm.http.status_code', 500);
```

## Attribute Naming Convention

### Use `apm.*` prefix for all custom attributes
```javascript
✅ span.setAttribute('apm.operation', 'createUser');
✅ span.setAttribute('apm.user.id', userId);
✅ span.setAttribute('apm.result.count', 10);

❌ span.setAttribute('operation', 'createUser');  // No prefix
❌ span.setAttribute('userId', userId);           // No namespace
```

### Use dot notation for hierarchy
```javascript
✅ span.setAttribute('apm.user.username', 'john');
✅ span.setAttribute('apm.result.success', true);
✅ span.setAttribute('apm.error.message', 'Not found');

❌ span.setAttribute('apm.user_username', 'john');  // Use dots, not underscores
```

## Data Types

```javascript
// String
span.setAttribute('apm.operation', 'getAllUsers');

// Number
span.setAttribute('apm.result.count', 42);
span.setAttribute('apm.user.age', 25);

// Boolean
span.setAttribute('apm.result.success', true);
span.setAttribute('apm.user.is_active', false);

// Array
span.setAttribute('apm.user.tags', ['admin', 'vip']);
span.setAttribute('apm.update.fields', ['email', 'age']);
```

## When to Use Method 1

### ✅ Perfect For:
- Adding business context to HTTP requests
- Enriching database query spans
- Adding user information to operations
- Quick wins with minimal code changes
- Request-level metadata

### ❌ Not Suitable For:
- Creating new custom spans (use Method 2)
- Cross-service context propagation (use Method 3)
- Global attributes for all spans (use Method 4)
- When no span exists (requires auto-instrumentation)

## Prerequisites

### Required: OpenTelemetry Auto-Instrumentation
Method 1 requires spans to already exist. Ensure you have auto-instrumentation set up:

```javascript
// tracing.js (load before your app)
const { NodeTracerProvider } = require('@opentelemetry/sdk-trace-node');
const { registerInstrumentations } = require('@opentelemetry/instrumentation');
const { getNodeAutoInstrumentations } = require('@opentelemetry/auto-instrumentations-node');

const provider = new NodeTracerProvider();
provider.register();

registerInstrumentations({
  instrumentations: [getNodeAutoInstrumentations()],
});
```

## Testing

### 1. Check if span exists
```javascript
const span = trace.getActiveSpan();
console.log('Span exists:', !!span);
if (span) {
  console.log('Span name:', span.name);
}
```

### 2. Make a request
```bash
curl http://localhost:8080/users
```

### 3. Check traces in your backend
- Jaeger: http://localhost:16686
- SigNoz: http://localhost:3301
- Look for attributes starting with `apm.*`

## Troubleshooting

### Span is null?
**Problem**: `trace.getActiveSpan()` returns `null`

**Solution**: Ensure auto-instrumentation is configured and running

### Attributes not visible?
**Problem**: Attributes don't appear in traces

**Solutions**:
1. Check attribute limits (default: 128 per span)
2. Verify exporter is configured
3. Force flush: `await provider.forceFlush()`

## Next Steps

1. ✅ Implement in your controllers
2. ✅ Test with real requests
3. ✅ View traces in your observability backend
4. ✅ Refine attributes based on your needs
5. ✅ Explore other methods for advanced use cases

## Full Documentation
See [METHOD_1_ACTIVE_SPAN_ENRICHMENT.md](./METHOD_1_ACTIVE_SPAN_ENRICHMENT.md) for complete details.

---

**Quick Reference**: This is the simplest method - just get the span and add attributes!

