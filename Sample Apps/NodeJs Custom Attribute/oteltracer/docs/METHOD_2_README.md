# Method 2: Span Creation - Complete Implementation

## 🎯 Overview
This directory contains a complete implementation of **Method 2: Span Creation** for OpenTelemetry custom attributes in Node.js. This method creates custom spans with full control over span lifecycle, attributes, events, and status.

## 📁 Implementation Files

### Core Implementation
- **`services/tracerService.js`** - Centralized tracer service with helper methods
- **`controllers/userController.js`** - All 5 controller methods instrumented with custom spans

### Documentation
- **`METHOD_2_QUICK_START.md`** - Quick start guide (start here!)
- **`METHOD_2_SPAN_CREATION.md`** - Complete implementation guide
- **`METHOD_2_IMPLEMENTATION_SUMMARY.md`** - Implementation summary
- **`METHOD_2_README.md`** - This file

## 🚀 Quick Start

### 1. Prerequisites
```bash
# Ensure OpenTelemetry packages are installed
npm install @opentelemetry/api @opentelemetry/sdk-node @opentelemetry/auto-instrumentations-node
```

### 2. Basic Usage
```javascript
const tracerService = require('../services/tracerService');
const { SpanKind } = require('@opentelemetry/api');

// Wrap your operation in a custom span
return tracerService.executeInSpan(
  'MyOperation',
  async (span) => {
    // Add attributes
    tracerService.addCommonAttributes(span, {
      operation: 'myOperation',
      controller: 'MyController'
    });
    
    // Add events
    span.addEvent('operation.started');
    
    // Your business logic
    const result = await doWork();
    
    // Add success attributes
    tracerService.addSuccessAttributes(span, 200);
    
    return result;
  },
  { kind: SpanKind.INTERNAL }
);
```

### 3. Test It
```bash
# Start the application
npm start

# Make a request
curl http://localhost:8080/users

# View traces in Jaeger
open http://localhost:16686
```

## 🏗️ Architecture

### TracerService
Centralized service providing:
- ✅ Singleton tracer instance
- ✅ Automatic span lifecycle management
- ✅ Helper methods for common patterns
- ✅ Error handling with exception recording
- ✅ Context propagation for nested spans

### UserController
All 5 methods instrumented:
1. **getAllUsers** - Simple operation with database span
2. **getUserByUsername** - Operation with 404 handling
3. **createUser** - Complex operation with validation, check, and database spans
4. **updateUser** - Operation with field tracking
5. **deleteUser** - Operation with deletion tracking

## 📊 Span Hierarchy

### Simple Operation (getAllUsers)
```
UserController.getAllUsers (INTERNAL)
└── UserController.getAllUsers.database (CLIENT)
```

### Complex Operation (createUser)
```
UserController.createUser (INTERNAL)
├── UserController.createUser.validation (INTERNAL)
├── UserController.createUser.checkExists (CLIENT)
└── UserController.createUser.database (CLIENT)
```

## 🏷️ Custom Attributes

All attributes use the `apm.*` prefix for consistency:

### Common Attributes
- `apm.operation` - Operation name
- `apm.controller` - Controller name
- `apm.method` - HTTP method
- `apm.endpoint` - Request path
- `apm.http.status_code` - Response status
- `apm.result.success` - Success/failure flag

### Database Attributes
- `apm.db.operation` - SQL operation type
- `apm.db.table` - Table name
- `apm.db.rows_returned` - Number of rows
- `apm.db.found` - Record found flag
- `apm.db.created_id` - Created record ID

### Validation Attributes
- `apm.validation.passed` - Validation success
- `apm.validation.failed` - Validation failure
- `apm.validation.error` - Validation error message

### Error Attributes
- `apm.error.occurred` - Error flag
- `apm.error.message` - Error message
- `apm.error.type` - Error type

## 📅 Custom Events

Events mark important points in time:
- `{operation}.started` - Operation begins
- `{operation}.success` - Operation succeeds
- `{operation}.error` - Operation fails
- `{operation}.not_found` - Record not found
- `{operation}.conflict` - Conflict occurs

## 🎨 Key Features

### 1. Automatic Span Lifecycle
```javascript
// Span automatically started and ended
return tracerService.executeInSpan('operation', async (span) => {
  // Work here
  // Span ended automatically, even on error
});
```

### 2. Nested Spans
```javascript
return tracerService.executeInSpan('parent', async (parentSpan) => {
  // Parent work
  
  await tracerService.executeInSpan('child', async (childSpan) => {
    // Child work - automatically linked to parent
  });
});
```

