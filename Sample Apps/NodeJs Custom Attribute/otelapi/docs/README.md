# OpenTelemetry Custom Attributes Documentation

Welcome to the comprehensive guide for adding custom attributes in Node.js applications using OpenTelemetry.

## 📚 Documentation Files

### [OPENTELEMETRY_CUSTOM_ATTRIBUTES.md](./OPENTELEMETRY_CUSTOM_ATTRIBUTES.md)
**Complete comprehensive guide** covering all 4 methods in detail with:
- In-depth explanations
- Code examples (basic and advanced)
- Use cases and when to use each method
- Best practices and security considerations
- Common pitfalls and how to avoid them
- Real-world examples

**Recommended for:** Developers implementing OpenTelemetry for the first time or looking for detailed understanding.

### [QUICK_REFERENCE.md](./QUICK_REFERENCE.md)
**Quick reference guide** with:
- One-page overview of all 4 methods
- Decision tree for choosing the right method
- Comparison table
- Common patterns
- Best practices checklist

**Recommended for:** Quick lookups and daily reference.

---

## 🎯 The 4 Methods Overview

### Method 1: Active Span Enrichment
Add attributes to existing spans created by auto-instrumentation.

**Complexity:** ⭐ Low  
**Use Case:** Business context, request metadata

### Method 2: Manual Tracer and Span Creation
Create new spans with full lifecycle control using the tracer API.

**Complexity:** ⭐⭐ Medium
**Use Case:** Custom operations, hierarchical tracing

### Method 3: Baggage Propagation
Propagate context across service boundaries.

**Complexity:** ⭐⭐⭐ Medium-High  
**Use Case:** Distributed tracing, correlation IDs

### Method 4: SpanProcessor
Centralized attribute injection at SDK level.

**Complexity:** ⭐⭐ Medium  
**Use Case:** Environment metadata, zero-code enrichment

---

## 🚀 Quick Start

### 1. Install Dependencies

```bash
npm install @opentelemetry/api @opentelemetry/sdk-trace-node
```

### 2. Choose Your Method

```javascript
// Method 1: Active Span Enrichment
const span = trace.getActiveSpan();
if (span) {
  span.setAttribute('user.id', userId);
}

// Method 2: Manual Tracer and Span Creation
tracer.startActiveSpan('operation', (span) => {
  span.setAttribute('key', 'value');
  span.end();
});

// Method 3: Baggage Propagation
const baggage = propagation.createBaggage({
  'tenant.id': { value: tenantId }
});

// Method 4: SpanProcessor
class CustomProcessor {
  onStart(span) {
    span.setAttribute('env', process.env.NODE_ENV);
  }
}
```

---

## 📖 Learning Path

### Beginner
1. Start with [QUICK_REFERENCE.md](./QUICK_REFERENCE.md)
2. Try Method 1 (Active Span Enrichment)
3. Understand the decision tree

### Intermediate
1. Read [OPENTELEMETRY_CUSTOM_ATTRIBUTES.md](./OPENTELEMETRY_CUSTOM_ATTRIBUTES.md) - Methods 1 & 2
2. Implement Method 2 (Explicit Span Creation)
3. Review best practices section

### Advanced
1. Study Method 3 (Baggage Propagation)
2. Implement Method 4 (SpanProcessor)
3. Review real-world examples
4. Combine multiple methods

---

## 🎓 Key Concepts

### Spans
Represent a unit of work in a distributed system. Can have attributes, events, and links.

### Attributes
Key-value pairs that provide context about a span (e.g., user ID, HTTP method, database query).

### Baggage
Context propagation mechanism for passing data across service boundaries via HTTP headers.

### SpanProcessor
SDK component that processes spans when they start and end, allowing centralized attribute injection.

---

## ⚠️ Important Warnings

### Security
- **Never put sensitive data in baggage** (passwords, API keys, PII)
- Baggage is transmitted in HTTP headers and visible to network monitoring

### Performance
- **Manage attribute cardinality** - avoid unique values per request
- **Always end spans** to prevent memory leaks
- Keep SpanProcessor operations fast

### Best Practices
- Always check if span exists before adding attributes
- Use semantic conventions for standard attributes
- Namespace custom attributes (business.*, app.*)
- Use try/finally to ensure spans are ended

---

## 🔗 External Resources

- [OpenTelemetry Official Docs](https://opentelemetry.io/docs/)
- [Node.js SDK Documentation](https://opentelemetry.io/docs/languages/js/)
- [Semantic Conventions](https://opentelemetry.io/docs/specs/semconv/)
- [Baggage Specification](https://opentelemetry.io/docs/concepts/signals/baggage/)
- [Community Slack](https://cloud-native.slack.com/archives/C01N7PP1THC)

---

## 📝 Contributing

Found an issue or want to improve the documentation? Please open an issue or submit a pull request.

---

**Last Updated:** December 2024  
**Version:** 1.0.0

