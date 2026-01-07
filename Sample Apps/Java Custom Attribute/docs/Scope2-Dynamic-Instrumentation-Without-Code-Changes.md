# Scope 2: Dynamic Instrumentation WITHOUT Client Code Changes

> **Document Type:** Implementation Guide  
> **Status:** POC Research  
> **Last Updated:** December 5, 2025  
> **Recommendation:** ⚠️ **LIMITED APPROACH - Use Only When Scope 1 Not Possible**

---

## Overview

This document covers implementing **dynamic custom attributes** when client code modifications are **NOT permitted**. This approach has significant limitations but provides options for injecting context without touching application code.

---

## ⚠️ Critical Limitation

```
┌────────────────────────────────────────────────────────────────────────────┐
│                              IMPORTANT                                      │
├────────────────────────────────────────────────────────────────────────────┤
│ WITHOUT client code changes, you CANNOT access runtime business data:      │
│                                                                             │
│   ❌ Order IDs (exist only in application memory)                          │
│   ❌ Customer information (exist only in application variables)            │
│   ❌ Transaction amounts (exist only at runtime)                           │
│   ❌ Request-specific business context                                     │
│                                                                             │
│ The OpenTelemetry agent cannot "magically" know which variables            │
│ contain business-relevant data.                                            │
└────────────────────────────────────────────────────────────────────────────┘
```

---

## What IS Possible Without Code Changes

| Attribute Type | Possible? | Method |
|----------------|-----------|--------|
| Static deployment attributes | ✅ Yes | Environment Variables |
| Configuration-driven attributes | ✅ Yes | Custom SpanProcessor + Config File |
| Client/Tenant identifiers | ✅ Yes | Environment Variables |
| Region/Environment info | ✅ Yes | Resource Attributes |
| Upstream context (headers) | ⚠️ Partial | Baggage Propagation |
| Runtime business data | ❌ No | Requires code changes |

---

## Architecture Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                              │
│   ┌─────────────────┐     ┌─────────────────────────────────────────────┐   │
│   │ Config File     │     │ JAVA APPLICATION                            │   │
│   │ (attributes.json│────▶│  ┌─────────────────────────────────────┐    │   │
│   │  - refreshable) │     │  │ Custom SpanProcessor Extension      │    │   │
│   └─────────────────┘     │  │ (Reads config, injects attributes)  │    │   │
│                           │  └──────────────────┬──────────────────┘    │   │
│   ┌─────────────────┐     │                     │                       │   │
│   │ Environment     │────▶│  Resource Attributes│                       │   │
│   │ Variables       │     │  (OTEL_RESOURCE_ATTRIBUTES)                 │   │
│   └─────────────────┘     └─────────────────────┼───────────────────────┘   │
│                                                  │                           │
└──────────────────────────────────────────────────┼───────────────────────────┘
                                                   ▼
                           ┌──────────────┐     ┌────────────┐     ┌──────────┐
                           │ OTEL         │────▶│ Cache      │────▶│ Your     │
                           │ Collector    │     │ File       │     │ Backend  │
                           └──────────────┘     └────────────┘     └──────────┘
```

---

## Implementation Options

### Option A: Resource Attributes via Environment Variables (Simplest)

**Best for:** Static per-deployment attributes (client name, region, environment)

```bash
# Set at deployment time - NO code changes needed
export OTEL_RESOURCE_ATTRIBUTES="client.name=AcmeCorp,business.unit=retail,deployment.region=us-east-1,env=production"

# Start application with agent
java -javaagent:opentelemetry-javaagent.jar -jar client-app.jar
```

**Or via Java system properties:**
```bash
java -javaagent:opentelemetry-javaagent.jar \
     -Dotel.resource.attributes="client.name=AcmeCorp,business.unit=retail" \
     -jar client-app.jar
