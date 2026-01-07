# Method 2: Span Creation Implementation

## Overview
This document describes the implementation of **Method 2: Span Creation** in the oteltracer application. This method creates custom spans with full control over span lifecycle, attributes, events, and status.

## Key Differences from Method 1
| Aspect | Method 1 (Active Span Enrichment) | Method 2 (Span Creation) |
|--------|-----------------------------------|--------------------------|
| **Span Creation** | ❌ Uses existing spans | ✅ Creates new custom spans |
| **Span Control** | ❌ Limited | ✅ Full control (name, kind, lifecycle) |
| **Nested Spans** | ❌ Cannot create | ✅ Can create hierarchies |
| **Events** | ❌ Cannot add | ✅ Can add custom events |
| **Complexity** | ⭐ Low | ⭐⭐ Medium |
| **Use Case** | Quick enrichment | Detailed instrumentation |

## Implementation Architecture

### Components
1. **TracerService** (`services/tracerService.js`) - Centralized tracer management
2. **UserController** (`controllers/userController.js`) - Controller with custom spans
3. **OpenTelemetry API** - Core tracing functionality

### Tracer Service
The `TracerService` provides:
- Centralized tracer instance
- Helper methods for span creation
- Automatic span lifecycle management
- Common attribute patterns
- Error handling

## Custom Attributes with `apm.*` Prefix

### Common Attributes (All Operations)
| Attribute | Type | Description | Example |
|-----------|------|-------------|---------|
| `apm.operation` | string | Controller method name | `getAllUsers` |
| `apm.controller` | string | Controller class name | `UserController` |
| `apm.method` | string | HTTP method | `GET`, `POST`, `PUT`, `DELETE` |
| `apm.endpoint` | string | Request path | `/users`, `/users/:username` |
| `apm.http.status_code` | number | HTTP response status | `200`, `404`, `500` |
| `apm.result.success` | boolean | Operation success status | `true`, `false` |

### Database Operation Attributes
| Attribute | Type | Description | Example |
|-----------|------|-------------|---------|
| `apm.db.operation` | string | Database operation type | `SELECT`, `INSERT`, `UPDATE`, `DELETE` |
| `apm.db.table` | string | Database table name | `nodejs_user_tbl` |
| `apm.db.username` | string | Username in query | `johndoe` |
| `apm.db.rows_returned` | number | Number of rows returned | `10` |
| `apm.db.found` | boolean | Whether record was found | `true`, `false` |
| `apm.db.created_id` | number | ID of created record | `123` |
| `apm.db.updated_id` | number | ID of updated record | `123` |
| `apm.db.deleted_id` | number | ID of deleted record | `123` |

### Validation Attributes
| Attribute | Type | Description |
|-----------|------|-------------|
| `apm.validation.failed` | boolean | Whether validation failed |
| `apm.validation.passed` | boolean | Whether validation passed |
| `apm.validation.error` | string | Validation error message |
| `apm.validation.username_provided` | boolean | Username provided |
| `apm.validation.email_provided` | boolean | Email provided |

### Error Attributes
| Attribute | Type | Description |
|-----------|------|-------------|
| `apm.error.occurred` | boolean | Whether an error occurred |
| `apm.error.message` | string | Error message |
| `apm.error.type` | string | Error type/class name |
| `apm.conflict.occurred` | boolean | Whether a conflict occurred |
| `apm.conflict.reason` | string | Conflict reason |

## Span Hierarchy

### Example: createUser Operation
```
UserController.createUser (INTERNAL)
├── UserController.createUser.validation (INTERNAL)
├── UserController.createUser.checkExists (CLIENT)
└── UserController.createUser.database (CLIENT)
```

### Example: getAllUsers Operation
```
UserController.getAllUsers (INTERNAL)
└── UserController.getAllUsers.database (CLIENT)
```

### Span Kinds
- **INTERNAL**: Internal application operations (controller methods)
- **CLIENT**: Outgoing calls (database queries)
- **SERVER**: Incoming requests (handled by auto-instrumentation)

## Custom Events

Events mark specific points in time within a span with optional attributes.

### Common Events
| Event Name | When | Attributes |
|------------|------|------------|
| `{operation}.started` | Operation begins | Operation-specific data |
| `{operation}.success` | Operation succeeds | Result data |
| `{operation}.error` | Operation fails | Error details |
| `{operation}.not_found` | Record not found | Search criteria |
| `{operation}.conflict` | Conflict occurs | Conflict reason |

