# Adding Custom Business Attributes to .NET Zero-Code Instrumentation

## Overview

This document provides comprehensive solutions for adding custom business attributes to OpenTelemetry traces at runtime in a .NET application that uses **zero-code (automatic) instrumentation**. The traces are collected by an OTEL Collector with custom logic that sends data to your application backend and UI.

## Problem Statement

You have:
- .NET application with OpenTelemetry zero-code instrumentation already implemented
- OTEL Collector capturing traces with custom logic
- Backend and UI displaying trace data

You need:
- To capture custom business attributes (e.g., user ID, tenant ID, order ID, transaction type) at runtime
- These attributes should be included in the existing trace flow without breaking the current setup

---

## Solution Approaches

There are **three supported approaches** to add custom business attributes while maintaining zero-code instrumentation:

### 1. ✅ Direct Span Enrichment (Recommended for Simple Cases) -- works perfectly. service name: DotNeCore8tCustomAttribute


**Description:** Add custom attributes directly to the current active span using `Activity.Current.SetTag()`.

**When to Use:**
- Simple attribute additions within your business logic
- No additional infrastructure needed
- Minimal code changes

**Implementation Steps:**

#### Step 1: Add the Required Package
Add `System.Diagnostics.DiagnosticSource` to your project (usually already included in .NET Core):

```xml
<PackageReference Include="System.Diagnostics.DiagnosticSource" Version="8.0.0" />
```

#### Step 2: Add Custom Attributes in Your Code

In your controller or service methods, access the current span and add tags:

```csharp
using System.Diagnostics;

[HttpGet("{id}")]
public async Task<ActionResult<Product>> GetProduct(int id)
{
    // Get the current active span created by auto-instrumentation
    var currentActivity = Activity.Current;
    
    // Add custom business attributes
    currentActivity?.SetTag("business.user_id", "user-12345");
    currentActivity?.SetTag("business.tenant_id", "tenant-abc");
    currentActivity?.SetTag("business.product_id", id);
    currentActivity?.SetTag("business.operation_type", "product_retrieval");
    
    var product = await _context.Products.FindAsync(id);
    
    if (product == null)
    {
        currentActivity?.SetTag("business.result", "not_found");
        return NotFound();
    }
    
    currentActivity?.SetTag("business.result", "success");
    currentActivity?.SetTag("business.product_category", product.Category);
    
    return product;
}
```

**Advantages:**
- ✅ Works seamlessly with zero-code instrumentation
- ✅ No configuration changes needed
- ✅ Attributes appear in the same span created by auto-instrumentation
- ✅ Simple and straightforward

**Disadvantages:**
- ❌ Requires code changes in each location where you want to add attributes
- ❌ Manual implementation across multiple endpoints

---

### 2. ✅ Instrumentation Library Enrichment Hooks (Recommended for Framework-Level Attributes)

**Description:** Use built-in enrichment callbacks provided by OpenTelemetry instrumentation libraries to add attributes at the framework level.

**When to Use:**
- Adding attributes to all HTTP requests/responses
- Framework-level context (headers, user info, etc.)
- Centralized attribute management

**Implementation Steps:**

#### Step 1: Install OpenTelemetry Packages

Even with zero-code instrumentation, you can add these packages for enrichment:

```bash
dotnet add package OpenTelemetry.Instrumentation.AspNetCore
dotnet add package OpenTelemetry.Extensions.Hosting
```

#### Step 2: Configure Enrichment in Program.cs

```csharp
using OpenTelemetry.Trace;
using OpenTelemetry.Resources;

var builder = WebApplication.CreateBuilder(args);

// Add services to the container
builder.Services.AddControllers();

// Configure OpenTelemetry enrichment (works alongside zero-code instrumentation)
builder.Services.AddOpenTelemetry()
    .WithTracing(tracerProviderBuilder =>
    {
        tracerProviderBuilder
            .AddAspNetCoreInstrumentation(options =>
            {
                // Enrich spans with custom attributes
                options.Enrich = (activity, eventName, rawObject) =>
                {
                    if (eventName == "OnStartActivity")
                    {
                        if (rawObject is HttpRequest httpRequest)
                        {
                            // Add custom headers as attributes
                            if (httpRequest.Headers.TryGetValue("X-Tenant-Id", out var tenantId))
                            {
                                activity.SetTag("business.tenant_id", tenantId.ToString());
                            }
                            
                            if (httpRequest.Headers.TryGetValue("X-User-Id", out var userId))
                            {
                                activity.SetTag("business.user_id", userId.ToString());
                            }
                            
                            // Add query parameters
                            activity.SetTag("business.query_params", httpRequest.QueryString.ToString());
                        }
                    }
                    
                    if (eventName == "OnStopActivity")
                    {
                        if (rawObject is HttpResponse httpResponse)
                        {
                            // Add response-specific attributes
                            activity.SetTag("business.response_status", httpResponse.StatusCode);
                        }
                    }
                };
            });
    });

var app = builder.Build();
// ... rest of your configuration
```

