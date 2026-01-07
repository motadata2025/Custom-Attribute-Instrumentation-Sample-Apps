# OpenTelemetry Java - Custom Attributes Instrumentation

> **POC Research Document**
> **Last Verified:** December 5, 2025
> **Related Docs:** [Scope 1 (With Code Changes)](./Scope1-Dynamic-Instrumentation-With-Code-Changes.md) | [Scope 2 (Without Code Changes)](./Scope2-Dynamic-Instrumentation-Without-Code-Changes.md)

---

## ✅ Verification Status

All approaches verified against official sources:

| Component | Status | Source |
|-----------|--------|--------|
| `@WithSpan` | ✅ Verified | [GitHub](https://github.com/open-telemetry/opentelemetry-java-instrumentation/blob/main/instrumentation-annotations/src/main/java/io/opentelemetry/instrumentation/annotations/WithSpan.java) |
| `@SpanAttribute` | ✅ Verified | [GitHub](https://github.com/open-telemetry/opentelemetry-java-instrumentation/blob/main/instrumentation-annotations/src/main/java/io/opentelemetry/instrumentation/annotations/SpanAttribute.java) |
| `Span.current()` | ✅ Verified | [GitHub](https://github.com/open-telemetry/opentelemetry-java/blob/main/api/all/src/main/java/io/opentelemetry/api/trace/Span.java) |
| `GlobalOpenTelemetry.getTracer()` | ✅ Verified | [GitHub](https://github.com/open-telemetry/opentelemetry-java/blob/main/api/all/src/main/java/io/opentelemetry/api/GlobalOpenTelemetry.java) |
| `SpanProcessor` | ✅ Verified | [GitHub](https://github.com/open-telemetry/opentelemetry-java/blob/main/sdk/trace/src/main/java/io/opentelemetry/sdk/trace/SpanProcessor.java) |
| `OTEL_INSTRUMENTATION_METHODS_INCLUDE` | ✅ Verified | [Official Docs](https://opentelemetry.io/docs/zero-code/java/agent/annotations/) |

**Java Version:** 21
**Dependencies:** `opentelemetry-instrumentation-annotations:2.22.0` | `opentelemetry-api:1.56.0`

---

## 5 Ways to Add Custom Attributes

| # | Approach | Code Changes | Dynamic | Best For |
|---|----------|--------------|---------|----------|
| 1 | `@SpanAttribute` | ✅ Yes | ❌ No | Method parameters as attributes |
| 2 | `@WithSpan` | ✅ Yes | ❌ No | Custom spans for methods |
| 3 | `Span.current().setAttribute()` | ✅ Yes | ✅ Yes | **Dynamic runtime attributes** |
| 4 | `SpanProcessor` Extension | ❌ No | ⚠️ Config | Global/static attributes |
| 5 | Environment Variables | ❌ No | ❌ No | Resource-level attributes |

---

## 1. `@SpanAttribute` Annotation

```java
@WithSpan("process-order")
public void processOrder(
        @SpanAttribute("order.id") String orderId,
        @SpanAttribute("customer.id") String customerId) {
    // Parameters automatically added as span attributes
}
```

---

## 2. `@WithSpan` Annotation

```java
@WithSpan(value = "payment-processing", kind = SpanKind.CLIENT)
public PaymentResult processPayment(PaymentRequest request) {
    return executePayment(request);
}
```

| Parameter | Default | Description |
|-----------|---------|-------------|
| `value` | `""` | Custom span name |
| `kind` | `INTERNAL` | SpanKind |
| `inheritContext` | `true` | Parent in existing context |

---

## 3. `Span.current().setAttribute()` ⭐ Recommended for Dynamic

```java
public User getUser(String userId) {
    Span currentSpan = Span.current();
    currentSpan.setAttribute("user.id", userId);

    User user = userRepository.findById(userId);
    currentSpan.setAttribute("user.tier", user.getTier());

    return user;
}
```

> **See:** [Scope 1 - Dynamic Instrumentation](./Scope1-Dynamic-Instrumentation-With-Code-Changes.md) for full implementation with `MotadataDynamicInstrumentation` SDK.

---

## 4. Custom `SpanProcessor` Extension

```java
public class CustomAttributeSpanProcessor implements SpanProcessor {
    @Override
    public void onStart(Context parentContext, ReadWriteSpan span) {
        span.setAttribute("environment", System.getenv("ENV"));
        span.setAttribute("service.version", "1.0.0");
    }

    @Override public boolean isStartRequired() { return true; }
    @Override public void onEnd(ReadableSpan span) { }
    @Override public boolean isEndRequired() { return false; }
}
```

> **See:** [Scope 2 - Without Code Changes](./Scope2-Dynamic-Instrumentation-Without-Code-Changes.md) for full extension implementation.

---

## 5. Environment Variables (No Code Changes)

```bash
# Instrument specific methods
export OTEL_INSTRUMENTATION_METHODS_INCLUDE="com.example.MyClass[method1,method2]"

# Resource attributes (applies to all spans)
export OTEL_RESOURCE_ATTRIBUTES="service.name=my-service,env=production"
```

> **See:** [Scope 2 - Without Code Changes](./Scope2-Dynamic-Instrumentation-Without-Code-Changes.md) for detailed configuration.

---

## Which Approach to Use?

```
┌─────────────────────────────────────────────────────────────────┐
│                    DECISION FLOWCHART                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Can you modify client code?                                    │
│       │                                                         │
│       ├── YES ──▶ Need dynamic/runtime attributes?              │
│       │               │                                         │
│       │               ├── YES ──▶ Use Span.current() (Scope 1)  │
│       │               │                                         │
│       │               └── NO ──▶ Use @SpanAttribute/@WithSpan   │
│       │                                                         │
│       └── NO ──▶ Need per-request attributes?                   │
│                       │                                         │
│                       ├── YES ──▶ ❌ NOT POSSIBLE               │
│                       │                                         │
│                       └── NO ──▶ Use SpanProcessor/Env (Scope 2)│
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Annotation vs API: Detailed Comparison

### When to Use Which?

| Aspect | `@SpanAttribute` (Annotation) | `Span.current().setAttribute()` (API) |
|--------|------------------------------|---------------------------------------|
| **When data is known** | At method **entry** only | **Anytime** during execution |
| **Data source** | Method parameters only | Any variable, DB result, computed value |
| **Requires code change** | Minimal (just add annotation) | More (add setAttribute calls) |
| **Dynamic attributes** | ❌ Not possible | ✅ Fully supported |
| **Conditional attributes** | ❌ Not possible | ✅ Add based on if/else logic |
| **Requires Java Agent** | ✅ Yes (to process annotations) | ❌ No (works standalone) |

---

### Data Types Support

| Data Type | `@SpanAttribute` | `Span.current().setAttribute()` |
|-----------|------------------|--------------------------------|
| `String` | ✅ | ✅ |
| `int` / `Integer` | ✅ | ✅ (as `long`) |
| `long` / `Long` | ✅ | ✅ |
| `double` / `Double` | ✅ | ✅ |
| `boolean` / `Boolean` | ✅ | ✅ |
| `String[]` / `List<String>` | ✅ (converted to string) | ✅ (use `AttributeKey.stringArrayKey()`) |
| `long[]` / `List<Long>` | ❌ | ✅ (use `AttributeKey.longArrayKey()`) |
| `double[]` / `List<Double>` | ❌ | ✅ (use `AttributeKey.doubleArrayKey()`) |
| `boolean[]` / `List<Boolean>` | ❌ | ✅ (use `AttributeKey.booleanArrayKey()`) |
| Custom Objects (POJO) | ❌ (uses `.toString()`) | ❌ (must extract fields manually) |
| `null` values | ⚠️ Ignored silently | ⚠️ Ignored silently |
| Enums | ✅ (uses `.toString()`) | ✅ (use `.name()` or `.toString()`) |

---

### Data Source Capabilities

| Data Source | `@SpanAttribute` | `Span.current().setAttribute()` |
|-------------|------------------|--------------------------------|
| Request parameters (path, query) | ✅ | ✅ |
| Request headers | ✅ (if passed as param) | ✅ |
| Request body fields | ❌ (not a param) | ✅ |
| Database query results | ❌ | ✅ |
| External API responses | ❌ | ✅ |
| Computed/derived values | ❌ | ✅ |
| Loop counters / aggregates | ❌ | ✅ |
| Exception details | ❌ | ✅ |
| Environment variables | ❌ | ✅ |
| Configuration values | ❌ | ✅ |
| Time/duration measurements | ❌ | ✅ |

---

### Practical Examples

| Scenario | Annotation Approach | API Approach |
|----------|--------------------| -------------|
| **User ID from request** | `@SpanAttribute("user.id") String userId` | `Span.current().setAttribute("user.id", userId)` |
| **User email from DB** | ❌ Not possible | `Span.current().setAttribute("user.email", user.getEmail())` |
| **Record count after query** | ❌ Not possible | `Span.current().setAttribute("record.count", list.size())` |
| **Error message on exception** | ❌ Not possible | `Span.current().setAttribute("error.message", e.getMessage())` |
| **Processing time** | ❌ Not possible | `Span.current().setAttribute("processing.time.ms", duration)` |
| **Conditional: only if admin** | ❌ Not possible | `if(isAdmin) Span.current().setAttribute("admin.access", true)` |

---

### Code Comparison

**Scenario: Create User with both input & derived data**

```java
// ❌ ANNOTATION ONLY - Cannot capture DB-generated ID
@WithSpan("user.create")
public User createUser(
        @SpanAttribute("user.username") String username,    // ✅ Works - input param
        @SpanAttribute("user.email") String email) {        // ✅ Works - input param

    User created = userRepository.save(new User(username, email));
    // ❌ Cannot add created.getId() - not a parameter!
    return created;
}

// ✅ HYBRID APPROACH - Best of both
@WithSpan("user.create")
public User createUser(
        @SpanAttribute("user.username") String username,    // Input param
        @SpanAttribute("user.email") String email) {        // Input param

    User created = userRepository.save(new User(username, email));

    // Dynamic data - use API
    Span.current().setAttribute("user.id", created.getId());           // DB-generated
    Span.current().setAttribute("user.created_at", created.getCreatedAt().toString());

    return created;
}
```

---

### Decision Matrix

| Your Situation | Use |
|----------------|-----|
| Value is a method parameter | `@SpanAttribute` |
| Value comes from database | `Span.current().setAttribute()` |
| Value is computed inside method | `Span.current().setAttribute()` |
| Value depends on conditional logic | `Span.current().setAttribute()` |
| Want minimal code changes | `@SpanAttribute` |
| Need array of numbers | `Span.current().setAttribute()` |
| Value might change during method | `Span.current().setAttribute()` |
| Value is known before method runs | `@SpanAttribute` |

---

### Dynamic Instrumentation Use Case

For architectures with dynamic business attributes that change per client:

| Attribute Type | Approach |
|----------------|----------|
| Client ID, Request ID | `@SpanAttribute` (input params) |
| Business metrics from DB | `Span.current().setAttribute()` |
| Client-specific custom fields | `Span.current().setAttribute()` (dynamic) |
| Config-driven attributes | `Span.current().setAttribute()` (read from config) |

**Bottom line:** Use **both together** — annotations for inputs, API for everything dynamic.

---

# Annotation reference table — what each does to spans & traces

| Annotation (usage)                                          |                  Creates **new span**?                  |                                        Can start a **new trace**?                                       |                  Adds attributes to **current active span**?                  |                               Adds attributes to **the span it creates**?                               | Notes / typical usage                                                                                                                                                                                                                                                 |
| ----------------------------------------------------------- | :-----------------------------------------------------: | :-----------------------------------------------------------------------------------------------------: | :---------------------------------------------------------------------------: | :-----------------------------------------------------------------------------------------------------: | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `@WithSpan`                                                 | ✅ Always (creates a span for the annotated method/ctor) | ❌ by default — **can** if you set `inheritContext = false` (then span is created with `Context.root()`) | ❌ (it creates a span; it does not add attrs to an already-active parent span) | ✅ Yes — `@SpanAttribute` parameters on the method will be attached to the span that `@WithSpan` creates | Use to instrument a method/ctor with its own span. If async return types are supported by the agent, span may remain open until completion.                                                                                                                           |
| `@WithSpan(inheritContext = false)`                         |                          ✅ Yes                          |                             ✅ Yes — starts a new trace (span has no parent)                             |                                       ❌                                       |                                                  ✅ Yes                                                  | Use when you want a fresh trace (not a child of current context).                                                                                                                                                                                                     |
| `@SpanAttribute` (on a method parameter)                    |            ❌ (itself does not create a span)            |                                                    ❌                                                    |                                      ✅/✅*                                     |                                                   ✅/✅*                                                  | When used together with `@WithSpan`, the parameter value is attached to that created span. When used with `@AddingSpanAttributes`, the parameter value is attached to the current active span. If no annotation-driven instrumentation is active, it's just metadata. |
| `@SpanAttributes` (container / multi attribute)             |                            ❌                            |                                                    ❌                                                    |                                      ✅/✅*                                     |                                                   ✅/✅*                                                  | Container form to declare multiple span attributes; behavior follows `@SpanAttribute` semantics depending on whether a span is being created or attributes are being added.                                                                                           |
| `@AddingSpanAttributes`                                     |            ❌ No (does not create a new span)            |                                                   ❌ No                                                  |      ✅ Yes — adds annotated parameter values to the currently active span     |                                ❌ (it does not create a span to attach to)                               | Use when you want to enrich the **existing** span (for example, framework-created server span) without creating a nested span.                                                                                                                                        |
| (No annotation) — `@SpanAttribute` used alone without agent |                            ❌                            |                                                    ❌                                                    |                                       ❌                                       |                                                    ❌                                                    | If no agent/processor is active, annotations are inert — they do nothing at runtime.                                                                                                                                                                                  |

*@SpanAttribute and @SpanAttributes attach to whichever span is in-scope for the instrumentation action: the new span created by @WithSpan or the current active span when used with @AddingSpanAttributes*

## References

- [OpenTelemetry Java Agent](https://opentelemetry.io/docs/zero-code/java/agent/)
- [Annotations Guide](https://opentelemetry.io/docs/zero-code/java/agent/annotations/)
- [opentelemetry-java-instrumentation (GitHub)](https://github.com/open-telemetry/opentelemetry-java-instrumentation)
- [opentelemetry-java (GitHub)](https://github.com/open-telemetry/opentelemetry-java)
