# Method 2: Span Creation - Quick Start Guide

## What is Method 2?
Method 2 creates **custom spans** with full control over span lifecycle, attributes, events, and status. Unlike Method 1, you create new spans rather than enriching existing ones.

## Quick Implementation (5 Steps)

### Step 1: Import TracerService and SpanKind
```javascript
const tracerService = require('../services/tracerService');
const { SpanKind } = require('@opentelemetry/api');
```

### Step 2: Wrap your operation in executeInSpan
```javascript
return tracerService.executeInSpan(
  'MyOperation',
  async (span) => {
    // Your code here
  },
  { kind: SpanKind.INTERNAL }
);
```

### Step 3: Add attributes
```javascript
tracerService.addCommonAttributes(span, {
  operation: 'myOperation',
  controller: 'MyController',
  method: req.method,
  endpoint: req.path
});
```

### Step 4: Add events
```javascript
span.addEvent('operation.started');
// ... do work ...
span.addEvent('operation.completed');
```

### Step 5: Add success/error attributes
```javascript
// Success
tracerService.addSuccessAttributes(span, 200, {
  'apm.result.count': result.length
});

// Error (automatically handled by executeInSpan)
tracerService.addErrorAttributes(span, error, 500);
```

## Complete Example

```javascript
const tracerService = require('../services/tracerService');
const { SpanKind } = require('@opentelemetry/api');

class MyController {
  static async myMethod(req, res) {
    return tracerService.executeInSpan(
      'MyController.myMethod',
      async (span) => {
        // Add common attributes
        tracerService.addCommonAttributes(span, {
          operation: 'myMethod',
          controller: 'MyController',
          method: req.method,
          endpoint: req.path
        });

        // Add start event
        span.addEvent('myMethod.started');

        try {
          // Your business logic
          const result = await doSomething();

          // Add success event
          span.addEvent('myMethod.success', {
            'result.count': result.length
          });

          // Add success attributes
          tracerService.addSuccessAttributes(span, 200, {
            'apm.result.count': result.length
          });

          res.status(200).json({ success: true, data: result });
        } catch (error) {
          // Add error event
          span.addEvent('myMethod.error');
          
          // Error attributes added automatically by executeInSpan
          res.status(500).json({ success: false, error: error.message });
        }
      },
      { kind: SpanKind.INTERNAL }
    );
  }
}
```

## Nested Spans Example

```javascript
return tracerService.executeInSpan(
  'ParentOperation',
  async (parentSpan) => {
    parentSpan.setAttribute('apm.operation', 'parent');
    
    // Create child span for database operation
    const data = await tracerService.executeInSpan(
      'ParentOperation.database',
      async (dbSpan) => {
        dbSpan.setAttribute('apm.db.operation', 'SELECT');
        return await fetchFromDatabase();
      },
      { kind: SpanKind.CLIENT }
    );
    
    // Continue with parent span
    parentSpan.setAttribute('apm.result.count', data.length);
    return data;
  },
  { kind: SpanKind.INTERNAL }
);
```

## Span Kinds

```javascript
// INTERNAL: Application logic (controllers, services)
{ kind: SpanKind.INTERNAL }

// CLIENT: Outgoing calls (database, HTTP requests)
{ kind: SpanKind.CLIENT }

// SERVER: Incoming requests (usually auto-instrumented)
{ kind: SpanKind.SERVER }

// PRODUCER: Publishing messages (queues, events)
{ kind: SpanKind.PRODUCER }

// CONSUMER: Consuming messages (queue listeners)
{ kind: SpanKind.CONSUMER }
```

## Common Patterns

### Pattern 1: Simple Operation
```javascript
return tracerService.executeInSpan('operation', async (span) => {
  span.setAttribute('apm.operation', 'myOp');
  const result = await doWork();
  tracerService.addSuccessAttributes(span, 200);
  return result;
}, { kind: SpanKind.INTERNAL });
```

