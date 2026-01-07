# The 4 Methods - OpenTelemetry Custom Attributes

A comprehensive guide to adding custom attributes in OpenTelemetry Node.js applications.

---

## 📋 Table of Contents

1. [Method 1: Active Span Enrichment](#method-1-active-span-enrichment)
2. [Method 2: Span Creation](#method-2-span-creation)
3. [Method 3: Baggage Propagation](#method-3-baggage-propagation)
4. [Method 4: SpanProcessor](#method-4-spanprocessor)
5. [Comparison Matrix](#-comparison-matrix)
6. [Best Practices](#-best-practices-checklist)
7. [Resources](#-resources)

---

## 🎯 The 4 Methods

### Method 1: Active Span Enrichment
**Add attributes to existing spans created by auto-instrumentation**

#### Basic Example
```javascript
const { trace } = require('@opentelemetry/api');

// Get the currently active span
const span = trace.getActiveSpan();
if (span) {
  span.setAttribute('user.id', userId);
  span.setAttribute('user.role', 'admin');
  span.setAttribute('business.transaction_amount', 1500.50);
}
```

#### Advanced Example with Multiple Attributes
```javascript
const { trace } = require('@opentelemetry/api');

app.post('/checkout', async (req, res) => {
  const span = trace.getActiveSpan();

  if (span) {
    // Add business context
    span.setAttribute('checkout.cart_id', req.body.cartId);
    span.setAttribute('checkout.total_items', req.body.items.length);
    span.setAttribute('checkout.total_amount', calculateTotal(req.body.items));
    span.setAttribute('checkout.payment_method', req.body.paymentMethod);

    // Add user context
    span.setAttribute('user.id', req.user.id);
    span.setAttribute('user.tier', req.user.tier);

    // Add array attributes
    span.setAttribute('checkout.product_ids', req.body.items.map(i => i.productId));
  }

  // Your business logic here
});
```

#### When to Use
- ✅ Adding business context to HTTP requests
- ✅ Enriching database query spans
- ✅ Adding user information to existing operations
- ✅ Quick wins with minimal code changes

#### Pros & Cons
**Pros:**
- Minimal code changes
- Works with auto-instrumentation
- Low performance overhead
- Easy to implement

**Cons:**
- Only works if a span already exists
- Cannot control span lifecycle
- Limited to existing span hierarchy

**Best for:** Business KPIs, request context, user tracking
**Complexity:** ⭐ Low
**Code Changes:** Minimal

---

### Method 2: Span Creation
**Create new spans with full control using the tracer API**

#### Setup: Acquire a Tracer
```javascript
const { trace } = require('@opentelemetry/api');

// Get a tracer for your service
const tracer = trace.getTracer('my-service-name', '1.0.0');
```

#### Basic Example: startActiveSpan
```javascript
tracer.startActiveSpan('validate-order', (span) => {
  try {
    // Add attributes
    span.setAttribute('order.id', orderId);
    span.setAttribute('order.total', 150.50);

    // Add events
    span.addEvent('validation_started');

    // Your business logic
    const result = validateOrder(orderId);

    span.addEvent('validation_completed');
    span.setStatus({ code: SpanStatusCode.OK });
  } catch (error) {
    // Record errors
    span.recordException(error);
    span.setStatus({
      code: SpanStatusCode.ERROR,
      message: error.message
    });
    throw error;
  } finally {
    span.end(); // Always end the span
  }
});
```

#### Advanced Example: Nested Spans
```javascript
const { trace, SpanStatusCode } = require('@opentelemetry/api');

async function processOrder(orderId) {
  return tracer.startActiveSpan('process-order', async (parentSpan) => {
    parentSpan.setAttribute('order.id', orderId);

    try {
      // Child span 1: Validate
      await tracer.startActiveSpan('validate-order', async (validateSpan) => {
        validateSpan.setAttribute('validation.type', 'inventory');
        const isValid = await validateInventory(orderId);
        validateSpan.setAttribute('validation.result', isValid);
        validateSpan.end();
        return isValid;
      });

      // Child span 2: Payment
      await tracer.startActiveSpan('process-payment', async (paymentSpan) => {
        paymentSpan.setAttribute('payment.method', 'credit_card');
        const paymentResult = await processPayment(orderId);
        paymentSpan.setAttribute('payment.transaction_id', paymentResult.txnId);
        paymentSpan.end();
        return paymentResult;
      });

      // Child span 3: Ship
      await tracer.startActiveSpan('ship-order', async (shipSpan) => {
        shipSpan.setAttribute('shipping.carrier', 'FedEx');
        const trackingId = await shipOrder(orderId);
        shipSpan.setAttribute('shipping.tracking_id', trackingId);
        shipSpan.end();
        return trackingId;
      });

      parentSpan.setStatus({ code: SpanStatusCode.OK });
    } catch (error) {
      parentSpan.recordException(error);
      parentSpan.setStatus({ code: SpanStatusCode.ERROR, message: error.message });
      throw error;
    } finally {
      parentSpan.end();
    }
  });
}
```

#### Span Kinds
```javascript
const { SpanKind } = require('@opentelemetry/api');

// SERVER: Handling incoming requests
tracer.startActiveSpan('http-handler', { kind: SpanKind.SERVER }, (span) => {
  // Handle HTTP request
  span.end();
});

// CLIENT: Making outgoing requests
tracer.startActiveSpan('api-call', { kind: SpanKind.CLIENT }, (span) => {
  // Call external API
  span.end();
});

// INTERNAL: Internal operations
tracer.startActiveSpan('calculate-tax', { kind: SpanKind.INTERNAL }, (span) => {
  // Business logic
  span.end();
});

// PRODUCER: Publishing messages
tracer.startActiveSpan('publish-event', { kind: SpanKind.PRODUCER }, (span) => {
  // Publish to queue
  span.end();
});

// CONSUMER: Consuming messages
tracer.startActiveSpan('consume-event', { kind: SpanKind.CONSUMER }, (span) => {
  // Process message
  span.end();
});
```

#### Manual Span Creation (Non-Active)
```javascript
// Create span without making it active
const span = tracer.startSpan('background-task');

try {
  span.setAttribute('task.type', 'cleanup');
  // Do work
  span.setStatus({ code: SpanStatusCode.OK });
} catch (error) {
  span.recordException(error);
  span.setStatus({ code: SpanStatusCode.ERROR });
} finally {
  span.end();
}
```

#### When to Use
- ✅ Tracking custom business operations
- ✅ Measuring specific function durations
- ✅ Creating detailed trace hierarchies
- ✅ Tracking background jobs or async tasks
- ✅ Adding custom events and exceptions

#### Pros & Cons
**Pros:**
- Full control over span lifecycle
- Can create custom hierarchies
- Add events and exceptions
- Set custom span kinds
- Works for any code path

**Cons:**
- More code required
- Must remember to end spans
- Higher complexity
- Potential for span leaks if not ended

**Best for:** Custom workflows, duration tracking, detailed instrumentation
**Complexity:** ⭐⭐ Medium
**Code Changes:** Moderate

---

### Method 3: Baggage Propagation
**Cross-service context propagation - pass data across service boundaries**

#### What is Baggage?
Baggage is a key-value store that propagates across service boundaries alongside trace context. It's sent in HTTP headers and available to all downstream services.

#### Basic Example
```javascript
const { propagation, context } = require('@opentelemetry/api');

// Create baggage
const baggage = propagation.createBaggage({
  'tenant.id': { value: 'tenant-123' },
  'user.id': { value: 'user-456' },
  'request.priority': { value: 'high' }
});

// Set baggage in context
context.with(propagation.setBaggage(context.active(), baggage), () => {
  // All operations here and downstream will have access to baggage
  makeApiCall(); // Baggage automatically propagates
});
```

#### Reading Baggage
```javascript
const { propagation, context } = require('@opentelemetry/api');

// Get current baggage
const currentBaggage = propagation.getBaggage(context.active());

// Read specific value
const tenantId = currentBaggage?.getEntry('tenant.id')?.value;

// Add to span attributes
const span = trace.getActiveSpan();
if (span && tenantId) {
  span.setAttribute('tenant.id', tenantId);
}
```

#### Advanced Example: Multi-Service Propagation
```javascript
const { propagation, context, trace } = require('@opentelemetry/api');

// Service A: Set baggage
app.post('/api/order', (req, res) => {
  const baggage = propagation.createBaggage({
    'tenant.id': { value: req.headers['x-tenant-id'] },
    'correlation.id': { value: generateCorrelationId() },
    'user.tier': { value: req.user.tier },
    'feature.flags': { value: JSON.stringify(req.featureFlags) }
  });

  context.with(propagation.setBaggage(context.active(), baggage), async () => {
    // Call Service B - baggage propagates automatically
    await fetch('http://service-b/process', {
      method: 'POST',
      body: JSON.stringify(req.body)
    });
  });
});

// Service B: Read baggage
app.post('/process', (req, res) => {
  const baggage = propagation.getBaggage(context.active());
  const tenantId = baggage?.getEntry('tenant.id')?.value;
  const correlationId = baggage?.getEntry('correlation.id')?.value;

  // Add to current span
  const span = trace.getActiveSpan();
  if (span) {
    span.setAttribute('tenant.id', tenantId);
    span.setAttribute('correlation.id', correlationId);
  }

  // Use in business logic
  processOrder(tenantId, req.body);
});
```

#### Adding Baggage to Existing Context
```javascript
const { propagation, context } = require('@opentelemetry/api');

// Get current baggage
let baggage = propagation.getBaggage(context.active()) || propagation.createBaggage();

// Add new entry
baggage = baggage.setEntry('new.key', { value: 'new-value' });

// Update context
context.with(propagation.setBaggage(context.active(), baggage), () => {
  // New baggage is now active
});
```

#### Automatic Span Attribute Injection
Some languages have Baggage Span Processors that automatically add baggage as span attributes:

```javascript
// Custom processor to auto-add baggage to spans
const { propagation } = require('@opentelemetry/api');

class BaggageSpanProcessor {
  onStart(span, parentContext) {
    const baggage = propagation.getBaggage(parentContext);
    if (baggage) {
      baggage.getAllEntries().forEach(([key, entry]) => {
        span.setAttribute(`baggage.${key}`, entry.value);
      });
    }
  }

  onEnd() {}
  shutdown() { return Promise.resolve(); }
  forceFlush() { return Promise.resolve(); }
}

// Add to provider
provider.addSpanProcessor(new BaggageSpanProcessor());
```

#### When to Use
- ✅ Multi-tenant applications (tenant ID)
- ✅ Correlation IDs across services
- ✅ User context propagation
- ✅ Feature flags
- ✅ Request priority/routing
- ✅ A/B test variants

#### Security Considerations
**⚠️ CRITICAL SECURITY WARNING:**
- Baggage is sent in **HTTP headers** (visible in network traffic)
- **Never** put sensitive data: passwords, API keys, PII, tokens
- Baggage is **not encrypted** by default
- Anyone inspecting network traffic can see baggage
- Downstream services can read and modify baggage

**Safe to use:**
- Tenant IDs (non-sensitive)
- Correlation IDs
- Request IDs
- Feature flag names
- User tier/role (if not sensitive)

**Never use:**
- Passwords
- API keys
- Credit card numbers
- Personal identifiable information (PII)
- Authentication tokens

#### Pros & Cons
**Pros:**
- Propagates across service boundaries
- Available to all downstream services
- No need to pass data in request bodies
- Automatic propagation with HTTP instrumentation

**Cons:**
- Sent in HTTP headers (security risk)
- Increases network payload
- No built-in integrity checks
- Can be modified by intermediaries

**Best for:** Distributed tracing, correlation IDs, multi-tenant context
**Complexity:** ⭐⭐⭐ Medium-High
**Code Changes:** Moderate
**⚠️ Security:** Never put sensitive data in baggage!

---

### Method 4: SpanProcessor
**Zero-code centralized injection - enrich ALL spans automatically**

#### What is a SpanProcessor?
A SpanProcessor intercepts every span at creation and completion, allowing you to add attributes, filter spans, or modify telemetry without changing application code.

#### Basic Example
```javascript
const { NodeTracerProvider } = require('@opentelemetry/sdk-trace-node');

class CustomSpanProcessor {
  onStart(span, parentContext) {
    // Called when span starts
    span.setAttribute('app.version', process.env.APP_VERSION);
    span.setAttribute('app.environment', process.env.NODE_ENV);
    span.setAttribute('app.hostname', require('os').hostname());
  }

  onEnd(span) {
    // Called when span ends (optional)
  }

  shutdown() {
    return Promise.resolve();
  }

  forceFlush() {
    return Promise.resolve();
  }
}

// Register processor
const provider = new NodeTracerProvider();
provider.addSpanProcessor(new CustomSpanProcessor());
provider.register();
```

#### Advanced Example: Environment & Resource Attributes
```javascript
const { NodeTracerProvider } = require('@opentelemetry/sdk-trace-node');
const { Resource } = require('@opentelemetry/resources');
const { SemanticResourceAttributes } = require('@opentelemetry/semantic-conventions');

class EnvironmentSpanProcessor {
  onStart(span, parentContext) {
    // Add deployment info
    span.setAttribute('deployment.environment', process.env.DEPLOYMENT_ENV);
    span.setAttribute('deployment.version', process.env.APP_VERSION);
    span.setAttribute('deployment.region', process.env.AWS_REGION);

    // Add runtime info
    span.setAttribute('runtime.node_version', process.version);
    span.setAttribute('runtime.platform', process.platform);

    // Add custom business context
    span.setAttribute('business.cost_center', process.env.COST_CENTER);
    span.setAttribute('business.team', process.env.TEAM_NAME);
  }

  onEnd() {}
  shutdown() { return Promise.resolve(); }
  forceFlush() { return Promise.resolve(); }
}

const provider = new NodeTracerProvider({
  resource: new Resource({
    [SemanticResourceAttributes.SERVICE_NAME]: 'my-service',
    [SemanticResourceAttributes.SERVICE_VERSION]: '1.0.0',
  }),
});

provider.addSpanProcessor(new EnvironmentSpanProcessor());
provider.register();
```

#### Filtering Spans
```javascript
class FilteringSpanProcessor {
  constructor(wrappedProcessor) {
    this.wrappedProcessor = wrappedProcessor;
  }

  onStart(span, parentContext) {
    // Add attributes to all spans
    span.setAttribute('filtered', 'true');
    this.wrappedProcessor.onStart(span, parentContext);
  }

  onEnd(span) {
    // Filter out health check spans
    const spanName = span.name;
    if (spanName.includes('/health') || spanName.includes('/ping')) {
      // Don't export health check spans
      return;
    }

    this.wrappedProcessor.onEnd(span);
  }

  shutdown() {
    return this.wrappedProcessor.shutdown();
  }

  forceFlush() {
    return this.wrappedProcessor.forceFlush();
  }
}

// Wrap the exporter processor
const { BatchSpanProcessor } = require('@opentelemetry/sdk-trace-base');
const { OTLPTraceExporter } = require('@opentelemetry/exporter-trace-otlp-http');

const exporter = new OTLPTraceExporter();
const batchProcessor = new BatchSpanProcessor(exporter);
const filteringProcessor = new FilteringSpanProcessor(batchProcessor);

provider.addSpanProcessor(filteringProcessor);
```

#### Conditional Attribute Injection
```javascript
class ConditionalSpanProcessor {
  onStart(span, parentContext) {
    const spanName = span.name;

    // Add attributes based on span type
    if (spanName.startsWith('HTTP')) {
      span.setAttribute('span.category', 'http');
      span.setAttribute('monitoring.alert_enabled', true);
    } else if (spanName.includes('database')) {
      span.setAttribute('span.category', 'database');
      span.setAttribute('monitoring.slow_query_threshold_ms', 1000);
    } else if (spanName.includes('cache')) {
      span.setAttribute('span.category', 'cache');
      span.setAttribute('monitoring.cache_hit_tracking', true);
    }

    // Add timestamp
    span.setAttribute('span.created_at', new Date().toISOString());
  }

  onEnd() {}
  shutdown() { return Promise.resolve(); }
  forceFlush() { return Promise.resolve(); }
}

provider.addSpanProcessor(new ConditionalSpanProcessor());
```

#### Sampling Based on Attributes
```javascript
class AttributeBasedSamplingProcessor {
  onStart(span, parentContext) {
    // Add sampling decision attribute
    const shouldSample = Math.random() < 0.1; // 10% sampling
    span.setAttribute('sampling.decision', shouldSample);
    span.setAttribute('sampling.rate', 0.1);
  }

  onEnd() {}
  shutdown() { return Promise.resolve(); }
  forceFlush() { return Promise.resolve(); }
}
```

#### Multiple Processors
```javascript
const { NodeTracerProvider } = require('@opentelemetry/sdk-trace-node');
const { BatchSpanProcessor } = require('@opentelemetry/sdk-trace-base');
const { OTLPTraceExporter } = require('@opentelemetry/exporter-trace-otlp-http');

const provider = new NodeTracerProvider();

// Processor 1: Add environment attributes
provider.addSpanProcessor(new EnvironmentSpanProcessor());

// Processor 2: Add baggage as attributes
provider.addSpanProcessor(new BaggageSpanProcessor());

// Processor 3: Filter spans
const exporter = new OTLPTraceExporter();
const batchProcessor = new BatchSpanProcessor(exporter);
provider.addSpanProcessor(new FilteringSpanProcessor(batchProcessor));

provider.register();
```

#### When to Use
- ✅ Adding environment metadata to ALL spans
- ✅ Centralized attribute injection
- ✅ Filtering unwanted spans (health checks)
- ✅ Adding deployment/version info
- ✅ Zero-code instrumentation
- ✅ Consistent attributes across all spans

#### Pros & Cons
**Pros:**
- Zero application code changes
- Centralized configuration
- Applies to ALL spans automatically
- Easy to maintain
- Consistent attributes

**Cons:**
- Applies to all spans (can't be selective per-span)
- Requires SDK configuration
- Less flexible than per-span attributes
- Performance impact on every span

**Best for:** Environment metadata, zero-code enrichment, global attributes
**Complexity:** ⭐⭐ Medium
**Code Changes:** None (SDK configuration only)

---

## 📊 Comparison Matrix

| Method | Span Created | Code Change | Scope | Best For | Performance | Propagates |
|--------|--------------|-------------|-------|----------|-------------|------------|
| **Active Span Enrichment** | ❌ | Low | Single span | Business KPIs, user context | ⭐⭐⭐ Excellent | ❌ |
| **Span Creation** | ✅ | High | Custom hierarchy | Custom workflows, duration tracking | ⭐⭐ Good | ❌ |
| **Baggage Propagation** | ❌ | Medium | Cross-service | Distributed tracing, correlation IDs | ⭐⭐ Good | ✅ |
| **SpanProcessor** | ❌ | None (SDK) | All spans | Environment metadata, global attributes | ⭐⭐⭐ Excellent | ❌ |

### Detailed Comparison

#### When to Use Each Method

| Scenario | Recommended Method | Why |
|----------|-------------------|-----|
| Add user ID to HTTP request | Active Span Enrichment | Quick, minimal code |
| Track custom business operation | Span Creation | Full control, custom duration |
| Pass tenant ID across services | Baggage Propagation | Cross-service context |
| Add app version to all spans | SpanProcessor | Zero-code, centralized |
| Track payment processing steps | Span Creation | Nested spans, detailed tracking |
| Add feature flags globally | Baggage Propagation | Available everywhere |
| Filter health check spans | SpanProcessor | Centralized filtering |
| Add cart total to checkout | Active Span Enrichment | Business context |

#### Attribute Cardinality Guidelines

| Cardinality | Example | Safe? | Notes |
|-------------|---------|-------|-------|
| **Low** (< 100 values) | `user.tier`, `payment.method`, `region` | ✅ Safe | Ideal for aggregation |
| **Medium** (100-10K values) | `product.category`, `error.type` | ⚠️ Caution | Monitor backend performance |
| **High** (> 10K values) | `user.id`, `order.id`, `session.id` | ⚠️ Caution | Use for filtering, not aggregation |
| **Unbounded** | `user.email`, `full.url`, `sql.query` | ❌ Avoid | Can overwhelm backend |

---

## ✅ Best Practices Checklist

### General Best Practices
- ✅ **Always check if span exists** before adding attributes
  ```javascript
  const span = trace.getActiveSpan();
  if (span) {
    span.setAttribute('key', 'value');
  }
  ```

- ✅ **Always end spans** (use try/finally or startActiveSpan)
  ```javascript
  const span = tracer.startSpan('operation');
  try {
    // work
  } finally {
    span.end(); // Always called
  }
  ```

- ✅ **Use semantic conventions** for standard attributes
  ```javascript
  // Good: Use semantic conventions
  span.setAttribute('http.method', 'POST');
  span.setAttribute('http.status_code', 200);

  // Bad: Custom names for standard concepts
  span.setAttribute('request_method', 'POST');
  ```

- ✅ **Namespace custom attributes** (business.*, app.*, custom.*)
  ```javascript
  // Good: Namespaced
  span.setAttribute('business.transaction_amount', 150.50);
  span.setAttribute('app.feature_flag', 'new_checkout');

  // Bad: No namespace
  span.setAttribute('transaction_amount', 150.50);
  ```

- ✅ **Never put sensitive data in baggage**
  ```javascript
  // Bad: Sensitive data
  baggage.setEntry('user.password', { value: password }); // ❌
  baggage.setEntry('credit.card', { value: ccNumber }); // ❌

  // Good: Non-sensitive IDs
  baggage.setEntry('user.id', { value: userId }); // ✅
  baggage.setEntry('tenant.id', { value: tenantId }); // ✅
  ```

- ✅ **Manage cardinality** - avoid unique values per request
  ```javascript
  // Bad: High cardinality
  span.setAttribute('user.email', 'user@example.com'); // ❌
  span.setAttribute('full.url', 'https://...?token=xyz'); // ❌

  // Good: Low cardinality
  span.setAttribute('user.tier', 'premium'); // ✅
  span.setAttribute('url.path', '/api/users'); // ✅
  ```

- ✅ **Use appropriate types** (string, number, boolean, array)
  ```javascript
  span.setAttribute('order.total', 150.50); // number
  span.setAttribute('order.id', 'order-123'); // string
  span.setAttribute('order.is_paid', true); // boolean
  span.setAttribute('order.items', ['item1', 'item2']); // array
  ```

---

## 📊 Supported Data Types for Custom Attributes

OpenTelemetry supports specific data types for attribute values. Understanding these types is crucial for proper instrumentation.

### Language/Runtime Support Matrix

| Language/Runtime | Supported Datatype |
|------------------|-------------------|
| **Java** | `boolean`, `Boolean`, `double`, `Double`, `int`, `Integer`, `long`, `Long`, `String`, `List<Boolean>`, `List<Double>`, `List<Integer>`, `List<Long>`, `List<String>` |
| **.NET** | `bool`, `double`, `float`, `int`, `long`, `string`, `bool[]`, `double[]`, `float[]`, `int[]`, `long[]`, `string[]` |
| **Python** | `bool`, `int`, `float`, `str`, `Sequence[bool]`, `Sequence[int]`, `Sequence[float]`, `Sequence[str]` |
| **Node.js** | `string`, `number`, `boolean`, `Array<string>`, `Array<number>`, `Array<boolean>`, `Array<null \| undefined \| string>`, `Array<null \| undefined \| number>`, `Array<null \| undefined \| boolean>` |

### Node.js TypeScript Definition

From the official `@opentelemetry/api` package:

```typescript
/**
 * Attribute values may be any non-nullish primitive value except an object.
 *
 * null or undefined attribute values are invalid and will result in undefined behavior.
 */
export type AttributeValue =
  | string
  | number
  | boolean
  | Array<null | undefined | string>
  | Array<null | undefined | number>
  | Array<null | undefined | boolean>;
```

**Source:** [`@opentelemetry/api/src/common/Attributes.ts`](https://github.com/open-telemetry/opentelemetry-js/blob/main/api/src/common/Attributes.ts)

---

### Primitive Types (Stable)

#### 1. String
```javascript
span.setAttribute('user.name', 'John Doe');
span.setAttribute('http.method', 'POST');
span.setAttribute('db.statement', 'SELECT * FROM users');
span.setAttribute('error.message', 'Connection timeout');

// Empty strings are valid
span.setAttribute('optional.field', ''); // ✅ Valid
```

**Limits:**
- Default max length: **Infinity** (configurable via `AttributeValueLengthLimit`)
- Can be truncated if exceeds limit
- Each character counts as 1

---

#### 2. Number (Double Precision Floating Point - IEEE 754-1985)
```javascript
// Integers
span.setAttribute('http.status_code', 200);
span.setAttribute('user.age', 25);
span.setAttribute('retry.count', 3);

// Floating point
span.setAttribute('order.total', 1599.99);
span.setAttribute('response.time_ms', 45.67);
span.setAttribute('cpu.usage_percent', 78.5);

// Zero is valid
span.setAttribute('error.count', 0); // ✅ Valid and meaningful

// Negative numbers
span.setAttribute('temperature.celsius', -15.5);
```

**Note:** JavaScript numbers are always 64-bit floating point (IEEE 754)

---

#### 3. Boolean
```javascript
span.setAttribute('user.is_authenticated', true);
span.setAttribute('cache.hit', false);
span.setAttribute('payment.is_successful', true);
span.setAttribute('feature.enabled', false);
```

---

#### 4. Signed 64-bit Integer
```javascript
// In JavaScript, use regular numbers (they're 64-bit floats)
span.setAttribute('user.id', 1234567890);
span.setAttribute('timestamp.unix', Date.now());
span.setAttribute('file.size_bytes', 1048576);

// For very large integers, use BigInt (if supported by exporter)
span.setAttribute('large.number', Number(9007199254740991n));
```

---

### Array Types (Stable)

#### Homogeneous Arrays (Same Type)
Arrays must contain values of the **same primitive type**.

```javascript
// ✅ String arrays
span.setAttribute('user.roles', ['admin', 'editor', 'viewer']);
span.setAttribute('product.tags', ['electronics', 'sale', 'featured']);
span.setAttribute('http.request.headers', ['Content-Type', 'Authorization']);

// ✅ Number arrays
span.setAttribute('product.prices', [19.99, 29.99, 39.99]);
span.setAttribute('response.times_ms', [45, 67, 89, 123]);
span.setAttribute('user.scores', [100, 95, 87]);

// ✅ Boolean arrays
span.setAttribute('feature.flags', [true, false, true, true]);
span.setAttribute('validation.results', [true, true, false]);

// ✅ Empty arrays are valid
span.setAttribute('empty.list', []); // ✅ Valid and meaningful
```

#### ❌ Heterogeneous Arrays (Mixed Types) - NOT ALLOWED
```javascript
// ❌ INVALID: Mixed types in array
span.setAttribute('mixed', ['string', 123, true]); // ❌ NOT ALLOWED

// ❌ INVALID: Nested arrays of different types
span.setAttribute('nested', [[1, 2], ['a', 'b']]); // ❌ NOT ALLOWED
```

---

### Advanced Types (Development Status)

#### 5. Byte Array (Status: Development)
```javascript
// Byte arrays for binary data
const buffer = Buffer.from('Hello World', 'utf-8');
span.setAttribute('binary.data', buffer);

// Image data
const imageBuffer = fs.readFileSync('image.png');
span.setAttribute('image.thumbnail', imageBuffer);
```

**Limits:**
- Default max length: **Infinity** (configurable via `AttributeValueLengthLimit`)
- Each byte counts as 1

---

#### 6. Array of AnyValue (Status: Development)
Nested arrays with mixed types (if supported by implementation).

```javascript
// Nested arrays (Development status - check your SDK)
span.setAttribute('nested.array', [
  ['item1', 'item2'],
  ['item3', 'item4']
]);

// Array of mixed AnyValue types (Development status)
span.setAttribute('complex.array', [
  'string',
  123,
  true,
  ['nested', 'array']
]);
```

---

#### 7. Map/Object (Status: Development)
```javascript
// Map/Object values (Development status - check your SDK)
span.setAttribute('user.metadata', {
  tier: 'premium',
  region: 'us-east-1',
  credits: 100
});

// Nested objects
span.setAttribute('request.context', {
  headers: {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer token'
  },
  query: {
    page: 1,
    limit: 10
  }
});

// Deep nesting allowed (equivalent to JSON object)
span.setAttribute('complex.object', {
  level1: {
    level2: {
      level3: {
        value: 'deep'
      }
    }
  }
});
```

**Note:** Map keys are case-sensitive and must be unique.

---

#### 8. Null/Undefined (Status: Development)
```javascript
// Null values (if supported by language)
span.setAttribute('optional.field', null); // Development status
span.setAttribute('optional.field', undefined); // Development status

// In arrays (should be avoided but preserved if present)
span.setAttribute('array.with.null', ['value1', null, 'value3']); // Preserved as-is
```

**Note:**
- Null is valid but should be avoided in arrays
- If exporter doesn't support null, it may be replaced with `0`, `false`, or `''`

---

### Complete Data Type Examples

```javascript
const { trace, SpanStatusCode } = require('@opentelemetry/api');

const span = trace.getActiveSpan();

if (span) {
  // ========================================
  // PRIMITIVE TYPES (Stable)
  // ========================================

  // Strings
  span.setAttribute('user.email', 'user@example.com');
  span.setAttribute('http.url', 'https://api.example.com/users');

  // Numbers (integers)
  span.setAttribute('http.status_code', 200);
  span.setAttribute('user.age', 30);

  // Numbers (floats)
  span.setAttribute('order.total', 1599.99);
  span.setAttribute('response.time_ms', 45.67);

  // Booleans
  span.setAttribute('user.is_premium', true);
  span.setAttribute('cache.hit', false);

  // ========================================
  // ARRAY TYPES (Stable)
  // ========================================

  // String arrays
  span.setAttribute('user.roles', ['admin', 'editor']);
  span.setAttribute('product.tags', ['electronics', 'sale']);

  // Number arrays
  span.setAttribute('product.prices', [19.99, 29.99, 39.99]);
  span.setAttribute('scores', [100, 95, 87]);

  // Boolean arrays
  span.setAttribute('feature.flags', [true, false, true]);

  // Empty arrays
  span.setAttribute('empty.list', []);

  // ========================================
  // ADVANCED TYPES (Development)
  // ========================================

  // Byte arrays
  const buffer = Buffer.from('binary data');
  span.setAttribute('file.content', buffer);

  // Objects/Maps (if supported)
  span.setAttribute('user.metadata', {
    tier: 'premium',
    region: 'us-east-1'
  });

  // Nested structures (if supported)
  span.setAttribute('request.context', {
    headers: { 'Content-Type': 'application/json' },
    query: { page: 1, limit: 10 }
  });
}
```

---

### Type Validation & Best Practices

#### ✅ Valid Attribute Values
```javascript
// Primitive types
span.setAttribute('string', 'value');           // ✅
span.setAttribute('number', 123);               // ✅
span.setAttribute('float', 123.45);             // ✅
span.setAttribute('boolean', true);             // ✅
span.setAttribute('zero', 0);                   // ✅ Meaningful
span.setAttribute('empty', '');                 // ✅ Meaningful
span.setAttribute('false', false);              // ✅ Meaningful

// Homogeneous arrays
span.setAttribute('strings', ['a', 'b', 'c']);  // ✅
span.setAttribute('numbers', [1, 2, 3]);        // ✅
span.setAttribute('booleans', [true, false]);   // ✅
span.setAttribute('empty', []);                 // ✅ Meaningful
```

#### ❌ Invalid Attribute Values
```javascript
// Mixed type arrays
span.setAttribute('mixed', ['string', 123]);    // ❌ NOT ALLOWED

// Objects (unless Development status supported)
span.setAttribute('object', { key: 'value' });  // ⚠️ Check SDK support

// Functions
span.setAttribute('function', () => {});        // ❌ NOT ALLOWED

// Symbols
span.setAttribute('symbol', Symbol('test'));    // ❌ NOT ALLOWED

// Undefined (unless Development status supported)
span.setAttribute('undefined', undefined);      // ⚠️ Check SDK support
```

---

### Attribute Limits

#### Default Limits
```javascript
// AttributeCountLimit: 128 attributes per span (default)
// AttributeValueLengthLimit: Infinity (default)

// Configure limits
const { NodeTracerProvider } = require('@opentelemetry/sdk-trace-node');

const provider = new NodeTracerProvider({
  // Limit attribute count
  spanLimits: {
    attributeCountLimit: 64,           // Max 64 attributes per span
    attributeValueLengthLimit: 1024,   // Max 1024 chars per string value
  }
});
```

#### What Happens When Limits Are Exceeded?

**Attribute Count Limit:**
```javascript
// If you exceed attributeCountLimit (default: 128)
// Additional attributes are DISCARDED
for (let i = 0; i < 200; i++) {
  span.setAttribute(`attr_${i}`, i);
}
// Only first 128 attributes are kept
```

**Attribute Value Length Limit:**
```javascript
// If string exceeds attributeValueLengthLimit
const longString = 'a'.repeat(2000);
span.setAttribute('long.string', longString);
// String is TRUNCATED to attributeValueLengthLimit

// For arrays of strings, limit applies to EACH element
span.setAttribute('long.strings', [
  'a'.repeat(2000),  // Truncated individually
  'b'.repeat(2000),  // Truncated individually
]);
```

---

### Type Conversion & Serialization

#### OTLP Format
For protocols that don't natively support some types:

```javascript
// Values are JSON-encoded
int64(100)      → 100
float64(1.5)    → 1.5
[]              → []
['a', 'b']      → ["a", "b"]
true            → true
```

#### Null Handling
```javascript
// If exporter doesn't support null, it may be replaced:
null → 0        // for numbers
null → false    // for booleans
null → ''       // for strings
```

---

### Performance Considerations

```javascript
// ✅ Good: Primitive types (fast)
span.setAttribute('user.id', 123);
span.setAttribute('user.name', 'John');

// ⚠️ Caution: Large arrays (slower)
span.setAttribute('large.array', new Array(10000).fill('value'));

// ⚠️ Caution: Deep nested objects (slower, if supported)
span.setAttribute('deep.object', {
  level1: { level2: { level3: { level4: 'value' } } }
});

// ✅ Better: Flatten or summarize
span.setAttribute('object.depth', 4);
span.setAttribute('object.leaf_value', 'value');
```

---

### Quick Reference: Data Types

| Type | Status | Example | Notes |
|------|--------|---------|-------|
| **String** | ✅ Stable | `'hello'` | Max length configurable |
| **Number (int)** | ✅ Stable | `123` | 64-bit signed integer |
| **Number (float)** | ✅ Stable | `123.45` | IEEE 754-1985 double |
| **Boolean** | ✅ Stable | `true` | true or false |
| **String Array** | ✅ Stable | `['a', 'b']` | Homogeneous only |
| **Number Array** | ✅ Stable | `[1, 2, 3]` | Homogeneous only |
| **Boolean Array** | ✅ Stable | `[true, false]` | Homogeneous only |
| **Byte Array** | 🚧 Development | `Buffer.from('data')` | Binary data |
| **AnyValue Array** | 🚧 Development | `[1, 'a', true]` | Mixed types |
| **Map/Object** | 🚧 Development | `{key: 'value'}` | Nested structures |
| **Null/Undefined** | 🚧 Development | `null` | Avoid in arrays |

**Legend:**
- ✅ **Stable** - Production ready, fully supported
- 🚧 **Development** - May not be supported by all SDKs/exporters

### Attribute Naming Conventions

```javascript
// ✅ Good naming patterns
span.setAttribute('http.method', 'POST');           // Semantic convention
span.setAttribute('business.revenue', 1500);        // Business metrics
span.setAttribute('app.version', '1.2.3');          // Application info
span.setAttribute('user.tier', 'premium');          // User context
span.setAttribute('db.query_time_ms', 45);          // Technical metrics

// ❌ Bad naming patterns
span.setAttribute('method', 'POST');                // Too generic
span.setAttribute('revenue', 1500);                 // No namespace
span.setAttribute('v', '1.2.3');                    // Unclear abbreviation
span.setAttribute('userTier', 'premium');           // camelCase (use dots)
```

### Error Handling

```javascript
// ✅ Good: Record exceptions properly
try {
  await processOrder();
} catch (error) {
  span.recordException(error);
  span.setStatus({
    code: SpanStatusCode.ERROR,
    message: error.message
  });
  throw error;
}

// ❌ Bad: Just set status
try {
  await processOrder();
} catch (error) {
  span.setStatus({ code: SpanStatusCode.ERROR });
  // Missing: recordException and error details
}
```

### Performance Tips

- ✅ **Batch span processors** for better performance
  ```javascript
  const { BatchSpanProcessor } = require('@opentelemetry/sdk-trace-base');
  provider.addSpanProcessor(new BatchSpanProcessor(exporter, {
    maxQueueSize: 2048,
    maxExportBatchSize: 512,
    scheduledDelayMillis: 5000,
  }));
  ```

- ✅ **Use sampling** for high-traffic applications
  ```javascript
  const { TraceIdRatioBasedSampler } = require('@opentelemetry/sdk-trace-base');
  const provider = new NodeTracerProvider({
    sampler: new TraceIdRatioBasedSampler(0.1), // 10% sampling
  });
  ```

- ✅ **Limit attribute size**
  ```javascript
  // Bad: Large attribute
  span.setAttribute('response.body', JSON.stringify(largeObject)); // ❌

  // Good: Summary only
  span.setAttribute('response.size_bytes', Buffer.byteLength(body)); // ✅
  ```

---

## 🔗 Resources

### Official Documentation
- **OpenTelemetry Docs:** https://opentelemetry.io/docs/
- **Node.js SDK:** https://opentelemetry.io/docs/languages/js/
- **JavaScript API:** https://opentelemetry.io/docs/languages/js/instrumentation/
- **Semantic Conventions:** https://opentelemetry.io/docs/specs/semconv/
- **Baggage Spec:** https://opentelemetry.io/docs/concepts/signals/baggage/
- **Trace API:** https://opentelemetry.io/docs/specs/otel/trace/api/
- **SDK Specification:** https://opentelemetry.io/docs/specs/otel/trace/sdk/

### NPM Packages
```bash
# Core API
npm install @opentelemetry/api

# Node.js SDK
npm install @opentelemetry/sdk-trace-node
npm install @opentelemetry/sdk-trace-base

# Resources and Semantic Conventions
npm install @opentelemetry/resources
npm install @opentelemetry/semantic-conventions

# Auto-Instrumentation
npm install @opentelemetry/auto-instrumentations-node

# Exporters
npm install @opentelemetry/exporter-trace-otlp-http
npm install @opentelemetry/exporter-jaeger
npm install @opentelemetry/exporter-zipkin
```

### Common Semantic Conventions

#### HTTP Attributes
```javascript
span.setAttribute('http.method', 'POST');
span.setAttribute('http.url', 'https://api.example.com/users');
span.setAttribute('http.status_code', 200);
span.setAttribute('http.request.body.size', 1024);
span.setAttribute('http.response.body.size', 2048);
```

#### Database Attributes
```javascript
span.setAttribute('db.system', 'postgresql');
span.setAttribute('db.name', 'users_db');
span.setAttribute('db.statement', 'SELECT * FROM users WHERE id = $1');
span.setAttribute('db.operation', 'SELECT');
span.setAttribute('db.user', 'app_user');
```

#### Messaging Attributes
```javascript
span.setAttribute('messaging.system', 'kafka');
span.setAttribute('messaging.destination', 'orders-topic');
span.setAttribute('messaging.operation', 'publish');
span.setAttribute('messaging.message_id', 'msg-123');
```

#### RPC Attributes
```javascript
span.setAttribute('rpc.system', 'grpc');
span.setAttribute('rpc.service', 'UserService');
span.setAttribute('rpc.method', 'GetUser');
```

### Quick Reference Card

```javascript
// ============================================
// QUICK REFERENCE: The 4 Methods
// ============================================

// 1. ACTIVE SPAN ENRICHMENT
const span = trace.getActiveSpan();
if (span) {
  span.setAttribute('user.id', userId);
}

// 2. SPAN CREATION
tracer.startActiveSpan('operation', (span) => {
  span.setAttribute('key', 'value');
  span.addEvent('event_name');
  span.setStatus({ code: SpanStatusCode.OK });
  span.end();
});

// 3. BAGGAGE PROPAGATION
const baggage = propagation.createBaggage({
  'tenant.id': { value: tenantId }
});
context.with(propagation.setBaggage(context.active(), baggage), () => {
  // Baggage propagates
});

// 4. SPAN PROCESSOR
class CustomProcessor {
  onStart(span) {
    span.setAttribute('app.version', '1.0.0');
  }
  onEnd() {}
  shutdown() { return Promise.resolve(); }
  forceFlush() { return Promise.resolve(); }
}
provider.addSpanProcessor(new CustomProcessor());
```

### Troubleshooting

#### Spans Not Appearing?
```javascript
// 1. Check if provider is registered
provider.register();

// 2. Check if exporter is configured
const exporter = new OTLPTraceExporter({
  url: 'http://localhost:4318/v1/traces',
});

// 3. Check if spans are being ended
span.end(); // Don't forget this!

// 4. Force flush before exit
await provider.forceFlush();
```

#### Attributes Not Showing?
```javascript
// 1. Check if span exists
const span = trace.getActiveSpan();
console.log('Span exists:', !!span);

// 2. Check attribute limits
// Default: 128 attributes per span
// Increase if needed in SDK config

// 3. Check attribute value types
span.setAttribute('count', 123); // number ✅
span.setAttribute('count', '123'); // string ✅
span.setAttribute('count', { value: 123 }); // object ❌
```

#### Baggage Not Propagating?
```javascript
// 1. Check if propagator is configured
const { W3CTraceContextPropagator } = require('@opentelemetry/core');
const { W3CBaggagePropagator } = require('@opentelemetry/core');
const { CompositePropagator } = require('@opentelemetry/core');

propagation.setGlobalPropagator(
  new CompositePropagator({
    propagators: [
      new W3CTraceContextPropagator(),
      new W3CBaggagePropagator(),
    ],
  })
);

// 2. Check if HTTP instrumentation is enabled
// Baggage propagates via HTTP headers automatically
```

---

## 📝 Summary

### Choose Your Method

| If you need to... | Use this method |
|-------------------|-----------------|
| Add business context to existing HTTP requests | **Active Span Enrichment** |
| Track a custom operation with duration | **Span Creation** |
| Pass tenant ID across microservices | **Baggage Propagation** |
| Add app version to every span | **SpanProcessor** |
| Create nested spans for complex workflows | **Span Creation** |
| Add user context without changing code | **SpanProcessor** + Baggage |
| Filter out health check spans | **SpanProcessor** |

### Key Takeaways

1. **Start Simple:** Begin with Active Span Enrichment for quick wins
2. **Go Deep:** Use Span Creation for detailed instrumentation
3. **Go Wide:** Use Baggage for cross-service context
4. **Go Global:** Use SpanProcessor for consistent attributes

### Next Steps

1. ✅ Choose the method that fits your use case
2. ✅ Start with one method and expand
3. ✅ Follow semantic conventions
4. ✅ Monitor cardinality
5. ✅ Test in development first
6. ✅ Review traces in your backend (Jaeger, Zipkin, SigNoz, etc.)

---

**Version:** 2.0.0
**Last Updated:** December 2024
**Author:** OpenTelemetry Community
**License:** Apache 2.0

