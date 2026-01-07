# OtelApi

Demonstrates **API-based** OpenTelemetry instrumentation using `Span.current().setAttribute()` via the `MotadataDynamicInstrumentation` utility class. **This is the recommended approach.**

## Port

`8080` (configurable via `PORT` environment variable)

## Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/users` | Get all users |
| GET | `/users/{username}` | Get user by username |
| POST | `/users` | Create user |
| PUT | `/users/{username}` | Update user |
| DELETE | `/users/{username}` | Delete user |
| GET | `/test-instrumentation` | Test all supported data types |
| GET | `/swagger` | Swagger UI |

## Instrumentation Approach

Uses the `MotadataDynamicInstrumentation` utility to add attributes at any point in code execution:

```java
import OtelApi.util.MotadataDynamicInstrumentation;

// Add attributes dynamically - auto-prefixed with "apm."
MotadataDynamicInstrumentation.set("user.username", user.getUsername());
MotadataDynamicInstrumentation.set("user.email", user.getEmail());
MotadataDynamicInstrumentation.set("user.age", user.getAge());           // int → long
MotadataDynamicInstrumentation.set("user.salary", user.getSalary());     // double
MotadataDynamicInstrumentation.set("user.active", user.isActive());      // boolean
MotadataDynamicInstrumentation.setStringList("user.tags", user.getTags()); // List<String>
```

## MotadataDynamicInstrumentation Utility

Located at `util/MotadataDynamicInstrumentation.java`. Features:

| Feature | Description |
|---------|-------------|
| Auto-prefixing | Keys automatically prefixed with `apm.` |
| Null-safe | Null keys/values silently ignored |
| Type widening | `int` → `long`, `float` → `double` |
| Exception-safe | All errors suppressed, never crashes app |
| List support | `setStringList`, `setLongList`, `setDoubleList`, `setBooleanList`, `setIntegerList` |

### Supported Types

| Method | Java Types |
|--------|------------|
| `set(key, value)` | `String`, `Boolean`, `Double`, `Integer`, `Long` |
| `setStringList(key, list)` | `List<String>` |
| `setBooleanList(key, list)` | `List<Boolean>` |
| `setDoubleList(key, list)` | `List<Double>` |
| `setIntegerList(key, list)` | `List<Integer>` (converted to `List<Long>`) |
| `setLongList(key, list)` | `List<Long>` |

## Dependencies

- `opentelemetry-api:1.45.0`
- `opentelemetry-context:1.45.0`
- `postgresql:42.7.4`

## Build

```bash
javac -cp "$HOME/Downloads/opentelemetry-api-1.45.0.jar:$HOME/Downloads/opentelemetry-context-1.45.0.jar:$HOME/Downloads/postgresql-42.7.4.jar" \
  -d build/otelapi src/OtelApi/*.java src/OtelApi/**/*.java
```

## Run

```bash
java -javaagent:"$HOME/Downloads/opentelemetry-javaagent.jar" \
     -Dotel.service.name=otel-api-demo \
     -jar build/OtelApi-fat.jar
```

## Test All Data Types

```bash
curl http://localhost:8080/test-instrumentation
```

This endpoint tests all supported primitive, boxed, and list types.

## Advantages

- **Dynamic**: Add attributes at any point (start, middle, end of method)
- **Flexible**: Capture local variables, database results, calculated values
- **Span-agnostic**: Works regardless of how span was created

## Limitations

- Requires an active span (auto-instrumented or manually created)
- Attributes ignored in non-instrumented contexts

## When to Use

- **Recommended for most use cases**
- Dynamic runtime attribute injection needed
- Capturing computed values, database results, or local variables
- Minimal code changes preferred