### Example Events in createUser
```javascript
span.addEvent('createUser.started');
span.addEvent('createUser.conflict', { 'conflict.reason': 'Username already exists' });
span.addEvent('createUser.success', { 'user.id': newUser.id });
```

## Code Examples

### Basic Span Creation Pattern
```javascript
const tracerService = require('../services/tracerService');
const { SpanKind } = require('@opentelemetry/api');

// Create a span with automatic lifecycle management
return tracerService.executeInSpan(
  'MyOperation',
  async (span) => {
    // Add attributes
    span.setAttribute('apm.operation', 'myOperation');

    // Add events
    span.addEvent('operation.started');

    // Your business logic
    const result = await doSomething();

    // Add success attributes
    tracerService.addSuccessAttributes(span, 200, {
      'apm.result.count': result.length
    });

    return result;
  },
  { kind: SpanKind.INTERNAL }
);
```

### Nested Spans Pattern
```javascript
return tracerService.executeInSpan(
  'ParentOperation',
  async (parentSpan) => {
    // Parent span attributes


## TracerService API Reference

### Methods

#### `executeInSpan(spanName, fn, options)`
Execute a function within a custom span with automatic lifecycle management.

**Parameters:**
- `spanName` (string): Name of the span
- `fn` (async function): Function to execute, receives span as parameter
- `options` (object): Span options
  - `kind` (SpanKind): Span kind (INTERNAL, CLIENT, SERVER, PRODUCER, CONSUMER)
  - `attributes` (object): Initial attributes to set

**Returns:** Promise with function result

**Example:**
```javascript
const result = await tracerService.executeInSpan(
  'MyOperation',
  async (span) => {
    span.setAttribute('key', 'value');
    return await doWork();
  },
  { kind: SpanKind.INTERNAL }
);
```

#### `addCommonAttributes(span, metadata)`
Add common APM attributes to a span.

**Parameters:**
- `span` (Span): OpenTelemetry span
- `metadata` (object): Metadata object with common fields

**Example:**
```javascript
tracerService.addCommonAttributes(span, {
  operation: 'getAllUsers',
  controller: 'UserController',
  method: 'GET',
  endpoint: '/users'
});
```

#### `addSuccessAttributes(span, statusCode, data)`
Add success attributes to a span.

**Parameters:**
- `span` (Span): OpenTelemetry span
- `statusCode` (number): HTTP status code (default: 200)
- `data` (object): Additional attributes

**Example:**
```javascript
tracerService.addSuccessAttributes(span, 200, {
  'apm.result.count': 10,
  'apm.result.has_data': true
});
```

#### `addErrorAttributes(span, error, statusCode)`
Add error attributes to a span and record exception.

**Parameters:**
- `span` (Span): OpenTelemetry span
- `error` (Error): Error object
- `statusCode` (number): HTTP status code (default: 500)

**Example:**
```javascript
tracerService.addErrorAttributes(span, error, 500);
```

## Operation-Specific Implementation

### getAllUsers
**Span Hierarchy:**
```
UserController.getAllUsers (INTERNAL)
└── UserController.getAllUsers.database (CLIENT)
```

**Attributes:**
- `apm.operation`: `getAllUsers`
- `apm.result.count`: Number of users
- `apm.result.has_data`: Whether data exists
- `apm.db.operation`: `SELECT`
- `apm.db.rows_returned`: Number of rows

**Events:**
- `getAllUsers.started`
- `getAllUsers.users_retrieved` (with count)
- `getAllUsers.error` (on failure)

### getUserByUsername
**Span Hierarchy:**
```
UserController.getUserByUsername (INTERNAL)
└── UserController.getUserByUsername.database (CLIENT)
```

**Attributes:**
- `apm.operation`: `getUserByUsername`
- `apm.user.username`: Username being queried
- `apm.result.found`: Whether user was found
- `apm.user.id`: User ID (if found)
- `apm.db.query.username`: Username in query

**Events:**
- `getUserByUsername.started`
- `getUserByUsername.found` (on success)
- `getUserByUsername.not_found` (on 404)
- `getUserByUsername.error` (on failure)

### createUser
**Span Hierarchy:**
```
UserController.createUser (INTERNAL)
├── UserController.createUser.validation (INTERNAL)
├── UserController.createUser.checkExists (CLIENT)
└── UserController.createUser.database (CLIENT)
```

**Attributes:**
- `apm.operation`: `createUser`
- `apm.user.username`: Username being created
- `apm.user.email`: User email
- `apm.user.tags`: User tags array
- `apm.user.tags_count`: Number of tags
- `apm.validation.passed/failed`: Validation result
- `apm.conflict.occurred`: Whether username exists
- `apm.result.created`: Whether user was created
- `apm.db.created_id`: Created user ID

**Events:**
- `createUser.started`
- `createUser.conflict` (on username exists)
- `createUser.success` (on success)
- `createUser.error` (on failure)

### updateUser
**Span Hierarchy:**
```
UserController.updateUser (INTERNAL)
├── UserController.updateUser.checkExists (CLIENT)
└── UserController.updateUser.database (CLIENT)
```

**Attributes:**
- `apm.operation`: `updateUser`
- `apm.user.username`: Username being updated
- `apm.update.fields`: Array of fields being updated
- `apm.update.fields_count`: Number of fields
- `apm.result.updated`: Whether user was updated
- `apm.db.update_fields`: Fields being updated

**Events:**
- `updateUser.started`
- `updateUser.not_found` (on 404)
- `updateUser.success` (on success)
- `updateUser.error` (on failure)

### deleteUser
**Span Hierarchy:**
```
UserController.deleteUser (INTERNAL)
└── UserController.deleteUser.database (CLIENT)
```

**Attributes:**
- `apm.operation`: `deleteUser`
- `apm.user.username`: Username being deleted
- `apm.result.deleted`: Whether user was deleted
- `apm.db.deleted_id`: Deleted user ID

**Events:**
- `deleteUser.started`
- `deleteUser.not_found` (on 404)
- `deleteUser.success` (on success)
- `deleteUser.error` (on failure)

## Benefits of This Implementation

### ✅ Advantages
1. **Full Span Control**: Complete control over span name, kind, and lifecycle
2. **Nested Spans**: Create detailed hierarchies for complex operations
3. **Custom Events**: Mark important points in time with context
4. **Automatic Error Handling**: TracerService handles exceptions automatically
5. **Rich Context**: Detailed attributes at each level of operation
6. **Performance Insights**: See exactly where time is spent (validation, DB, etc.)
7. **Reusable Patterns**: TracerService provides consistent patterns

### ⚠️ Considerations
1. **More Code**: Requires more code than Method 1
2. **Complexity**: Need to manage span hierarchy
3. **Must End Spans**: Spans must be properly ended (handled by executeInSpan)
4. **Performance**: Creating spans has overhead (minimal but measurable)

## Best Practices

### 1. Use Meaningful Span Names
```javascript
// ✅ Good: Descriptive, hierarchical
'UserController.createUser'
'UserController.createUser.validation'
'UserController.createUser.database'

