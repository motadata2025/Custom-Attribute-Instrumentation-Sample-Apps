# OtelApiTracerProvider

Demonstrates **manual tracer and span creation** using `GlobalOpenTelemetry.getTracer()` with full lifecycle control.

## Port

`8082` (configurable via `PORT` environment variable)

## Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/orders` | Create order (demonstrates root + child spans) |
| GET | `/orders` | Get all orders |
| GET | `/orders/{orderId}` | Get order by ID |
| GET | `/swagger` | Swagger UI |

## Instrumentation Approach

Uses manual tracer and span creation for complete control:

```java
// Get tracer instance
private static final Tracer tracer = 
    GlobalOpenTelemetry.get().getTracer("com.example.order-service", "1.0.0");

// Create ROOT span (new trace)
Span rootSpan = tracer.spanBuilder("order.process")
    .setSpanKind(SpanKind.SERVER)
    .setNoParent()  // Creates new trace
    .startSpan();

try (Scope scope = rootSpan.makeCurrent()) {
    rootSpan.setAttribute("order.id", orderId);
    rootSpan.setAttribute("order.total", total);
    
    // Child spans auto-parent to current span
    validateOrder(orderId, total);
    
} catch (Exception e) {
    rootSpan.recordException(e);
    rootSpan.setStatus(StatusCode.ERROR, e.getMessage());
    throw e;
} finally {
    rootSpan.end();  // CRITICAL: Always end the span!
}
```

## Span Hierarchy Demo

The `POST /orders` endpoint creates this span hierarchy:

```
order.process (ROOT - SpanKind.SERVER)
├── order.validate (CHILD - SpanKind.INTERNAL)
├── order.payment (CHILD - SpanKind.CLIENT)
├── order.shipment (CHILD - SpanKind.CLIENT)
└── order.save_to_db (CHILD - SpanKind.CLIENT)
```

## SpanKind Reference

| SpanKind | Use Case |
|----------|----------|
| `INTERNAL` | Internal method calls (default) |
| `SERVER` | Server-side request handling |
| `CLIENT` | Client-side external calls |
| `PRODUCER` | Message producer |
| `CONSUMER` | Message consumer |

## Key Methods

| Method | Purpose |
|--------|---------|
| `spanBuilder("name")` | Create span builder |
| `.setNoParent()` | Create root span (new trace) |
| `.setSpanKind(kind)` | Set span type |
| `.startSpan()` | Start the span |
| `span.makeCurrent()` | Make span active in context |
| `span.setAttribute(k, v)` | Add custom attribute |
| `span.addEvent("name")` | Add timestamped event |
| `span.recordException(e)` | Record exception details |
| `span.setStatus(code)` | Set final status |
| `span.end()` | End span (REQUIRED) |

## Dependencies

- `opentelemetry-api:1.45.0`
- `opentelemetry-context:1.45.0`
- `postgresql:42.7.4`

## Build

```bash
javac -cp "$HOME/Downloads/opentelemetry-api-1.45.0.jar:$HOME/Downloads/opentelemetry-context-1.45.0.jar:$HOME/Downloads/postgresql-42.7.4.jar" \
  -d build/otelapitracerprovider src/OtelApiTracerProvider/*.java src/OtelApiTracerProvider/**/*.java
```

## Run

```bash
java -javaagent:"$HOME/Downloads/opentelemetry-javaagent.jar" \
     -Dotel.service.name=otel-tracer-provider-demo \
     -jar build/OtelApiTracerProvider-fat.jar
```

## Test

```bash
curl -X POST http://localhost:8082/orders \
     -H 'Content-Type: application/json' \
     -d '{"orderId":"ORD-123","total":99.99,"customerId":"CUST-456"}'
```

## Advantages

- **Complete control**: Create root spans, custom hierarchies
- **Precise lifecycle**: Exact control over span start/end
- **Async support**: Manual context propagation across threads

## Limitations

- **Verbose**: Requires significant boilerplate
- **Complex**: Requires careful try-finally blocks
- **Error-prone**: Forgetting `span.end()` causes memory leaks

## When to Use

- Creating new root traces (separate from auto-instrumentation)
- Complex parent-child span relationships
- Asynchronous context propagation
- Full control over span lifecycle needed