**Advantages:**
- ✅ Centralized attribute management
- ✅ Applies to all requests automatically
- ✅ Works with zero-code instrumentation
- ✅ Clean separation of concerns

**Disadvantages:**
- ❌ Requires adding OpenTelemetry SDK packages
- ❌ Limited to framework-level context

---

### 3. ✅ Custom ActivitySource with Additional Sources Configuration (Recommended for Business Logic Spans)

**Description:** Create custom spans for specific business operations while maintaining the same trace ID.

**When to Use:**
- Tracking specific business operations
- Need granular control over span lifecycle
- Want to measure duration of business logic

**Implementation Steps:**

#### Step 1: Create an ActivitySource

```csharp
// Create a static ActivitySource (do this once, typically in a separate class)
public static class Telemetry
{
    public static readonly ActivitySource ActivitySource = new ActivitySource("MyApp.Business");
}
```

#### Step 2: Use the ActivitySource in Your Code

```csharp
[HttpPost]
public async Task<ActionResult<Product>> PostProduct(Product product)
{
    // Create a custom span for business logic
    using (var activity = Telemetry.ActivitySource.StartActivity("ProcessProductCreation"))
    {
        // Add custom business attributes
        activity?.SetTag("business.product_name", product.Name);
        activity?.SetTag("business.product_price", product.Price);
        activity?.SetTag("business.operation", "create_product");

        _context.Products.Add(product);
        await _context.SaveChangesAsync();

        activity?.SetTag("business.product_id", product.Id);
        activity?.SetTag("business.status", "success");

        return CreatedAtAction("GetProduct", new { id = product.Id }, product);
    }
}
```

#### Step 3: Register ActivitySource with Zero-Code Instrumentation

Set the environment variable to register your custom ActivitySource:

**Linux/macOS:**
```bash
export OTEL_DOTNET_AUTO_TRACES_ADDITIONAL_SOURCES="MyApp.Business"
```

**Windows:**
```powershell
$env:OTEL_DOTNET_AUTO_TRACES_ADDITIONAL_SOURCES="MyApp.Business"
```

**Docker/Kubernetes:**
```yaml
env:
  - name: OTEL_DOTNET_AUTO_TRACES_ADDITIONAL_SOURCES
    value: "MyApp.Business"
```

**Multiple Sources:**
```bash
export OTEL_DOTNET_AUTO_TRACES_ADDITIONAL_SOURCES="MyApp.Business,MyApp.Integration,MyApp.*"
```

**Advantages:**
- ✅ Full control over span creation
- ✅ Can measure specific business operation duration
- ✅ Creates child spans within the same trace
- ✅ Works perfectly with zero-code instrumentation

**Disadvantages:**
- ❌ Requires environment variable configuration
- ❌ More code compared to direct enrichment

---

## 4. ✅ Using Baggage for Cross-Service Context Propagation

**Description:** Use OpenTelemetry Baggage to propagate business context across service boundaries and add them as span attributes.

**When to Use:**
- Microservices architecture
- Need to propagate context across multiple services
- Enterprise-level tracking (tenant ID, correlation ID, etc.)

**Implementation Steps:**

#### Step 1: Set Baggage Early in the Request Pipeline

```csharp
using System.Diagnostics;

// In a middleware or early in your request processing
public class BusinessContextMiddleware
{
    private readonly RequestDelegate _next;

    public BusinessContextMiddleware(RequestDelegate next)
    {
        _next = next;
    }

    public async Task InvokeAsync(HttpContext context)
    {
        // Extract business context from headers or claims
        if (context.Request.Headers.TryGetValue("X-Tenant-Id", out var tenantId))
        {
            Baggage.SetBaggage("tenant.id", tenantId.ToString());
        }

        if (context.User?.Identity?.Name != null)
        {
            Baggage.SetBaggage("user.id", context.User.Identity.Name);
        }

        // Baggage is automatically propagated to downstream services
        await _next(context);
    }
}

// Register middleware in Program.cs
app.UseMiddleware<BusinessContextMiddleware>();
```