// ❌ Bad: Generic, unclear
'operation'
'db'
'check'
```

### 2. Set Appropriate Span Kinds
```javascript
// INTERNAL: Application logic
{ kind: SpanKind.INTERNAL }

// CLIENT: Outgoing calls (DB, HTTP, etc.)
{ kind: SpanKind.CLIENT }

// SERVER: Incoming requests (usually auto-instrumented)
{ kind: SpanKind.SERVER }
```

### 3. Add Events at Key Points
```javascript
span.addEvent('operation.started');
span.addEvent('validation.completed', { 'validation.passed': true });
span.addEvent('database.query_executed', { 'rows.affected': 5 });
span.addEvent('operation.completed');
```

### 4. Use Nested Spans for Sub-Operations
```javascript
// Parent span for overall operation
return tracerService.executeInSpan('createUser', async (span) => {

  // Child span for validation
  await tracerService.executeInSpan('createUser.validation', async (validationSpan) => {
    // Validation logic
  });

  // Child span for database
  await tracerService.executeInSpan('createUser.database', async (dbSpan) => {
    // Database logic
  });

}, { kind: SpanKind.INTERNAL });
```

### 5. Always Use executeInSpan for Automatic Cleanup
```javascript
// ✅ Good: Automatic span lifecycle management
return tracerService.executeInSpan('operation', async (span) => {
  // Work here
  // Span automatically ended, even on error
});

