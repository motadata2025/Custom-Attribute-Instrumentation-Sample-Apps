# Custom/Business Specific Attribute Injection Strategies for .NET Runtime

> **Document Type:** Proof of Concept (POC)
> **Project:** .NET Custom Attribute
> **Last Verified:** December 17, 2025
> **Status:** Verified & Implemented
> **Testing Environment .NET Version:** 8 and 9
---

## 1. Overview

This document details the findings and implementation strategies for injecting custom business attributes into OpenTelemetry traces in a .NET runtime environment. Across all approaches evaluated below, traces were generated correctly, custom/business attributes were appended to the intended spans, multiple data types were supported (string, numeric, boolean, arrays/lists), and all attributes were visible in the UI.

Testing was performed on dummy .NET Core 8 and .NET Core 9 web applications using OpenTelemetry zero-code auto-instrumentation.

---

## 2. Approach 1: Custom ActivitySource Instrumentation (New Child Span Creation)

This approach creates explicit custom child spans inside an already existing trace context created by zero-code auto-instrumentation (for example, ASP.NET Core HTTP spans).

### 2.1 Description
*   A custom `ActivitySource` is defined at the application level.
*   OpenTelemetry auto-instrumentation is configured to listen to this source.
*   Business logic explicitly starts a new activity (span) as a child of the auto-generated HTTP span. Custom attributes are added to this new span.
*   **Trace Context:** The new span automatically shares the same `TraceId` as the parent span, ensuring it appears within the same trace in the observability backend.

**Strengths:**
*   Clear separation of business logic spans from framework spans.
*   Allows for granular tracking of specific business operations.

**Limitations:**
*   Requires additional setup such as `ActivitySource` registration and environment configuration.

### 2.2 Code Reference

```csharp
using System.Diagnostics;

// Define the ActivitySource
static readonly ActivitySource AppActivitySource = new ActivitySource("motadata.custom.instrumentation");

// Start a new activity
using (var activity = AppActivitySource.StartActivity("BusinessOperation"))
{
    activity?.SetTag("apm.operation", "create_order");
    activity?.SetTag("apm.order_id", orderId);
    
    // business logic
}
```

---

## 3. Approach 2: API-Based Direct Span Enrichment (Recommended Approach)

This approach enriches the already active span created by OpenTelemetry zero-code instrumentation using the built-in .NET `Activity.Current` API. To simplify usage and ensure type safety, we implemented a utility class `MotadataDynamicInstrumentation`.

### 3.1 Description
*   OpenTelemetry auto-instrumentation creates the HTTP server span.
*   `Activity.Current` references this active span.
*   Business attributes are added directly using `SetTag()`.

**Strengths:**
*   **Simple:** No need to create new spans if only attribute enrichment is required.
*   **Dynamic:** Attributes can be added at any point (start, middle, or end of method).
*   **Flexible:** Can capture local variables, database results, and calculated values.

**Limitations:**
*   Requires an active span. If the execution path is not auto-instrumented, `Activity.Current` may be null.

### 3.2 Client-Side Implementation
Clients should include the `MotadataDynamicInstrumentation` utility class in their project to handle null-safety and naming conventions.

**Step 1: Add the Utility Class**
(See `WebApplicationCore8/Util/MotadataDynamicInstrumentation.cs` in the project for full source).

**Step 2: Instrument Code**
```csharp
using WebApplicationCore8.Util;

public async Task<ActionResult<Product>> GetProduct(int id)
{
    // Add custom business attributes
    MotadataDynamicInstrumentation.Set("apm.operation", "get_product");
    MotadataDynamicInstrumentation.Set("apm.product_id", id);
    MotadataDynamicInstrumentation.Set("apm.user_id", User?.Identity?.Name ?? "anonymous");

    var product = await _context.Products.FindAsync(id);

    if (product == null)
    {
        MotadataDynamicInstrumentation.Set("apm.result", "not_found");
        return NotFound();
    }

    // Add product-specific attributes
    MotadataDynamicInstrumentation.Set("apm.product_name", product.Name);
    MotadataDynamicInstrumentation.Set("apm.product_price", product.Price);
    
    // Example: Adding List/Array attributes
    string[] categories = new[] { "Electronics", "Gadgets" };
    int[] stockCounts = new[] { 50, 20, 10 };
    
    MotadataDynamicInstrumentation.SetStringArray("apm.product.categories", categories);
    MotadataDynamicInstrumentation.SetIntArray("apm.product.stock_history", stockCounts);

    return product;
}
```