#### Step 2: Retrieve Baggage and Add to Spans

```csharp
[HttpGet("{id}")]
public async Task<ActionResult<Product>> GetProduct(int id)
{
    var currentActivity = Activity.Current;

    // Retrieve baggage and add as span attributes
    var tenantId = Baggage.GetBaggage("tenant.id");
    var userId = Baggage.GetBaggage("user.id");

    if (!string.IsNullOrEmpty(tenantId))
    {
        currentActivity?.SetTag("business.tenant_id", tenantId);
    }

    if (!string.IsNullOrEmpty(userId))
    {
        currentActivity?.SetTag("business.user_id", userId);
    }

    var product = await _context.Products.FindAsync(id);
    return product == null ? NotFound() : Ok(product);
}
```

**Advantages:**
- ✅ Automatic propagation across services
- ✅ Works with distributed tracing
- ✅ Standardized OpenTelemetry approach

**Disadvantages:**
- ❌ Baggage has size limits
- ❌ Propagated in headers (network overhead)

---

## Comparison Matrix

| Approach | Complexity | Scope | Configuration | Best For |
|----------|-----------|-------|---------------|----------|
| **Direct Span Enrichment** | Low | Per-method | None | Simple attribute additions |
| **Instrumentation Hooks** | Medium | Framework-level | SDK packages | HTTP-level attributes |
| **Custom ActivitySource** | Medium | Business logic | Environment variable | Business operation tracking |
| **Baggage** | Medium | Cross-service | Middleware | Distributed systems |

---

## Recommended Implementation Strategy

### For Your Use Case (Zero-Code Instrumentation with Custom Attributes):

**Phase 1: Quick Wins (Immediate Implementation)**
1. Use **Direct Span Enrichment** (Approach 1) in critical business endpoints
2. Add attributes like user ID, tenant ID, transaction type directly in controllers

**Phase 2: Framework-Level Enrichment (Week 1-2)**
1. Implement **Instrumentation Hooks** (Approach 2) for HTTP-level attributes
2. Extract common attributes from headers/claims automatically

**Phase 3: Business Logic Tracking (Week 2-3)**
1. Create **Custom ActivitySources** (Approach 3) for important business operations
2. Configure `OTEL_DOTNET_AUTO_TRACES_ADDITIONAL_SOURCES` environment variable

**Phase 4: Cross-Service Context (If Applicable)**
1. Implement **Baggage** (Approach 4) if you have microservices
2. Propagate tenant/user context across services

---

## Complete Example: ProductsController with Custom Attributes

```csharp
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using System.Diagnostics;
using WebApplicationCore8.Data;
using WebApplicationCore8.Models;

namespace WebApplicationCore8.Controllers
{
    [Route("api/[controller]")]
    [ApiController]
    public class ProductsController : ControllerBase
    {
        private readonly ProductDbContext _context;
        private static readonly ActivitySource ActivitySource = new ActivitySource("WebApplicationCore8.Business");

        public ProductsController(ProductDbContext context)
        {
            _context = context;
        }

        [HttpGet]
        public async Task<ActionResult<IEnumerable<Product>>> GetProducts()
        {
            // Approach 1: Direct enrichment
            Activity.Current?.SetTag("business.operation", "list_products");
            Activity.Current?.SetTag("business.user_id", User?.Identity?.Name ?? "anonymous");

            var products = await _context.Products.ToListAsync();

            Activity.Current?.SetTag("business.result_count", products.Count);

            return products;
        }

        [HttpGet("{id}")]
        public async Task<ActionResult<Product>> GetProduct(int id)
        {
            // Approach 3: Custom span for business logic
            using (var activity = ActivitySource.StartActivity("RetrieveProduct"))
            {
                activity?.SetTag("business.product_id", id);
                activity?.SetTag("business.operation", "get_product");

                var product = await _context.Products.FindAsync(id);

                if (product == null)
                {
                    activity?.SetTag("business.result", "not_found");
                    return NotFound();
                }

                activity?.SetTag("business.result", "success");
                activity?.SetTag("business.product_name", product.Name);
                activity?.SetTag("business.product_price", product.Price);

                return product;
            }
        }

        [HttpPost]
        public async Task<ActionResult<Product>> PostProduct(Product product)
        {
            using (var activity = ActivitySource.StartActivity("CreateProduct"))
            {
                activity?.SetTag("business.operation", "create_product");
                activity?.SetTag("business.product_name", product.Name);
                activity?.SetTag("business.product_price", product.Price);

                _context.Products.Add(product);
                await _context.SaveChangesAsync();

                activity?.SetTag("business.product_id", product.Id);
                activity?.SetTag("business.status", "created");

                return CreatedAtAction("GetProduct", new { id = product.Id }, product);
            }
        }
    }
}
```