// ❌ Bad: Manual span management (error-prone)
const span = tracerService.createSpan('operation');
try {
  // Work here
} finally {
  span.end(); // Easy to forget!
}
```

## Testing the Implementation

### Prerequisites
1. OpenTelemetry SDK must be configured
2. An exporter must be configured (OTLP, Jaeger, Zipkin, etc.)
3. A backend must be running to receive traces

### Test Scenarios

#### 1. Test getAllUsers
```bash
curl http://localhost:8080/users
```

**Expected Spans:**
- `UserController.getAllUsers` (INTERNAL)
  - `UserController.getAllUsers.database` (CLIENT)

**Expected Attributes:**
- Parent: `apm.operation=getAllUsers`, `apm.result.count=N`
- Child: `apm.db.operation=SELECT`, `apm.db.rows_returned=N`

**Expected Events:**
- `getAllUsers.started`
- `getAllUsers.users_retrieved`

#### 2. Test createUser (Success)
```bash
curl -X POST http://localhost:8080/users \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "tags": ["developer", "nodejs"]
  }'
```

**Expected Spans:**
- `UserController.createUser` (INTERNAL)
  - `UserController.createUser.validation` (INTERNAL)
  - `UserController.createUser.checkExists` (CLIENT)
  - `UserController.createUser.database` (CLIENT)

**Expected Events:**
- `createUser.started`
- `createUser.success`

#### 3. Test createUser (Validation Error)
```bash
curl -X POST http://localhost:8080/users \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser"}'
```

**Expected Attributes:**
- `apm.validation.failed=true`
- `apm.http.status_code=400`

#### 4. Test createUser (Conflict)
```bash
# Create user first, then try again with same username
curl -X POST http://localhost:8080/users \
  -H "Content-Type: application/json" \
  -d '{"username": "duplicate", "email": "test@example.com"}'
```

**Expected Attributes:**
- `apm.conflict.occurred=true`
- `apm.conflict.reason=Username already exists`

**Expected Events:**
- `createUser.conflict`

## Viewing Traces

### Jaeger UI
1. Navigate to http://localhost:16686
2. Select service: `oteltracer-service`
3. Find operation: `UserController.createUser`
4. View span hierarchy and attributes

### Expected Trace View
```
UserController.createUser (150ms)
├── UserController.createUser.validation (5ms)
├── UserController.createUser.checkExists (20ms)
└── UserController.createUser.database (100ms)
```

## Troubleshooting

### Spans Not Appearing?
1. **Check tracer initialization**: Ensure SDK is configured
2. **Verify exporter**: Check exporter configuration
3. **Force flush**: `await provider.forceFlush()`

### Nested Spans Not Showing?
1. **Check context propagation**: Ensure spans are created within parent context
2. **Use executeInSpan**: This automatically handles context
3. **Verify span kinds**: Different kinds may display differently

### Events Not Visible?
1. **Check backend support**: Not all backends display events prominently
2. **Look in span details**: Events are usually in span detail view
3. **Verify event format**: Ensure event attributes are valid types

## Performance Considerations

### Overhead
- **Span creation**: ~10-50 microseconds per span
- **Attribute setting**: ~1-5 microseconds per attribute
- **Event recording**: ~5-10 microseconds per event
- **Total overhead**: Usually <1% for typical operations

### Recommendations
1. **Limit nesting depth**: Keep to 3-4 levels maximum
2. **Avoid excessive attributes**: 20-30 attributes per span is reasonable
3. **Use sampling**: For high-traffic endpoints, use sampling
4. **Batch export**: Use BatchSpanProcessor for better performance

## Next Steps

### Extend to Other Controllers
Apply the same pattern to other controllers:
1. Import `tracerService` and `SpanKind`
2. Wrap operations in `executeInSpan`
3. Create nested spans for sub-operations
4. Add attributes, events, and error handling

### Combine with Other Methods
- **Method 1**: Use for simple attribute enrichment
- **Method 2**: Use for detailed instrumentation (current)
- **Method 3**: Use baggage for cross-service context
- **Method 4**: Use SpanProcessor for global attributes

## References
- [OpenTelemetry JavaScript API](https://opentelemetry.io/docs/languages/js/)
- [Trace API Specification](https://opentelemetry.io/docs/specs/otel/trace/api/)
- [Span API](https://opentelemetry.io/docs/specs/otel/trace/api/#span)
- [THE_4_METHODS.md](../../THE_4_METHODS.md) - Complete guide to all 4 methods

---

**Version**: 1.0.0
**Last Updated**: December 2024
**Implementation**: oteltracer/controllers/userController.js, oteltracer/services/tracerService.js

