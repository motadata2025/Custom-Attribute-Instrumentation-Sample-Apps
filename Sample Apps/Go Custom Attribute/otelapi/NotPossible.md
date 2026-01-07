Here's a professional Jira comment explaining why attributes cannot be added to the current auto-instrumented span, with proper references:

---

## Issue Summary

Custom attributes added via `trace.SpanFromContext(ctx).SetAttributes()` are **not appearing** in auto-instrumented spans when using eBPF-based OpenTelemetry Go instrumentation.

## Root Cause Analysis

The Go eBPF auto-instrumentation framework operates at the **kernel/eBPF level** and creates spans independently from the application's Go runtime context. When using `trace.SpanFromContext(r.Context())` in application code, it returns a **non-recording no-op span** rather than the actual auto-instrumented span.

### Technical Details

1. **eBPF Instrumentation Architecture**: The eBPF instrumentation works by intercepting system calls and library functions at the kernel level. These spans are created **outside** the Go application's memory space and are not propagated into the application's `context.Context` in a way that allows direct modification via `trace.SpanFromContext()`.

2. **Span Context Validation**: Debug logging confirms the issue:
   ```
   log.Printf("DEBUG: Span Context - TraceID: %s, SpanID: %s, IsSampled: %v, IsValid: %v",
		sc.TraceID(), sc.SpanID(), sc.IsSampled(), sc.IsValid())
   
   DEBUG: Span Context - TraceID: 00000000000000000000000000000000,
   SpanID: 0000000000000000, IsSampled: false, IsValid: false
   ```
   The all-zero TraceID and SpanID indicate that `trace.SpanFromContext()` is returning an invalid, non-recording span.

3. **Auto SDK Design Limitation**: According to the official OpenTelemetry documentation, the Go Auto SDK is designed to **create new manual spans** that link with auto-instrumented spans through context propagation, not to enrich existing auto-instrumented spans directly.

## Official Documentation References

### 1. OpenTelemetry Go Auto SDK Documentation
**URL**: https://opentelemetry.io/docs/zero-code/go/autosdk/

**Key Quote**:
> "Creating manual spans using the Auto SDK is essentially the same as creating spans using standard Go instrumentation... using it is as simple as creating manual spans with `tracer.Start()`"

The documentation explicitly shows creating **new spans** with `tracer.Start()`, not enriching existing spans with `trace.SpanFromContext()`.

### 2. How the Auto SDK Works
**From the same documentation**:
> "Essentially the Auto SDK is how OpenTelemetry eBPF identifies and orchestrates context propagation with the standard OpenTelemetry API, by instrumenting OpenTelemetry function symbols much like it does for any other package."

This confirms that the Auto SDK creates **new spans** that participate in context propagation, rather than allowing modification of eBPF-generated spans.

### 3. Important Constraint
**URL**: https://opentelemetry.io/docs/zero-code/go/autosdk/#auto-sdk-tracerprovider

**Key Quote**:
> "Manually setting a global TracerProvider will conflict with the Auto SDK and prevent manual spans from properly correlating with eBPF-based spans."

This highlights that the Auto SDK manages its own TracerProvider and span lifecycle independently from manual instrumentation attempts.

## Solution

The **correct and only supported approach** is to create **child spans** using `tracer.Start()` that will automatically link to the auto-instrumented spans:

### Correct Implementation Pattern

```go
func (h *UserHandler) GetUser(w http.ResponseWriter, r *http.Request) {
    // Create a NEW manual span using Auto SDK
    tracer := otel.Tracer("user-handler")
    ctx, span := tracer.Start(r.Context(), "GetUser-Handler")
    defer span.End()

    // Add custom attributes to YOUR manual span
    span.SetAttributes(
        attribute.String("apm.http.method", r.Method),
        attribute.String("apm.operation", "get_user"),
    )

    // Business logic...
}
```

### Resulting Trace Structure

```
GET /users/johndoe (eBPF auto-instrumented HTTP span)
└── GetUser-Handler (manual span with custom attributes)
    └── GetUserByUsername-Repository (manual span with custom attributes)
        └── DB (eBPF auto-instrumented database span)
```

## Why This Approach is Necessary

1. **Architecture Boundary**: eBPF operates at kernel level; Go application operates at user space. Direct span modification across this boundary is not supported.

2. **Span Ownership**: Auto-instrumented spans are owned and managed by the eBPF agent, not by the Go application runtime.

3. **Context Propagation Design**: The Auto SDK is specifically designed to enable context propagation **between** auto-instrumented and manual spans, not to modify auto-instrumented spans directly.

## Additional References

- **OpenTelemetry Go eBPF Auto-Instrumentation GitHub**: https://github.com/open-telemetry/opentelemetry-go-instrumentation
- **OpenTelemetry Specification - Context Propagation**: https://opentelemetry.io/docs/specs/otel/context/
- **Go Auto SDK Package Documentation**: https://pkg.go.dev/go.opentelemetry.io/auto/sdk

## Conclusion

The inability to enrich auto-instrumented spans directly is **by design**, not a bug. The supported pattern is to create manual child spans with custom attributes that automatically link to the auto-instrumented parent spans through the Auto SDK's context propagation mechanism.

---

**Recommendation**: Update implementation to use `tracer.Start()` for creating manual spans with custom attributes instead of attempting to enrich auto-instrumented spans via `trace.SpanFromContext()`.