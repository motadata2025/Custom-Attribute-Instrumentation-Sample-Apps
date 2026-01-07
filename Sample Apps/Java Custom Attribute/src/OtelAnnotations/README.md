# OtelAnnotations

Demonstrates **annotation-based** OpenTelemetry instrumentation using `@WithSpan`, `@SpanAttribute`, and `@AddingSpanAttributes`.

## Port

`8081` (configurable via `PORT` environment variable)

## Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/users` | Get all users |
| GET | `/users/{username}` | Get user by username |
| POST | `/users` | Create user |
| PUT | `/users/{username}` | Update user |
| DELETE | `/users/{username}` | Delete user |
| GET | `/swagger` | Swagger UI |

## Instrumentation Approach

Uses OpenTelemetry annotations to declaratively create spans and capture attributes:

```java
// Creates a new span with method parameters as attributes
@WithSpan("otelannotation.user.create")
private void createUser(
    HttpExchange exchange,
    @SpanAttribute("otelannotation.user.username") String username,
    @SpanAttribute("otelannotation.user.email") String email,
    @SpanAttribute("otelannotation.user.age") int age) { }

// Adds attributes to CURRENT span (no new span created)
@AddingSpanAttributes
private void deleteUser(
    HttpExchange exchange,
    @SpanAttribute("otelannotation.user.username") String username) { }
```

## Key Annotations

| Annotation | Purpose |
|------------|---------|
| `@WithSpan("name")` | Creates a new child span for the method |
| `@SpanAttribute("key")` | Captures method parameter as span attribute |
| `@AddingSpanAttributes` | Enriches current span without creating new one |

## Dependencies

- `opentelemetry-instrumentation-annotations:2.11.0`
- `opentelemetry-api:1.45.0`
- `opentelemetry-context:1.45.0`
- `postgresql:42.7.4`

## Build

```bash
javac -cp "$HOME/Downloads/opentelemetry-api-1.45.0.jar:$HOME/Downloads/opentelemetry-context-1.45.0.jar:$HOME/Downloads/opentelemetry-instrumentation-annotations-2.11.0.jar:$HOME/Downloads/postgresql-42.7.4.jar" \
  -d build/otelannotations src/OtelAnnotations/*.java src/OtelAnnotations/**/*.java
```

## Run

```bash
java -javaagent:"$HOME/Downloads/opentelemetry-javaagent.jar" \
     -Dotel.service.name=otel-annotations-demo \
     -jar build/OtelAnnotations-fat.jar
```

## Limitations

- Can only capture attributes available at method entry (parameters)
- Cannot capture values computed inside the method body
- Cannot capture return values easily

## When to Use

- Clean, declarative code preferred
- Capturing method input parameters
- Automatic span creation and context propagation needed

