# Java Custom Attribute Instrumentation POC

Proof of Concept demonstrating custom/business attribute injection strategies for OpenTelemetry in Java applications.

## Overview

This project provides three sample applications showcasing different approaches to inject custom attributes into OpenTelemetry traces:

| Module | Port | Approach | Description |
|--------|------|----------|-------------|
| `OtelAnnotations` | 8081 | Annotation-Based | Uses `@WithSpan`, `@SpanAttribute` annotations |
| `OtelApi` | 8080 | API-Based (Recommended) | Uses `Span.current().setAttribute()` via utility class |
| `OtelApiTracerProvider` | 8082 | Manual Tracer | Full control with manual span lifecycle management |

## Prerequisites

- Java 21+
- OpenTelemetry Java Agent
- PostgreSQL (optional, for database features)

### Required JARs

Download and place in `~/Downloads/`:
- `opentelemetry-api-1.45.0.jar`
- `opentelemetry-context-1.45.0.jar`
- `opentelemetry-instrumentation-annotations-2.11.0.jar`
- `postgresql-42.7.4.jar`
- `opentelemetry-javaagent.jar` (for runtime)

## Build

Build fat JARs for each module:

```bash
# OtelAnnotations (Annotation-based)
rm -rf build/otelannotations && mkdir -p build/otelannotations && \
cd build/otelannotations && \
jar xf $HOME/Downloads/opentelemetry-api-1.45.0.jar && \
jar xf $HOME/Downloads/opentelemetry-context-1.45.0.jar && \
jar xf $HOME/Downloads/opentelemetry-instrumentation-annotations-2.11.0.jar && \
jar xf $HOME/Downloads/postgresql-42.7.4.jar && \
rm -rf META-INF && cd ../.. && \
javac -cp "$HOME/Downloads/opentelemetry-api-1.45.0.jar:$HOME/Downloads/opentelemetry-context-1.45.0.jar:$HOME/Downloads/opentelemetry-instrumentation-annotations-2.11.0.jar:$HOME/Downloads/postgresql-42.7.4.jar" \
  -d build/otelannotations src/OtelAnnotations/*.java src/OtelAnnotations/**/*.java && \
jar cfm build/OtelAnnotations-fat.jar manifest-otelannotations.txt -C build/otelannotations .

# OtelApi (API-based - Recommended)
rm -rf build/otelapi && mkdir -p build/otelapi && \
cd build/otelapi && \
jar xf $HOME/Downloads/opentelemetry-api-1.45.0.jar && \
jar xf $HOME/Downloads/opentelemetry-context-1.45.0.jar && \
jar xf $HOME/Downloads/postgresql-42.7.4.jar && \
rm -rf META-INF && cd ../.. && \
javac -cp "$HOME/Downloads/opentelemetry-api-1.45.0.jar:$HOME/Downloads/opentelemetry-context-1.45.0.jar:$HOME/Downloads/postgresql-42.7.4.jar" \
  -d build/otelapi src/OtelApi/*.java src/OtelApi/**/*.java && \
jar cfm build/OtelApi-fat.jar manifest-otelapi.txt -C build/otelapi .

# OtelApiTracerProvider (Manual spans)
rm -rf build/otelapitracerprovider && mkdir -p build/otelapitracerprovider && \
cd build/otelapitracerprovider && \
jar xf $HOME/Downloads/opentelemetry-api-1.45.0.jar && \
jar xf $HOME/Downloads/opentelemetry-context-1.45.0.jar && \
jar xf $HOME/Downloads/postgresql-42.7.4.jar && \
rm -rf META-INF && cd ../.. && \
javac -cp "$HOME/Downloads/opentelemetry-api-1.45.0.jar:$HOME/Downloads/opentelemetry-context-1.45.0.jar:$HOME/Downloads/postgresql-42.7.4.jar" \
  -d build/otelapitracerprovider src/OtelApiTracerProvider/*.java src/OtelApiTracerProvider/**/*.java && \
jar cfm build/OtelApiTracerProvider-fat.jar manifest-otelapitracerprovider.txt -C build/otelapitracerprovider .
```

## Run

Run with OpenTelemetry Java Agent:

```bash
# OtelApi (port 8080)
java -javaagent:"$HOME/Downloads/opentelemetry-javaagent.jar" \
     -Dotel.service.name=otel-api-demo \
     -jar build/OtelApi-fat.jar

# OtelAnnotations (port 8081)
java -javaagent:"$HOME/Downloads/opentelemetry-javaagent.jar" \
     -Dotel.service.name=otel-annotations-demo \
     -jar build/OtelAnnotations-fat.jar

# OtelApiTracerProvider (port 8082)
java -javaagent:"$HOME/Downloads/opentelemetry-javaagent.jar" \
     -Dotel.service.name=otel-tracer-provider-demo \
     -jar build/OtelApiTracerProvider-fat.jar
```

Access Swagger UI at `http://localhost:<PORT>/swagger`

## Project Structure

```
├── src/
│   ├── OtelAnnotations/       # Annotation-based instrumentation demo
│   ├── OtelApi/               # API-based instrumentation demo (recommended)
│   │   └── util/MotadataDynamicInstrumentation.java  # Utility class
│   └── OtelApiTracerProvider/ # Manual tracer/span demo
├── build/                     # Compiled fat JARs
├── docs/                      # Additional documentation
├── Testing Snapshots/         # Verification screenshots
└── Java_Custom_Attribute_POC.md  # Detailed POC documentation
```

## Quick Reference

### Annotation-Based
```java
@WithSpan("process-user")
public void processUser(@SpanAttribute("apm.user.id") String userId) { }
```

### API-Based (Recommended)
```java
import OtelApi.util.MotadataDynamicInstrumentation;

MotadataDynamicInstrumentation.set("user.id", userId);  // Auto-prefixed with "apm."
MotadataDynamicInstrumentation.setStringList("items", itemList);
```

### Manual Tracer
```java
Tracer tracer = GlobalOpenTelemetry.getTracer("my.instrumentation");
Span span = tracer.spanBuilder("my-span").startSpan();
try (Scope scope = span.makeCurrent()) {
    span.setAttribute("apm.key", "value");
} finally {
    span.end();
}
```

## Testing Snapshots

See [Testing Snapshots](Testing%20Snapshots/) for verification screenshots.

