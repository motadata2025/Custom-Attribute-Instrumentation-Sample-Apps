# OpenTelemetry Custom Attributes in Node.js
## Complete Guide to Instrumentation Methods

> **Version:** 1.0.0  
> **Last Updated:** December 2024  
> **OpenTelemetry API:** @opentelemetry/api v1.x

---

## Table of Contents

1. [Introduction](#introduction)
2. [Method 1: Active Span Enrichment](#method-1-active-span-enrichment)
3. [Method 2: Manual Tracer and Span Creation](#method-2-manual-tracer-and-span-creation)
4. [Method 3: Context-Based Propagation (Baggage)](#method-3-context-based-propagation-baggage)
5. [Method 4: SDK-Level Injection (SpanProcessor)](#method-4-sdk-level-injection-spanprocessor)
6. [Comparison Matrix](#comparison-matrix)
7. [Best Practices](#best-practices)
8. [Common Pitfalls](#common-pitfalls)
9. [Real-World Examples](#real-world-examples)

---

## Introduction

OpenTelemetry provides **four fundamental methods** for adding custom attributes to telemetry data in Node.js applications. Each method serves different use cases and has distinct characteristics.

### Why Custom Attributes Matter

Custom attributes enable you to:
- **Enrich telemetry** with business context (user IDs, tenant IDs, transaction amounts)
- **Enable better debugging** by adding application-specific metadata
- **Improve observability** across distributed systems
- **Support compliance** requirements by tracking specific data points

### The Four Methods

All custom attribute instrumentation in OpenTelemetry Node.js reduces to these four approaches:

1. **Active Span Enrichment** - Add to existing spans
2. **Manual Tracer and Span Creation** - Create new spans with attributes
3. **Context-Based Propagation** - Use Baggage for cross-service data
4. **SDK-Level Injection** - Centralized attribute injection

---

## Method 1: Active Span Enrichment

### Overview

Add custom attributes to an **already active span** without creating a new span. This is the simplest and most common method for adding business context to auto-instrumented spans.

### When to Use

✅ **Use when:**
- Auto-instrumentation is already creating spans (HTTP, database, etc.)
- You want to add business context to existing operations
- You need minimal code changes
- You're enriching framework-generated spans

❌ **Don't use when:**
- No span is currently active
- You need to create a new logical operation
- You want to measure a specific code block's duration

### Basic Example

```javascript
const { trace } = require('@opentelemetry/api');

async function processOrder(orderId, userId, amount) {
  // Get the currently active span (created by auto-instrumentation)
  const span = trace.getActiveSpan();
  
  if (span) {
    // Add business context to the existing span
    span.setAttribute('business.order_id', orderId);
    span.setAttribute('business.user_id', userId);
    span.setAttribute('business.amount', amount);
    span.setAttribute('business.currency', 'USD');
  }
  
  // Your business logic here
  const result = await saveOrderToDatabase(orderId, userId, amount);
  
  return result;
}
```

### Advanced Example with Error Handling

```javascript
const { trace, SpanStatusCode } = require('@opentelemetry/api');

async function processPayment(paymentData) {
  const span = trace.getActiveSpan();
  
  if (span) {
    // Add initial attributes
    span.setAttribute('payment.method', paymentData.method);
    span.setAttribute('payment.amount', paymentData.amount);
    span.setAttribute('payment.currency', paymentData.currency);
    span.setAttribute('customer.id', paymentData.customerId);
  }
  
  try {
    const result = await chargePaymentGateway(paymentData);
    
    if (span) {
      span.setAttribute('payment.transaction_id', result.transactionId);
      span.setAttribute('payment.status', 'success');
      span.setStatus({ code: SpanStatusCode.OK });
    }
    
    return result;
  } catch (error) {
    if (span) {
      span.setAttribute('payment.status', 'failed');
      span.setAttribute('payment.error_code', error.code);
      span.setStatus({
        code: SpanStatusCode.ERROR,
        message: error.message
      });
      span.recordException(error);
    }
    throw error;
  }
}
```

### Key Characteristics

| Aspect | Details |
|--------|---------|
| **Span Creation** | ❌ No new span created |
| **Code Complexity** | ⭐ Low - Simple API call |
| **Performance Impact** | ⭐⭐⭐ Minimal overhead |
| **Auto-instrumentation** | ✅ Works seamlessly |
| **Null Safety** | ⚠️ Must check if span exists |

### Important Notes

1. **Always check for null**: `getActiveSpan()` returns `undefined` if no span is active
2. **Attributes are ignored** if no span exists - no error is thrown
3. **Works with any instrumentation** - manual or automatic
4. **Attributes are added immediately** to the current span
5. **No parent-child relationship** is created

---

## Method 2: Manual Tracer and Span Creation

### Overview

Create a **new span manually** using the tracer API and attach custom attributes. This gives you full control over the span lifecycle and creates a new level in the trace hierarchy.

### When to Use

✅ **Use when:**
- You need to measure a specific operation's duration
- You want to create a logical grouping of work
- You need child spans to be grouped under this span
- You're implementing custom instrumentation

❌ **Don't use when:**
- Auto-instrumentation already covers the operation
- You don't need to measure duration
- You want to avoid creating extra spans

### Understanding startSpan vs startActiveSpan

#### `startSpan` - Simple Duration Measurement

Creates a span but **does NOT** make it the active span. Child spans created during this work will NOT be nested under it.

```javascript
const { trace } = require('@opentelemetry/api');

const tracer = trace.getTracer('my-service');

async function fetchUserData(userId) {
  // Creates a span but doesn't make it active
  const span = tracer.startSpan('fetch-user-data');
  span.setAttribute('user.id', userId);

  try {
    const userData = await database.query('SELECT * FROM users WHERE id = ?', [userId]);
    span.setAttribute('user.found', userData !== null);
    return userData;
  } finally {
    span.end(); // Always end the span
  }
}
```

**Result:** The span measures duration but any child operations (like the database query) will be **siblings**, not children.

#### `startActiveSpan` - Hierarchical Tracing

Creates a span AND makes it the active span. All spans created during the callback will be **children** of this span.

```javascript
const { trace } = require('@opentelemetry/api');

const tracer = trace.getTracer('my-service');

async function processUserOrder(userId, orderId) {
  return tracer.startActiveSpan('process-user-order', async (span) => {
    span.setAttribute('user.id', userId);
    span.setAttribute('order.id', orderId);

    try {
      // These operations will create child spans
      const user = await fetchUser(userId);        // Child span 1
      const order = await fetchOrder(orderId);     // Child span 2
      const result = await validateOrder(order);   // Child span 3

      span.setAttribute('order.valid', result.valid);
      span.setAttribute('order.total', result.total);

      return result;
    } catch (error) {
      span.recordException(error);
      span.setStatus({ code: SpanStatusCode.ERROR });
      throw error;
    } finally {
      span.end(); // Always end the span
    }
  });
}
```

**Result:** Creates a hierarchical trace where all child operations are visually grouped under the parent span.

### Advanced Example: Nested Spans

```javascript
const { trace, SpanKind } = require('@opentelemetry/api');

const tracer = trace.getTracer('order-service', '1.0.0');

async function createOrder(orderData) {
  return tracer.startActiveSpan(
    'create-order',
    {
      kind: SpanKind.SERVER,
      attributes: {
        'order.id': orderData.id,
        'order.customer_id': orderData.customerId,
        'order.items_count': orderData.items.length,
        'order.total_amount': orderData.totalAmount
      }
    },
    async (parentSpan) => {
      try {
        // Nested span for validation
        await tracer.startActiveSpan('validate-order', async (validationSpan) => {
          validationSpan.setAttribute('validation.type', 'business_rules');
          const isValid = await validateOrderRules(orderData);
          validationSpan.setAttribute('validation.result', isValid);
          validationSpan.end();

          if (!isValid) {
            throw new Error('Order validation failed');
          }
        });

        // Nested span for inventory check
        await tracer.startActiveSpan('check-inventory', async (inventorySpan) => {
          inventorySpan.setAttribute('inventory.warehouse', 'main');
          const available = await checkInventory(orderData.items);
          inventorySpan.setAttribute('inventory.available', available);
          inventorySpan.end();

          if (!available) {
            throw new Error('Insufficient inventory');
          }
        });

        // Nested span for payment processing
        const paymentResult = await tracer.startActiveSpan(
          'process-payment',
          { kind: SpanKind.CLIENT },
          async (paymentSpan) => {
            paymentSpan.setAttribute('payment.method', orderData.paymentMethod);
            paymentSpan.setAttribute('payment.amount', orderData.totalAmount);

            const result = await processPayment(orderData);

            paymentSpan.setAttribute('payment.transaction_id', result.transactionId);
            paymentSpan.setAttribute('payment.status', result.status);
            paymentSpan.end();

            return result;
          }
        );

        parentSpan.setAttribute('order.status', 'completed');
        parentSpan.setAttribute('order.payment_transaction_id', paymentResult.transactionId);

        return { success: true, orderId: orderData.id };

      } catch (error) {
        parentSpan.recordException(error);
        parentSpan.setStatus({ code: SpanStatusCode.ERROR, message: error.message });
        parentSpan.setAttribute('order.status', 'failed');
        throw error;
      } finally {
        parentSpan.end();
      }
    }
  );
}
```

### Span Options

```javascript
const spanOptions = {
  // Span kind - describes the relationship between spans
  kind: SpanKind.SERVER,  // SERVER, CLIENT, PRODUCER, CONSUMER, INTERNAL

  // Initial attributes
  attributes: {
    'service.version': '1.2.3',
    'deployment.environment': 'production'
  },

  // Links to other spans (for batch processing, etc.)
  links: [
    {
      context: otherSpanContext,
      attributes: { 'link.type': 'follows_from' }
    }
  ],

  // Start time (defaults to now)
  startTime: Date.now()
};

tracer.startActiveSpan('my-operation', spanOptions, (span) => {
  // Your code here
  span.end();
});
```

### Key Characteristics

| Aspect | Details |
|--------|---------|
| **Span Creation** | ✅ Always creates new span |
| **Code Complexity** | ⭐⭐ Medium - Callback pattern |
| **Performance Impact** | ⭐⭐ Moderate - New span overhead |
| **Hierarchy Control** | ✅ Full control over parent-child |
| **Lifecycle Management** | ⚠️ Must manually call `span.end()` |

### Important Notes

1. **Always end spans**: Use `try/finally` to ensure `span.end()` is called
2. **startActiveSpan requires callback**: All work must be inside the callback
3. **Return values pass through**: The callback's return value is returned
4. **Async/await supported**: Callbacks can be async functions
5. **Span context is propagated**: Child spans automatically link to parent

---

## Method 3: Context-Based Propagation (Baggage)

### Overview

Store business metadata in **context** and propagate it across service boundaries. Baggage is a key-value store that travels with your requests, making data available to all downstream services.

### When to Use

✅ **Use when:**
- You need to propagate data across service boundaries
- You want to add the same attribute to multiple spans
- You need cross-cutting concerns (tenant ID, user ID, request ID)
- You're implementing distributed tracing across microservices

❌ **Don't use when:**
- Data is sensitive (baggage is sent in HTTP headers)
- You only need data in a single service
- The data is large (baggage increases payload size)
- You want attributes automatically added to spans

### Important Security Considerations

⚠️ **WARNING**: Baggage is transmitted in HTTP headers and is visible to:
- Network monitoring tools
- Proxies and load balancers
- Third-party APIs
- Anyone inspecting network traffic

**Never put sensitive data in baggage:**
- ❌ Passwords, API keys, tokens
- ❌ Personal Identifiable Information (PII)
- ❌ Credit card numbers
- ❌ Social security numbers
- ✅ User IDs, tenant IDs (non-sensitive identifiers)
- ✅ Request IDs, correlation IDs
- ✅ Feature flags, A/B test variants

### Basic Example

```javascript
const { context, propagation } = require('@opentelemetry/api');

function handleRequest(req, res) {
  // Create baggage with business context
  const baggage = propagation.createBaggage({
    'tenant.id': { value: req.headers['x-tenant-id'] },
    'user.id': { value: req.user.id },
    'request.id': { value: req.id },
    'feature.flag.new_ui': { value: 'true' }
  });

  // Execute code with baggage in context
  context.with(
    propagation.setBaggage(context.active(), baggage),
    () => {
      // All downstream operations can access this baggage
      processRequest(req, res);
    }
  );
}
```

### Reading Baggage

```javascript
const { propagation, context } = require('@opentelemetry/api');

function processRequest(req, res) {
  // Get baggage from current context
  const baggage = propagation.getBaggage(context.active());

  if (baggage) {
    // Read individual values
    const tenantId = baggage.getEntry('tenant.id')?.value;
    const userId = baggage.getEntry('user.id')?.value;
    const requestId = baggage.getEntry('request.id')?.value;

    console.log('Processing request:', {
      tenantId,
      userId,
      requestId
    });

    // Use baggage values in your logic
    if (tenantId) {
      loadTenantConfiguration(tenantId);
    }
  }
}
```

### Adding Baggage to Spans

**Important**: Baggage is NOT automatically added to spans. You must explicitly read baggage and add it as span attributes.

```javascript
const { trace, propagation, context } = require('@opentelemetry/api');

function addBaggageToSpan() {
  const span = trace.getActiveSpan();
  const baggage = propagation.getBaggage(context.active());

  if (span && baggage) {
    // Manually add baggage entries as span attributes
    baggage.getAllEntries().forEach(([key, entry]) => {
      span.setAttribute(`baggage.${key}`, entry.value);
    });
  }
}

// Usage in your code
async function processOrder(orderId) {
  const span = trace.getActiveSpan();

  // Add baggage to current span
  addBaggageToSpan();

  // Your business logic
  const result = await saveOrder(orderId);
  return result;
}
```

### Advanced Example: Cross-Service Propagation

```javascript
const { context, propagation, trace } = require('@opentelemetry/api');
const axios = require('axios');

// Service A: Setting baggage
async function serviceA_handleRequest(req, res) {
  // Create baggage with request context
  const baggage = propagation.createBaggage({
    'correlation.id': { value: generateCorrelationId() },
    'tenant.id': { value: req.headers['x-tenant-id'] },
    'user.tier': { value: req.user.tier }, // 'premium', 'standard', etc.
    'experiment.variant': { value: 'variant-b' }
  });

  await context.with(
    propagation.setBaggage(context.active(), baggage),
    async () => {
      // Call downstream service - baggage is automatically propagated
      const response = await axios.get('http://service-b/api/data');
      res.json(response.data);
    }
  );
}

// Service B: Reading baggage
async function serviceB_handleRequest(req, res) {
  const baggage = propagation.getBaggage(context.active());
  const span = trace.getActiveSpan();

  if (baggage && span) {
    // Extract baggage values
    const correlationId = baggage.getEntry('correlation.id')?.value;
    const tenantId = baggage.getEntry('tenant.id')?.value;
    const userTier = baggage.getEntry('user.tier')?.value;
    const experimentVariant = baggage.getEntry('experiment.variant')?.value;

    // Add to span for observability
    span.setAttribute('correlation.id', correlationId);
    span.setAttribute('tenant.id', tenantId);
    span.setAttribute('user.tier', userTier);
    span.setAttribute('experiment.variant', experimentVariant);

    // Use in business logic
    const data = await fetchData(tenantId, userTier);

    // Apply experiment variant logic
    if (experimentVariant === 'variant-b') {
      data.features = enhancedFeatures;
    }

    res.json(data);
  }
}
```

### Updating Baggage

```javascript
const { context, propagation } = require('@opentelemetry/api');

function addToBaggage(key, value) {
  const currentBaggage = propagation.getBaggage(context.active());

  // Create new baggage with additional entry
  const newBaggage = currentBaggage
    ? propagation.setBaggageEntry(currentBaggage, key, { value })
    : propagation.createBaggage({ [key]: { value } });

  // Update context with new baggage
  return propagation.setBaggage(context.active(), newBaggage);
}

// Usage
function processStep1() {
  const ctx = addToBaggage('step.completed', 'step1');

  context.with(ctx, () => {
    processStep2();
  });
}
```

### Baggage with Metadata

```javascript
const { propagation } = require('@opentelemetry/api');

const baggage = propagation.createBaggage({
  'user.id': {
    value: '12345',
    metadata: 'sensitive=false;ttl=3600' // Optional metadata
  },
  'session.id': {
    value: 'abc-def-ghi',
    metadata: 'propagate=true'
  }
});
```

### Key Characteristics

| Aspect | Details |
|--------|---------|
| **Span Creation** | ❌ No span created |
| **Code Complexity** | ⭐⭐⭐ Medium-High - Context management |
| **Performance Impact** | ⭐⭐ Moderate - HTTP header overhead |
| **Cross-Service** | ✅ Automatically propagated |
| **Automatic Attributes** | ❌ Must manually add to spans |
| **Security** | ⚠️ Visible in network traffic |

### Important Notes

1. **Not automatically added to spans**: You must explicitly read and add baggage as attributes
2. **Propagated in HTTP headers**: Visible to network monitoring tools
3. **Size matters**: Large baggage increases request payload
4. **Immutable**: Baggage entries cannot be modified, only replaced
5. **Context-bound**: Baggage lives in the context, not in spans
6. **Auto-instrumentation support**: Most HTTP clients automatically propagate baggage

---

## Method 4: SDK-Level Injection (SpanProcessor)

### Overview

Inject custom attributes **centrally** at the SDK level when spans are created. This is a zero-code approach that adds attributes to ALL spans automatically without modifying application code.

### When to Use

✅ **Use when:**
- You need to add attributes to ALL spans
- You want zero application code changes
- You need environment-level metadata (region, version, environment)
- You're implementing cross-cutting concerns
- You want centralized attribute management

❌ **Don't use when:**
- You need access to request-specific data
- You need access to local variables
- You want to add attributes to specific spans only
- The attribute logic is complex or request-dependent

### Basic SpanProcessor Example

```javascript
const { NodeTracerProvider } = require('@opentelemetry/sdk-trace-node');
const { Resource } = require('@opentelemetry/resources');

// Custom SpanProcessor that adds attributes to all spans
class CustomAttributeSpanProcessor {
  onStart(span, parentContext) {
    // Add attributes when span starts
    span.setAttribute('deployment.environment', process.env.NODE_ENV);
    span.setAttribute('service.version', process.env.APP_VERSION);
    span.setAttribute('service.region', process.env.AWS_REGION);
    span.setAttribute('service.instance.id', process.env.HOSTNAME);
  }

  onEnd(span) {
    // Optional: Add attributes when span ends
  }

  shutdown() {
    return Promise.resolve();
  }

  forceFlush() {
    return Promise.resolve();
  }
}

// Register the processor during SDK setup
const provider = new NodeTracerProvider({
  resource: Resource.default().merge(
    new Resource({
      'service.name': 'my-service',
      'service.version': '1.0.0'
    })
  )
});

// Add the custom processor
provider.addSpanProcessor(new CustomAttributeSpanProcessor());
provider.register();
```

### Advanced SpanProcessor with Conditional Logic

```javascript
const { SpanKind, SpanStatusCode } = require('@opentelemetry/api');

class BusinessContextSpanProcessor {
  constructor(config) {
    this.config = config;
  }

  onStart(span, parentContext) {
    // Add global attributes
    span.setAttribute('app.environment', this.config.environment);
    span.setAttribute('app.version', this.config.version);
    span.setAttribute('app.build_number', this.config.buildNumber);

    // Add timestamp
    span.setAttribute('span.start_timestamp', Date.now());

    // Add span kind as attribute for easier querying
    const spanKind = span.kind;
    span.setAttribute('span.kind_name', this.getSpanKindName(spanKind));

    // Add conditional attributes based on span name
    const spanName = span.name;
    if (spanName.includes('http')) {
      span.setAttribute('span.category', 'http');
    } else if (spanName.includes('db') || spanName.includes('database')) {
      span.setAttribute('span.category', 'database');
    } else if (spanName.includes('cache')) {
      span.setAttribute('span.category', 'cache');
    }
  }

  onEnd(span) {
    // Add duration as attribute
    const duration = span.endTime[0] - span.startTime[0];
    span.setAttribute('span.duration_ms', duration / 1000000); // Convert to ms

    // Add status information
    span.setAttribute('span.status_code', span.status.code);

    // Add error flag for easier filtering
    if (span.status.code === SpanStatusCode.ERROR) {
      span.setAttribute('span.has_error', true);
    }
  }

  getSpanKindName(kind) {
    const kinds = {
      [SpanKind.INTERNAL]: 'internal',
      [SpanKind.SERVER]: 'server',
      [SpanKind.CLIENT]: 'client',
      [SpanKind.PRODUCER]: 'producer',
      [SpanKind.CONSUMER]: 'consumer'
    };
    return kinds[kind] || 'unknown';
  }

  shutdown() {
    return Promise.resolve();
  }

  forceFlush() {
    return Promise.resolve();
  }
}

// Usage
const processor = new BusinessContextSpanProcessor({
  environment: process.env.NODE_ENV,
  version: process.env.APP_VERSION,
  buildNumber: process.env.BUILD_NUMBER
});

provider.addSpanProcessor(processor);
```

### SpanProcessor with Baggage Integration

```javascript
const { propagation, context } = require('@opentelemetry/api');

class BaggageToAttributesSpanProcessor {
  constructor(baggageKeys = []) {
    // Specify which baggage keys to add as attributes
    this.baggageKeys = baggageKeys;
  }

  onStart(span, parentContext) {
    const baggage = propagation.getBaggage(parentContext || context.active());

    if (baggage) {
      if (this.baggageKeys.length > 0) {
        // Add only specified baggage keys
        this.baggageKeys.forEach(key => {
          const entry = baggage.getEntry(key);
          if (entry) {
            span.setAttribute(`baggage.${key}`, entry.value);
          }
        });
      } else {
        // Add all baggage entries
        baggage.getAllEntries().forEach(([key, entry]) => {
          span.setAttribute(`baggage.${key}`, entry.value);
        });
      }
    }
  }

  onEnd(span) {}

  shutdown() {
    return Promise.resolve();
  }

  forceFlush() {
    return Promise.resolve();
  }
}

// Usage: Add specific baggage keys to all spans
const baggageProcessor = new BaggageToAttributesSpanProcessor([
  'tenant.id',
  'user.id',
  'correlation.id',
  'request.id'
]);

provider.addSpanProcessor(baggageProcessor);
```

### Complete SDK Setup Example

```javascript
const { NodeTracerProvider } = require('@opentelemetry/sdk-trace-node');
const { Resource } = require('@opentelemetry/resources');
const { SemanticResourceAttributes } = require('@opentelemetry/semantic-conventions');
const { BatchSpanProcessor } = require('@opentelemetry/sdk-trace-base');
const { OTLPTraceExporter } = require('@opentelemetry/exporter-trace-otlp-http');

// Create resource with service information
const resource = Resource.default().merge(
  new Resource({
    [SemanticResourceAttributes.SERVICE_NAME]: 'my-service',
    [SemanticResourceAttributes.SERVICE_VERSION]: '1.0.0',
    [SemanticResourceAttributes.DEPLOYMENT_ENVIRONMENT]: process.env.NODE_ENV
  })
);

// Create provider
const provider = new NodeTracerProvider({ resource });

// Add custom attribute processor (runs first)
provider.addSpanProcessor(new CustomAttributeSpanProcessor());

// Add baggage processor (runs second)
provider.addSpanProcessor(new BaggageToAttributesSpanProcessor(['tenant.id', 'user.id']));

// Add batch processor for export (runs last)
const exporter = new OTLPTraceExporter({
  url: process.env.OTEL_EXPORTER_OTLP_ENDPOINT
});
provider.addSpanProcessor(new BatchSpanProcessor(exporter));

// Register the provider
provider.register();

console.log('OpenTelemetry tracing initialized with custom processors');
```

### Key Characteristics

| Aspect | Details |
|--------|---------|
| **Span Creation** | ❌ No span created |
| **Code Complexity** | ⭐⭐⭐ Medium - SDK configuration |
| **Performance Impact** | ⭐ Minimal - Runs once per span |
| **Application Changes** | ✅ Zero code changes needed |
| **Local Variable Access** | ❌ No access to request data |
| **Scope** | ✅ Affects ALL spans |

### Important Notes

1. **Runs for ALL spans**: Both auto-instrumented and manual spans
2. **No access to local variables**: Can only use global/environment data
3. **Processor order matters**: Processors run in the order they're added
4. **Performance critical**: Keep `onStart` and `onEnd` fast
5. **Use for cross-cutting concerns**: Environment, version, region, etc.
6. **Combine with other methods**: SpanProcessors complement other approaches

---

## Comparison Matrix

### Quick Reference Table

| Method | Span Created | Code Change | Scope | Best For | Performance |
|--------|--------------|-------------|-------|----------|-------------|
| **Active Span Enrichment** | ❌ No | Low | Single span | Business KPIs, request context | ⭐⭐⭐ Excellent |
| **Manual Tracer and Span Creation** | ✅ Yes | High | New operation | Custom workflows, measurements | ⭐⭐ Good |
| **Baggage Propagation** | ❌ No | Medium | Cross-service | Distributed context, correlation | ⭐⭐ Good |
| **SpanProcessor** | ❌ No | None (SDK) | All spans | Environment metadata, zero-code | ⭐⭐⭐ Excellent |

### Detailed Comparison

#### When to Use Each Method

```
┌─────────────────────────────────────────────────────────────┐
│ Decision Tree                                                │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│ Need to add attributes to existing spans?                   │
│ └─ YES → Use Active Span Enrichment (Method 1)             │
│                                                              │
│ Need to measure a specific operation's duration?            │
│ └─ YES → Use Manual Tracer and Span Creation (Method 2)    │
│                                                              │
│ Need data available across multiple services?               │
│ └─ YES → Use Baggage Propagation (Method 3)                │
│                                                              │
│ Need attributes on ALL spans without code changes?          │
│ └─ YES → Use SpanProcessor (Method 4)                      │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Feature Matrix

| Feature | Method 1 | Method 2 | Method 3 | Method 4 |
|---------|----------|----------|----------|----------|
| Works with auto-instrumentation | ✅ | ✅ | ✅ | ✅ |
| Creates new spans | ❌ | ✅ | ❌ | ❌ |
| Access to local variables | ✅ | ✅ | ❌ | ❌ |
| Cross-service propagation | ❌ | ❌ | ✅ | ❌ |
| Automatic attribute addition | ✅ | ✅ | ❌ | ✅ |
| Requires code changes | ✅ | ✅ | ✅ | ❌ |
| Hierarchical tracing | ❌ | ✅ | ❌ | ❌ |
| Security concerns | ✅ Low | ✅ Low | ⚠️ High | ✅ Low |

---

## Best Practices

### 1. Attribute Naming Conventions

Follow OpenTelemetry semantic conventions for consistency:

```javascript
// ✅ GOOD: Use semantic conventions
span.setAttribute('http.method', 'GET');
span.setAttribute('http.status_code', 200);
span.setAttribute('db.system', 'postgresql');
span.setAttribute('db.statement', 'SELECT * FROM users');

// ✅ GOOD: Use namespaced custom attributes
span.setAttribute('business.order_id', orderId);
span.setAttribute('business.customer_tier', 'premium');
span.setAttribute('app.feature_flag.new_checkout', true);

// ❌ BAD: Generic names without namespace
span.setAttribute('id', orderId);
span.setAttribute('tier', 'premium');
span.setAttribute('flag', true);
```

**Recommended Namespaces:**
- `business.*` - Business domain attributes
- `app.*` - Application-specific attributes
- `custom.*` - Custom attributes
- `feature.*` - Feature flags
- `experiment.*` - A/B testing

### 2. Attribute Value Types

```javascript
// ✅ GOOD: Use appropriate types
span.setAttribute('user.id', '12345');              // string
span.setAttribute('order.amount', 99.99);           // number
span.setAttribute('order.is_paid', true);           // boolean
span.setAttribute('order.items', ['item1', 'item2']); // array

// ❌ BAD: Inconsistent types
span.setAttribute('user.id', 12345);  // Should be string for IDs
span.setAttribute('order.amount', '99.99');  // Should be number
```

### 3. Error Handling

```javascript
// ✅ GOOD: Always check for active span
const span = trace.getActiveSpan();
if (span) {
  span.setAttribute('user.id', userId);
}

// ✅ GOOD: Use try-catch for span operations
try {
  await tracer.startActiveSpan('operation', async (span) => {
    try {
      const result = await riskyOperation();
      span.setAttribute('result.success', true);
      return result;
    } catch (error) {
      span.recordException(error);
      span.setStatus({ code: SpanStatusCode.ERROR });
      throw error;
    } finally {
      span.end();
    }
  });
} catch (error) {
  console.error('Operation failed:', error);
}
```

### 4. Performance Considerations

```javascript
// ✅ GOOD: Add attributes once
const span = trace.getActiveSpan();
if (span) {
  span.setAttributes({
    'user.id': userId,
    'user.email': userEmail,
    'user.tier': userTier,
    'user.country': userCountry
  });
}

// ❌ BAD: Multiple setAttribute calls
const span = trace.getActiveSpan();
if (span) {
  span.setAttribute('user.id', userId);
  span.setAttribute('user.email', userEmail);
  span.setAttribute('user.tier', userTier);
  span.setAttribute('user.country', userCountry);
}

// ✅ GOOD: Avoid expensive computations in hot paths
const span = trace.getActiveSpan();
if (span) {
  // Only compute if span exists
  const complexValue = computeExpensiveValue();
  span.setAttribute('computed.value', complexValue);
}
```

### 5. Sensitive Data Handling

```javascript
// ✅ GOOD: Sanitize sensitive data
function addUserAttributes(span, user) {
  span.setAttribute('user.id', user.id);
  span.setAttribute('user.email_hash', hashEmail(user.email));
  span.setAttribute('user.country', user.country);
  // Don't include: password, credit card, SSN, etc.
}

// ❌ BAD: Including sensitive data
function addUserAttributes(span, user) {
  span.setAttribute('user.password', user.password);  // NEVER!
  span.setAttribute('user.credit_card', user.cc);     // NEVER!
  span.setAttribute('user.ssn', user.ssn);            // NEVER!
}

// ✅ GOOD: Redact sensitive parts
function addPaymentAttributes(span, payment) {
  span.setAttribute('payment.method', payment.method);
  span.setAttribute('payment.last4', payment.cardNumber.slice(-4));
  span.setAttribute('payment.amount', payment.amount);
}
```

### 6. Cardinality Management

```javascript
// ✅ GOOD: Low cardinality attributes
span.setAttribute('user.tier', 'premium');  // Limited values
span.setAttribute('http.method', 'GET');    // Limited values
span.setAttribute('order.status', 'completed');  // Limited values

// ⚠️ CAUTION: High cardinality attributes
span.setAttribute('user.id', userId);  // Many unique values
span.setAttribute('order.id', orderId);  // Many unique values

// ❌ BAD: Extremely high cardinality
span.setAttribute('timestamp', Date.now());  // Unique every time
span.setAttribute('random.uuid', generateUUID());  // Unique every time
```

### 7. Combining Methods

```javascript
// ✅ GOOD: Use multiple methods together
const { trace, context, propagation } = require('@opentelemetry/api');

async function handleRequest(req, res) {
  // Method 3: Set baggage for cross-service propagation
  const baggage = propagation.createBaggage({
    'tenant.id': { value: req.tenantId },
    'correlation.id': { value: req.correlationId }
  });

  await context.with(
    propagation.setBaggage(context.active(), baggage),
    async () => {
      // Method 2: Create explicit span for this operation
      await tracer.startActiveSpan('handle-request', async (span) => {
        // Method 1: Enrich with request-specific data
        span.setAttribute('http.method', req.method);
        span.setAttribute('http.url', req.url);
        span.setAttribute('user.id', req.user.id);

        // Method 4: SpanProcessor adds environment data automatically

        const result = await processRequest(req);
        span.end();
        return result;
      });
    }
  );
}
```

---

## Common Pitfalls

### 1. Forgetting to End Spans

```javascript
// ❌ BAD: Span never ends (memory leak!)
function badExample() {
  const span = tracer.startSpan('operation');
  span.setAttribute('key', 'value');
  doSomething();
  // Forgot to call span.end()!
}

// ✅ GOOD: Always end spans
function goodExample() {
  const span = tracer.startSpan('operation');
  try {
    span.setAttribute('key', 'value');
    doSomething();
  } finally {
    span.end();  // Always called, even if error occurs
  }
}

// ✅ BETTER: Use startActiveSpan (auto-ends)
async function betterExample() {
  return tracer.startActiveSpan('operation', async (span) => {
    span.setAttribute('key', 'value');
    const result = await doSomething();
    span.end();
    return result;
  });
}
```

### 2. Assuming Span Exists

```javascript
// ❌ BAD: Crashes if no active span
function badExample(userId) {
  const span = trace.getActiveSpan();
  span.setAttribute('user.id', userId);  // TypeError if span is undefined!
}

// ✅ GOOD: Always check for null
function goodExample(userId) {
  const span = trace.getActiveSpan();
  if (span) {
    span.setAttribute('user.id', userId);
  }
}
```

### 3. Baggage Not Added to Spans

```javascript
// ❌ BAD: Expecting baggage to appear in spans automatically
function badExample() {
  const baggage = propagation.createBaggage({
    'user.id': { value: '12345' }
  });
  context.with(propagation.setBaggage(context.active(), baggage), () => {
    // Baggage exists but won't appear in spans!
    doWork();
  });
}

// ✅ GOOD: Explicitly add baggage to spans
function goodExample() {
  const baggage = propagation.createBaggage({
    'user.id': { value: '12345' }
  });
  context.with(propagation.setBaggage(context.active(), baggage), () => {
    const span = trace.getActiveSpan();
    if (span && baggage) {
      const userId = baggage.getEntry('user.id')?.value;
      span.setAttribute('user.id', userId);
    }
    doWork();
  });
}
```

### 4. High Cardinality Attributes

```javascript
// ❌ BAD: Creates too many unique attribute combinations
function badExample(request) {
  const span = trace.getActiveSpan();
  if (span) {
    span.setAttribute('request.timestamp', Date.now());  // Unique every time!
    span.setAttribute('request.uuid', generateUUID());   // Unique every time!
    span.setAttribute('request.full_url', request.url);  // Too many variations
  }
}

// ✅ GOOD: Use low cardinality attributes
function goodExample(request) {
  const span = trace.getActiveSpan();
  if (span) {
    span.setAttribute('request.method', request.method);  // Limited values
    span.setAttribute('request.path', request.path);      // Reasonable variations
    span.setAttribute('request.status_code', 200);        // Limited values
  }
}
```

### 5. Sensitive Data in Baggage

```javascript
// ❌ BAD: Sensitive data in baggage (visible in HTTP headers!)
function badExample(user) {
  const baggage = propagation.createBaggage({
    'user.password': { value: user.password },      // NEVER!
    'user.credit_card': { value: user.creditCard }, // NEVER!
    'user.api_key': { value: user.apiKey }          // NEVER!
  });
}

// ✅ GOOD: Only non-sensitive identifiers
function goodExample(user) {
  const baggage = propagation.createBaggage({
    'user.id': { value: user.id },
    'user.tier': { value: user.tier },
    'session.id': { value: user.sessionId }
  });
}
```

### 6. Incorrect Span Hierarchy

```javascript
// ❌ BAD: Using startSpan when you want hierarchy
async function badExample() {
  const span = tracer.startSpan('parent-operation');

  // These will be siblings, not children!
  await fetchUser();      // Creates sibling span
  await fetchOrder();     // Creates sibling span

  span.end();
}

// ✅ GOOD: Use startActiveSpan for hierarchy
async function goodExample() {
  return tracer.startActiveSpan('parent-operation', async (span) => {
    // These will be children of parent-operation
    await fetchUser();    // Creates child span
    await fetchOrder();   // Creates child span

    span.end();
  });
}
```

---

## Real-World Examples

### Example 1: E-Commerce Order Processing

```javascript
const { trace, context, propagation } = require('@opentelemetry/api');

class OrderService {
  constructor(tracer) {
    this.tracer = tracer;
  }

  async processOrder(orderData) {
    // Set baggage for cross-service propagation
    const baggage = propagation.createBaggage({
      'order.id': { value: orderData.id },
      'customer.id': { value: orderData.customerId },
      'customer.tier': { value: orderData.customerTier }
    });

    return context.with(
      propagation.setBaggage(context.active(), baggage),
      async () => {
        // Create main span for order processing
        return this.tracer.startActiveSpan(
          'process-order',
          {
            kind: SpanKind.SERVER,
            attributes: {
              'order.id': orderData.id,
              'order.total_amount': orderData.totalAmount,
              'order.items_count': orderData.items.length,
              'customer.id': orderData.customerId,
              'customer.tier': orderData.customerTier
            }
          },
          async (span) => {
            try {
              // Step 1: Validate order
              await this.validateOrder(orderData);

              // Step 2: Check inventory
              const inventoryResult = await this.checkInventory(orderData.items);
              span.setAttribute('inventory.available', inventoryResult.available);

              // Step 3: Process payment
              const paymentResult = await this.processPayment(orderData);
              span.setAttribute('payment.transaction_id', paymentResult.transactionId);
              span.setAttribute('payment.status', paymentResult.status);

              // Step 4: Create shipment
              const shipmentResult = await this.createShipment(orderData);
              span.setAttribute('shipment.tracking_number', shipmentResult.trackingNumber);

              // Step 5: Send confirmation
              await this.sendConfirmation(orderData.customerId, orderData.id);

              span.setAttribute('order.status', 'completed');
              span.setStatus({ code: SpanStatusCode.OK });

              return {
                success: true,
                orderId: orderData.id,
                transactionId: paymentResult.transactionId,
                trackingNumber: shipmentResult.trackingNumber
              };

            } catch (error) {
              span.recordException(error);
              span.setStatus({
                code: SpanStatusCode.ERROR,
                message: error.message
              });
              span.setAttribute('order.status', 'failed');
              span.setAttribute('error.type', error.constructor.name);
              throw error;
            } finally {
              span.end();
            }
          }
        );
      }
    );
  }

  async validateOrder(orderData) {
    return this.tracer.startActiveSpan('validate-order', async (span) => {
      span.setAttribute('validation.type', 'business_rules');

      // Add baggage to span
      const baggage = propagation.getBaggage(context.active());
      if (baggage) {
        const customerId = baggage.getEntry('customer.id')?.value;
        const customerTier = baggage.getEntry('customer.tier')?.value;
        span.setAttribute('customer.id', customerId);
        span.setAttribute('customer.tier', customerTier);
      }

      // Validation logic
      const isValid = orderData.items.length > 0 && orderData.totalAmount > 0;
      span.setAttribute('validation.result', isValid);

      span.end();

      if (!isValid) {
        throw new Error('Invalid order');
      }
    });
  }

  async processPayment(orderData) {
    return this.tracer.startActiveSpan(
      'process-payment',
      { kind: SpanKind.CLIENT },
      async (span) => {
        span.setAttribute('payment.method', orderData.paymentMethod);
        span.setAttribute('payment.amount', orderData.totalAmount);
        span.setAttribute('payment.currency', orderData.currency);

        try {
          // Call payment gateway
          const result = await paymentGateway.charge({
            amount: orderData.totalAmount,
            method: orderData.paymentMethod,
            customerId: orderData.customerId
          });

          span.setAttribute('payment.gateway_response_time', result.responseTime);
          span.setAttribute('payment.transaction_id', result.transactionId);
          span.setAttribute('payment.status', 'success');

          span.end();
          return result;

        } catch (error) {
          span.setAttribute('payment.status', 'failed');
          span.setAttribute('payment.error_code', error.code);
          span.recordException(error);
          span.end();
          throw error;
        }
      }
    );
  }
}
```

### Example 2: Multi-Tenant SaaS Application

```javascript
const { trace, context, propagation } = require('@opentelemetry/api');

// Middleware to set tenant context
function tenantMiddleware(req, res, next) {
  const tenantId = req.headers['x-tenant-id'];
  const userId = req.user?.id;

  if (!tenantId) {
    return res.status(400).json({ error: 'Missing tenant ID' });
  }

  // Set baggage for cross-service propagation
  const baggage = propagation.createBaggage({
    'tenant.id': { value: tenantId },
    'user.id': { value: userId || 'anonymous' },
    'request.id': { value: req.id }
  });

  // Add to current span
  const span = trace.getActiveSpan();
  if (span) {
    span.setAttribute('tenant.id', tenantId);
    span.setAttribute('user.id', userId);
    span.setAttribute('request.id', req.id);
  }

  // Execute with baggage context
  context.with(
    propagation.setBaggage(context.active(), baggage),
    () => next()
  );
}

// Service that uses tenant context
class DataService {
  async getData(filters) {
    const span = trace.getActiveSpan();
    const baggage = propagation.getBaggage(context.active());

    if (span && baggage) {
      const tenantId = baggage.getEntry('tenant.id')?.value;
      const userId = baggage.getEntry('user.id')?.value;

      span.setAttribute('tenant.id', tenantId);
      span.setAttribute('user.id', userId);
      span.setAttribute('query.filters_count', Object.keys(filters).length);

      // Tenant-specific query
      const data = await database.query(
        'SELECT * FROM data WHERE tenant_id = ? AND ...',
        [tenantId, ...filters]
      );

      span.setAttribute('query.results_count', data.length);

      return data;
    }
  }
}
```

---

## Summary

### The Four Methods at a Glance

1. **Active Span Enrichment** - Simplest way to add business context to existing spans
2. **Manual Tracer and Span Creation** - Full control for custom operations and hierarchies
3. **Baggage Propagation** - Cross-service context propagation (use with caution)
4. **SpanProcessor** - Zero-code centralized attribute injection

### Key Takeaways

✅ **Always check if span exists** before adding attributes
✅ **Use semantic conventions** for standard attributes
✅ **Namespace custom attributes** (business.*, app.*, etc.)
✅ **Never put sensitive data in baggage**
✅ **Always end spans** (use try/finally or startActiveSpan)
✅ **Manage cardinality** - avoid unique values per request
✅ **Combine methods** for comprehensive instrumentation

### Further Reading

- [OpenTelemetry Specification](https://opentelemetry.io/docs/specs/otel/)
- [Semantic Conventions](https://opentelemetry.io/docs/specs/semconv/)
- [Node.js SDK Documentation](https://opentelemetry.io/docs/languages/js/)
- [Baggage API](https://opentelemetry.io/docs/concepts/signals/baggage/)

---

**Document Version:** 1.0.0
**Last Updated:** December 2024
**Maintained by:** OpenTelemetry Community