### Pattern 2: Operation with Validation
```javascript
return tracerService.executeInSpan('createUser', async (span) => {
  // Validation span
  await tracerService.executeInSpan('createUser.validation', async (validationSpan) => {
    if (!isValid) {
      validationSpan.setAttribute('apm.validation.failed', true);
      throw new Error('VALIDATION_ERROR');
    }
    validationSpan.setAttribute('apm.validation.passed', true);
  }, { kind: SpanKind.INTERNAL });
  
  // Database span
  const user = await tracerService.executeInSpan('createUser.database', async (dbSpan) => {
    dbSpan.setAttribute('apm.db.operation', 'INSERT');
    return await createUser(data);
  }, { kind: SpanKind.CLIENT });
  
  return user;
}, { kind: SpanKind.INTERNAL });
```

### Pattern 3: Operation with Events
```javascript
return tracerService.executeInSpan('processOrder', async (span) => {
  span.addEvent('order.processing_started');
  
  const validated = await validateOrder();
  span.addEvent('order.validated', { 'order.valid': validated });
  
  const charged = await chargePayment();
  span.addEvent('payment.charged', { 'payment.amount': charged });
  
  const shipped = await shipOrder();
  span.addEvent('order.shipped', { 'tracking.id': shipped.trackingId });
  
  return shipped;
}, { kind: SpanKind.INTERNAL });
```

## TracerService Helper Methods

### addCommonAttributes
```javascript
tracerService.addCommonAttributes(span, {
  operation: 'getAllUsers',
  controller: 'UserController',
  method: 'GET',
  endpoint: '/users',
  userId: 123,
  username: 'john'
});
```

### addSuccessAttributes
```javascript
tracerService.addSuccessAttributes(span, 200, {
  'apm.result.count': 10,
  'apm.result.has_data': true
});
```

### addErrorAttributes
```javascript
tracerService.addErrorAttributes(span, error, 500);
// Automatically adds:
// - apm.result.success: false
// - apm.error.occurred: true
// - apm.error.message: error.message
// - apm.error.type: error.constructor.name
// - Records exception
// - Sets error status
```

## When to Use Method 2

### ✅ Perfect For:
- Creating custom spans for specific operations
- Tracking duration of business logic
- Creating nested span hierarchies
- Adding custom events at key points
- Detailed instrumentation of complex workflows
- Separating validation, business logic, and data access

### ❌ Not Suitable For:
- Simple attribute enrichment (use Method 1)
- Cross-service context propagation (use Method 3)
- Global attributes for all spans (use Method 4)

## Comparison with Method 1

| Feature | Method 1 | Method 2 |
|---------|----------|----------|
| Creates spans | ❌ | ✅ |
| Nested spans | ❌ | ✅ |
| Custom events | ❌ | ✅ |
| Span control | ❌ | ✅ |
| Code complexity | Low | Medium |
| Use case | Quick enrichment | Detailed instrumentation |

## Testing

### 1. Make a request
```bash
curl http://localhost:8080/users
```

### 2. Check traces in Jaeger
```
http://localhost:16686
```

### 3. Look for:
- Custom span names (e.g., `UserController.getAllUsers`)
- Nested spans (e.g., `UserController.getAllUsers.database`)
- Custom attributes with `apm.*` prefix
- Events at key points
- Span kinds (INTERNAL, CLIENT)

## Troubleshooting

### Spans not appearing?
- Ensure OpenTelemetry SDK is configured
- Check exporter configuration
- Verify tracer is initialized

### Nested spans not showing?
- Use `executeInSpan` for automatic context propagation
- Check that child spans are created within parent span function

### Events not visible?
- Check backend support (Jaeger shows events in span details)
- Verify event attributes are valid types

## Next Steps

1. ✅ Create TracerService (already done in `services/tracerService.js`)
2. ✅ Import in your controller
3. ✅ Wrap operations in `executeInSpan`
4. ✅ Add attributes and events
5. ✅ Test and view traces

## Full Documentation
See [METHOD_2_SPAN_CREATION.md](./METHOD_2_SPAN_CREATION.md) for complete details.

---

**Quick Reference**: Create custom spans with full control over lifecycle, attributes, and events!