```

#### Limitation
⚠️ These are **resource-level** attributes, applied to ALL spans. Cannot be dynamic per-request.

---

### Option B: Custom SpanProcessor Extension (Advanced)

**Best for:** Config-driven attributes that can be updated without restart

#### Step 1: Create Extension Project

**pom.xml:**
```xml
<?xml version="1.0" encoding="UTF-8"?>
<project>
    <modelVersion>4.0.0</modelVersion>
    <groupId>com.yourcompany</groupId>
    <artifactId>otel-dynamic-attributes-extension</artifactId>
    <version>1.0.0</version>
    
    <dependencies>
        <dependency>
            <groupId>io.opentelemetry</groupId>
            <artifactId>opentelemetry-sdk</artifactId>
            <version>1.56.0</version>
            <scope>provided</scope>
        </dependency>
        <dependency>
            <groupId>io.opentelemetry.javaagent</groupId>
            <artifactId>opentelemetry-javaagent-extension-api</artifactId>
            <version>2.22.0</version>
            <scope>provided</scope>
        </dependency>
        <dependency>
            <groupId>com.google.code.gson</groupId>
            <artifactId>gson</artifactId>
            <version>2.10.1</version>
        </dependency>
    </dependencies>
</project>
```

#### Step 2: Implement SpanProcessor
```java
package com.yourcompany.otel.extension;

import io.opentelemetry.context.Context;
import io.opentelemetry.sdk.trace.ReadWriteSpan;
import io.opentelemetry.sdk.trace.ReadableSpan;
import io.opentelemetry.sdk.trace.SpanProcessor;
import com.google.gson.Gson;
import com.google.gson.reflect.TypeToken;

import java.io.FileReader;
import java.lang.reflect.Type;
import java.util.Map;
import java.util.concurrent.*;

public class DynamicConfigSpanProcessor implements SpanProcessor {

    private static final String CONFIG_PATH = System.getenv()
        .getOrDefault("DYNAMIC_ATTRIBUTES_CONFIG", "/etc/otel/attributes.json");
    
    private volatile Map<String, String> dynamicAttributes = new ConcurrentHashMap<>();
    private final ScheduledExecutorService scheduler = Executors.newSingleThreadScheduledExecutor();
    private final Gson gson = new Gson();

    public DynamicConfigSpanProcessor() {
        loadConfig();
        // Reload config every 30 seconds for dynamic updates
        scheduler.scheduleAtFixedRate(this::loadConfig, 30, 30, TimeUnit.SECONDS);
    }

    private void loadConfig() {
        try (FileReader reader = new FileReader(CONFIG_PATH)) {
            Type type = new TypeToken<Map<String, String>>(){}.getType();
            Map<String, String> loaded = gson.fromJson(reader, type);
            if (loaded != null) {
                this.dynamicAttributes = new ConcurrentHashMap<>(loaded);
            }
        } catch (Exception e) {
            // Log error but don't crash - keep existing config
            System.err.println("Failed to load dynamic attributes config: " + e.getMessage());
        }
    }

    @Override
    public void onStart(Context parentContext, ReadWriteSpan span) {
        // Inject all configured attributes into every span
        for (Map.Entry<String, String> attr : dynamicAttributes.entrySet()) {
            span.setAttribute("config." + attr.getKey(), attr.getValue());
        }

        // Also inject environment-based attributes
        String clientId = System.getenv("CLIENT_ID");
        if (clientId != null) {
            span.setAttribute("client.id", clientId);
        }

        String businessUnit = System.getenv("BUSINESS_UNIT");
        if (businessUnit != null) {
            span.setAttribute("business.unit", businessUnit);
        }
    }

    @Override
    public boolean isStartRequired() {
        return true;
    }

    @Override
    public void onEnd(ReadableSpan span) {
        // No action needed on span end
    }

    @Override
    public boolean isEndRequired() {
        return false;
    }
}
```

#### Step 3: Create SPI Registration

Create file: `src/main/resources/META-INF/services/io.opentelemetry.javaagent.extension.AgentExtension`
```
com.yourcompany.otel.extension.DynamicAttributesExtension
```

**Extension class:**
```java
package com.yourcompany.otel.extension;

import io.opentelemetry.javaagent.extension.AgentExtension;
import io.opentelemetry.sdk.autoconfigure.spi.AutoConfigurationCustomizer;

public class DynamicAttributesExtension implements AgentExtension {

    @Override
    public String extensionName() {
        return "dynamic-attributes";
    }

    @Override
    public void extend(AutoConfigurationCustomizer autoConfiguration) {
        autoConfiguration.addTracerProviderCustomizer((builder, config) -> {
            return builder.addSpanProcessor(new DynamicConfigSpanProcessor());
        });
    }
}
```

#### Step 4: Build and Deploy Extension

```bash
# Build the extension JAR
mvn clean package