### 3. Automatic Error Handling
```javascript
// Errors automatically:
// - Recorded as exceptions
// - Set span status to ERROR
// - Add error attributes
// - Re-thrown for application handling
```

### 4. Helper Methods
```javascript
// Common attributes
tracerService.addCommonAttributes(span, { operation: 'myOp' });

// Success attributes
tracerService.addSuccessAttributes(span, 200, { 'apm.result.count': 10 });

// Error attributes
tracerService.addErrorAttributes(span, error, 500);
```

## 🧪 Testing

### Test All Operations
```bash
# Get all users
curl http://localhost:8080/users

# Get user by username
curl http://localhost:8080/users/johndoe

# Create user
curl -X POST http://localhost:8080/users \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "email": "test@example.com", "tags": ["developer"]}'

# Update user
curl -X PUT http://localhost:8080/users/testuser \
  -H "Content-Type: application/json" \
  -d '{"email": "newemail@example.com", "age": 30}'

# Delete user
curl -X DELETE http://localhost:8080/users/testuser
```

### View Traces in Jaeger
1. Open http://localhost:16686
2. Select service: `oteltracer-service`
3. Find operation: `UserController.{operation}`
4. View:
   - Span hierarchy
   - Custom attributes with `apm.*` prefix
   - Events at key points
   - Error details (if any)

## 📈 Benefits

### Observability
- ✅ Detailed span hierarchies show operation flow
- ✅ Custom attributes provide business context
- ✅ Events mark important points in time
- ✅ Error tracking with full context

### Performance
- ✅ See exactly where time is spent
- ✅ Identify slow database queries
- ✅ Track validation overhead
- ✅ Measure nested operation duration

### Debugging
- ✅ Trace request flow through application
- ✅ See which operations succeeded/failed
- ✅ Understand error context
- ✅ Track data transformations

## 🔄 Comparison with Other Methods

| Feature | Method 1 | Method 2 | Method 3 | Method 4 |
|---------|----------|----------|----------|----------|
| **Creates Spans** | ❌ | ✅ | ❌ | ❌ |
| **Nested Spans** | ❌ | ✅ | ❌ | ❌ |
| **Custom Events** | ❌ | ✅ | ❌ | ❌ |
| **Cross-Service** | ❌ | ❌ | ✅ | ❌ |
| **Global Attributes** | ❌ | ❌ | ❌ | ✅ |
| **Complexity** | Low | Medium | Low | Medium |

## 📚 Documentation

### Quick Start
Start with **`METHOD_2_QUICK_START.md`** for a quick introduction.

### Complete Guide
See **`METHOD_2_SPAN_CREATION.md`** for:
- Detailed implementation guide
- API reference
- Best practices
- Troubleshooting
- Performance considerations

### Implementation Summary
See **`METHOD_2_IMPLEMENTATION_SUMMARY.md`** for:
- What was implemented
- Span hierarchies
- Attribute catalog
- Testing guide

## 🚀 Next Steps

### 1. Extend to Other Controllers
Apply the same pattern to other controllers:
```javascript
const tracerService = require('../services/tracerService');
const { SpanKind } = require('@opentelemetry/api');

class MyController {
  static async myMethod(req, res) {
    return tracerService.executeInSpan(
      'MyController.myMethod',
      async (span) => {
        // Your implementation
      },
      { kind: SpanKind.INTERNAL }
    );
  }
}
```

### 2. Combine with Other Methods
- **Method 1**: Use for simple attribute enrichment
- **Method 3**: Use baggage for cross-service context
- **Method 4**: Use SpanProcessor for global attributes

### 3. Customize for Your Needs
- Add domain-specific attributes
- Create custom events for business milestones
- Implement custom span processors
- Add sampling strategies

## 🐛 Troubleshooting

### Spans not appearing?
- Ensure OpenTelemetry SDK is configured
- Check exporter configuration
- Verify tracer is initialized

### Nested spans not showing?
- Use `executeInSpan` for automatic context propagation
- Check that child spans are created within parent span function

### Events not visible?
- Check backend support (Jaeger shows events in span details)
- Verify event attributes are valid types

## 📞 Support

For questions or issues:
1. Check the documentation files
2. Review the implementation in `services/tracerService.js`
3. Look at examples in `controllers/userController.js`
4. Refer to [OpenTelemetry JavaScript documentation](https://opentelemetry.io/docs/languages/js/)

---

**Implementation Status**: ✅ Complete  
**Version**: 1.0.0  
**Last Updated**: December 2024  
**Method**: Method 2 - Span Creation