---

## Environment Configuration

### Required Environment Variables for Zero-Code Instrumentation

```bash
# Enable .NET automatic instrumentation
export CORECLR_ENABLE_PROFILING=1
export CORECLR_PROFILER={918728DD-259F-4A6A-AC2B-B85E1B658318}
export CORECLR_PROFILER_PATH=/path/to/OpenTelemetry.AutoInstrumentation.Native.so

# OTEL configuration
export OTEL_SERVICE_NAME=your-service-name
export OTEL_EXPORTER_OTLP_ENDPOINT=http://your-collector:4317

# Register custom ActivitySources (for Approach 3)
export OTEL_DOTNET_AUTO_TRACES_ADDITIONAL_SOURCES="WebApplicationCore8.Business,WebApplicationCore8.*"

# Optional: Add resource attributes
export OTEL_RESOURCE_ATTRIBUTES="deployment.environment=production,service.version=1.0.0"
```

---

## Testing Your Implementation

### 1. Verify Attributes in Traces

After implementation, check your OTEL Collector logs or backend UI to verify:

- Custom attributes appear in spans
- Attribute names follow your naming convention (e.g., `business.*`)
- Values are correctly populated
- Trace IDs remain consistent

### 2. Sample Trace Output

Expected trace structure:
```
Trace ID: abc123...
├─ Span: HTTP GET /api/products/5 (auto-instrumentation)
│  ├─ http.method: GET
│  ├─ http.url: /api/products/5
│  ├─ business.user_id: user-12345 (custom)
│  ├─ business.tenant_id: tenant-abc (custom)
│  └─ Child Span: RetrieveProduct (custom ActivitySource)
│     ├─ business.product_id: 5 (custom)
│     ├─ business.operation: get_product (custom)
│     ├─ business.result: success (custom)
│     └─ business.product_name: Widget (custom)
```

---

## Best Practices

1. **Naming Convention**: Use a consistent prefix for business attributes (e.g., `business.*`, `app.*`)
2. **Avoid PII**: Don't add sensitive personal information to spans
3. **Limit Cardinality**: Avoid high-cardinality values (e.g., timestamps, UUIDs) as attribute values
4. **Performance**: Adding attributes has minimal overhead, but avoid excessive attributes per span
5. **Documentation**: Document your custom attributes for team reference

---

## Troubleshooting

### Issue: Custom attributes not appearing in traces

**Solutions:**
1. Verify `Activity.Current` is not null before calling `SetTag()`
2. Check that `OTEL_DOTNET_AUTO_TRACES_ADDITIONAL_SOURCES` is set correctly
3. Ensure your OTEL Collector is configured to forward all attributes
4. Verify the collector isn't filtering out custom attributes

### Issue: Custom ActivitySource spans not created

**Solutions:**
1. Confirm environment variable `OTEL_DOTNET_AUTO_TRACES_ADDITIONAL_SOURCES` includes your source name
2. Restart the application after setting environment variables
3. Check that `ActivitySource` name matches the registered name exactly

---

## References

- [OpenTelemetry .NET Zero-Code Instrumentation](https://opentelemetry.io/docs/zero-code/dotnet/)
- [Custom Traces and Metrics](https://opentelemetry.io/docs/zero-code/dotnet/custom/)
- [.NET Activity API](https://learn.microsoft.com/en-us/dotnet/core/diagnostics/distributed-tracing-instrumentation-walkthroughs)
- [OpenTelemetry .NET Configuration](https://github.com/open-telemetry/opentelemetry-dotnet-instrumentation/blob/main/docs/config.md)
- [OpenTelemetry Semantic Conventions](https://opentelemetry.io/docs/specs/semconv/)

---

## Conclusion

Adding custom business attributes to .NET zero-code instrumentation is fully supported and can be achieved through multiple approaches. The recommended strategy is to:

1. Start with **Direct Span Enrichment** for immediate needs
2. Add **Instrumentation Hooks** for framework-level attributes
3. Use **Custom ActivitySources** for business logic tracking
4. Implement **Baggage** for cross-service context propagation

All approaches work seamlessly with your existing zero-code instrumentation and OTEL Collector setup, ensuring your custom business attributes flow through to your backend and UI without disrupting the current trace collection pipeline.