# Deploy with the agent
java -javaagent:opentelemetry-javaagent.jar \
     -Dotel.javaagent.extensions=/path/to/otel-dynamic-attributes-extension-1.0.0.jar \
     -jar client-app.jar
```

#### Step 5: Create Config File

**/etc/otel/attributes.json:**
```json
{
  "client.name": "AcmeCorp",
  "business.unit": "retail",
  "deployment.region": "us-east-1",
  "environment": "production",
  "cost.center": "CC-12345"
}
```

**To update attributes dynamically:** Simply edit the JSON file. The SpanProcessor reloads every 30 seconds.

---

### Option C: Baggage Propagation (For Upstream Context)

**Best for:** Attributes that come from upstream services via HTTP headers

```bash
# Enable baggage propagation
export OTEL_PROPAGATORS="tracecontext,baggage"
```

**Upstream service sets baggage:**
```java
// In upstream service
Baggage.current().toBuilder()
    .put("client.id", "ACME-123")
    .put("request.priority", "high")
    .build()
    .makeCurrent();
```

**Downstream receives via headers:**
```
baggage: client.id=ACME-123,request.priority=high
```

⚠️ **Limitation:** Requires upstream service to set baggage. Not useful for standalone applications.

---

## Comparison of Options

| Option | Dynamic Updates | Per-Request | Setup Effort | Use Case |
|--------|-----------------|-------------|--------------|----------|
| **A: Env Variables** | ❌ Restart needed | ❌ No | ✅ Very Low | Static deployment info |
| **B: SpanProcessor** | ✅ Config reload | ❌ No | ⚠️ Medium | Config-driven attributes |
| **C: Baggage** | ✅ Yes | ✅ Yes | ⚠️ Medium | Upstream context only |

---

## What You CANNOT Do Without Code Changes

| Requirement | Possible? | Reason |
|-------------|-----------|--------|
| Capture Order ID | ❌ No | Exists only in app memory |
| Capture Customer Tier | ❌ No | Runtime business logic |
| Capture Transaction Amount | ❌ No | Variable in application |
| Capture User Session Data | ❌ No | Application-specific |
| Capture Request Body Fields | ❌ No | Requires parsing logic |

---

## Recommended Hybrid Approach

For maximum coverage without code changes, combine options:

```bash
# 1. Resource attributes for static info
export OTEL_RESOURCE_ATTRIBUTES="client.name=AcmeCorp,region=us-east"

# 2. Point to config file for dynamic attributes
export DYNAMIC_ATTRIBUTES_CONFIG="/etc/otel/attributes.json"

# 3. Enable baggage for upstream context
export OTEL_PROPAGATORS="tracecontext,baggage"

# 4. Run with extension
java -javaagent:opentelemetry-javaagent.jar \
     -Dotel.javaagent.extensions=/path/to/extension.jar \
     -jar client-app.jar
```

---

## References

- [SpanProcessor Interface - GitHub](https://github.com/open-telemetry/opentelemetry-java/blob/main/sdk/trace/src/main/java/io/opentelemetry/sdk/trace/SpanProcessor.java)
- [Java Agent Extensions](https://opentelemetry.io/docs/zero-code/java/agent/extensions/)
- [Resource Attributes](https://opentelemetry.io/docs/languages/java/configuration/#resources)
- [Baggage Propagation](https://opentelemetry.io/docs/concepts/signals/baggage/)

---

## Summary

| Aspect | Details |
|--------|---------|
| **Best Option** | Custom SpanProcessor Extension + Environment Variables |
| **Flexibility** | ⚠️ Limited to config-driven attributes |
| **Runtime Changes** | ✅ Via config file reload (30s interval) |
| **Business Data Access** | ❌ Cannot access application variables |
| **Implementation Effort** | Medium - requires extension JAR |
| **Recommended For** | Only when Scope 1 is absolutely not possible |

---

## Final Recommendation

> **If you need true business-context attributes (Order ID, Customer data, Transaction details), Scope 1 is the ONLY viable option.**
>
> Scope 2 is suitable only for:
> - Deployment-level metadata (client name, region, environment)
> - Configuration-driven static attributes
> - Context propagated from upstream services