### 3.3 MotadataDynamicInstrumentation Utility Reference

This section explains the internal behavior of the `MotadataDynamicInstrumentation` utility class used in the API-Based instrumentation method.

#### What is happening inside `MotadataDynamicInstrumentation`?

The `MotadataDynamicInstrumentation` class acts as a **safe wrapper** around the standard .NET `Activity.Current.SetTag()` API. Its primary goal is to prevent runtime exceptions and enforce consistency without cluttering business logic.

#### Key Internal Mechanisms:

1.  **Automatic Prefixing:**
    *   Every attribute key passed to the utility is checked.
    *   If it doesn't already start with `apm.`, the prefix is automatically prepended.
    *   *Example:* `Set("user.id", ...)` becomes `apm.user.id` in the trace.

2.  **Null Safety:**
    *   The class explicitly checks for `null` keys and values.
    *   If a key or value is `null`, or if `Activity.Current` is null, the operation is **silently ignored**. No exceptions are thrown, ensuring that telemetry code never crashes the application.

3.  **Type Handling:**
    *   Supports `bool`, `double`, `float`, `int`, `long`, `string` and their array counterparts.
    *   Arrays are cleaned of null values (for strings) before being added.

4.  **Error Suppression:**
    *   All internal calls are wrapped in `try-catch` blocks that swallow exceptions. This guarantees that even if the API fails, the application flow remains uninterrupted.

#### Minimal Code Reference

```csharp
// Simplified view of what happens internally
public static void Set(string key, string value)
{
    try
    {
        if (string.IsNullOrEmpty(key) || value == null || Activity.Current == null)
            return;

        string prefixed = key.StartsWith("apm.") ? key : "apm." + key;
        Activity.Current.SetTag(prefixed, value);
    }
    catch
    {
        // Ignore all exceptions
    }
}
```

---

## 4. Data Type Support Summary

Both approaches support standard OpenTelemetry attribute types. The `MotadataDynamicInstrumentation` utility specifically handles type safety.

| Category | Supported .NET Types | Behavior |
| :--- | :--- | :--- |
| **Text** | `string` | Stored as String. |
| **Integer** | `int`, `long` | Stored as **Long**. |
| **Decimal** | `double`, `float` | Stored as **Double**. |
| **Boolean** | `bool` | Stored as Boolean. |
| **Lists** | `string[]`, `int[]`, `long[]`, `double[]`, `float[]`, `bool[]` | Stored as Arrays. |

---

## 5. Runtime Execution (Agent Attachment)

The method of initializing the instrumentation remains **identical to Zero-Code Instrumentation**. You must still attach the Motadata .NET Agent at runtime.

The only difference is that the **client application code has been modified** to capture specific attributes using the methods described above.

---

## 6. Resources & Verification

**GitHub Repository:** [**Sample .NET Application**](https://github.com/motadata2025/Custom-Attribute-Instrumentation-Sample-Apps/tree/main/Sample%20Apps/DotNet%20Custom%20Attribute)

**Verification Snapshots:** [**View Testing Snapshots on GitHub**](https://github.com/motadata2025/Custom-Attribute-Instrumentation-Sample-Apps/tree/main/Sample%20Apps/DotNet%20Custom%20Attribute/Core/Testing%20Snapshots)

**Custom Attribute Supported Datatype:** [**Supported Data Types**](https://motadataindia-my.sharepoint.com/:x:/r/personal/shiven_patel_motadata_com/_layouts/15/Doc.aspx?sourcedoc=%7BA95ADCCD-C7B9-4612-9BC9-5CFE1693A12D%7D&file=Custom%20Attribute%20Support.xlsx&action=default&mobileredirect=true&DefaultItemOpen=1&wdOrigin=APPHOME-WEB.DIRECT%2CAPPHOME-WEB.FILEBROWSER.RECENT&wdPreviousSession=08f9a629-a27d-48d1-84b4-ae788cafe875&wdPreviousSessionSrc=AppHomeWeb&ct=1765894539141)

---

> **Disclaimer:**
> This documentation and the associated findings are based on sample tests performed on sample .NET applications. Implementation details in a production environment may vary depending on specific framework versions, existing instrumentation, and architectural constraints.
