# OpenTelemetry Span Attribute Data Type Testing API

## Overview
This API endpoint tests which data types are supported as OpenTelemetry span attributes. It helps verify compatibility and understand limitations when adding custom attributes to spans.

## Endpoint

### GET `/test/datatypes`

Tests the following data types:
- ✅ `string` - String values
- ✅ `number` - Numeric values (integers and decimals)
- ✅ `boolean` - Boolean values (true/false)
- ✅ `string[]` - Array of strings
- ✅ `number[]` - Array of numbers
- ✅ `boolean[]` - Array of booleans
- ⚠️ Edge cases: empty values, null, undefined, objects, nested arrays

## Usage

### cURL
```bash
curl http://localhost:8080/test/datatypes
```

### Browser
```
http://localhost:8080/test/datatypes
```

### JavaScript/Fetch
```javascript
fetch('http://localhost:8080/test/datatypes')
  .then(response => response.json())
  .then(data => console.log(data));
```

## Response Format

### Success Response (200 OK)
```json
{
  "success": true,
  "message": "Data type testing completed",
  "summary": {
    "total_tested": 15,
    "supported_types": [
      "string",
      "number",
      "boolean",
      "string[]",
      "number[]",
      "boolean[]",
      "empty array"
    ],
    "unsupported_types": [
      "object",
      "null",
      "undefined"
    ],
    "error_count": 0
  },
  "details": [
    {
      "attribute": "apm.test.string",
      "dataType": "string",
      "value": "test-string-value",
      "status": "success"
    },
    {
      "attribute": "apm.test.number",
      "dataType": "number",
      "value": 42,
      "status": "success"
    },
    {
      "attribute": "apm.test.boolean",
      "dataType": "boolean",
      "value": true,
      "status": "success"
    },
    {
      "attribute": "apm.test.stringArray",
      "dataType": "string[]",
      "value": ["value1", "value2", "value3"],
      "status": "success"
    },
    {
      "attribute": "apm.test.numberArray",
      "dataType": "number[]",
      "value": [1, 2, 3, 4, 5],
      "status": "success"
    },
    {
      "attribute": "apm.test.booleanArray",
      "dataType": "boolean[]",
      "value": [true, false, true],
      "status": "success"
    }
  ],
  "errors": []
}
```

## Response Fields

### Summary Object
| Field | Type | Description |
|-------|------|-------------|
| `total_tested` | number | Total number of data types tested |
| `supported_types` | string[] | List of supported data types |
| `unsupported_types` | string[] | List of unsupported data types |
| `error_count` | number | Number of errors encountered |

### Details Array
Each item contains:
| Field | Type | Description |
|-------|------|-------------|
| `attribute` | string | Attribute name used in span |
| `dataType` | string | Data type being tested |
| `value` | any | Test value used |
| `status` | string | "success" or "error" |
| `error` | string | Error message (if status is "error") |

### Errors Array
Each item contains:
| Field | Type | Description |
|-------|------|-------------|
| `attribute` | string | Attribute name that failed |
| `error` | string | Error message |

## Tested Data Types

### Primitive Types
1. **string** - `"test-string-value"`
2. **number** - `42`
3. **boolean** - `true`

### Array Types
4. **string[]** - `["value1", "value2", "value3"]`
5. **number[]** - `[1, 2, 3, 4, 5]`
6. **boolean[]** - `[true, false, true]`

### Edge Cases
7. **empty string** - `""`
8. **zero number** - `0`
9. **false boolean** - `false`
10. **empty string array** - `[]`
11. **empty number array** - `[]`
12. **empty boolean array** - `[]`

### Unsupported Types (Expected to Fail)
13. **null** - `null`
14. **undefined** - `undefined`
15. **object** - `{ key: 'value' }`
16. **nested array** - `[[1, 2], [3, 4]]`
17. **mixed array** - `[1, 'two', true]`

## OpenTelemetry Span Attributes

### Attributes Added to Span
All test attributes use the `apm.test.*` prefix:
- `apm.test.string`
- `apm.test.number`
- `apm.test.boolean`
- `apm.test.stringArray`
- `apm.test.numberArray`
- `apm.test.booleanArray`
- ... and more

### Summary Attributes
- `apm.test.total_tested` - Total number of tests
- `apm.test.supported_count` - Number of supported types
- `apm.test.unsupported_count` - Number of unsupported types
- `apm.test.error_count` - Number of errors
- `apm.test.supported_types` - Array of supported type names

### Events Added to Span
- `datatype.test.success` - For each successful attribute
  - `test.attribute` - Attribute name
  - `test.type` - Data type
- `datatype.test.error` - For each failed attribute
  - `test.attribute` - Attribute name
  - `test.type` - Data type
  - `error.message` - Error message
- `testDataTypes.completed` - When all tests complete
  - `test.total` - Total tests
  - `test.supported` - Supported count

## Viewing Results in Jaeger

### 1. Make the API Request
```bash
curl http://localhost:8080/test/datatypes
```

### 2. Open Jaeger UI
```
http://localhost:16686
```

### 3. Find the Trace
- Service: `oteltracer-service`
- Operation: `DatatypeTestController.testDataTypes`

### 4. View Span Details
You'll see:
- All successfully set attributes with `apm.test.*` prefix
- Events marking successful and failed attribute attempts
- Summary attributes showing test results

## Expected Results

### ✅ Supported Types (OpenTelemetry Specification)
According to the OpenTelemetry specification, the following types are supported:
- **string** - UTF-8 encoded strings
- **number** - 64-bit floating point numbers (including integers)
- **boolean** - true or false
- **string[]** - Array of strings
- **number[]** - Array of numbers  
- **boolean[]** - Array of booleans

### ❌ Unsupported Types
- **null** - Not a valid attribute value
- **undefined** - Not a valid attribute value
- **object** - Complex objects are not supported
- **nested arrays** - Arrays of arrays are not supported
- **mixed arrays** - Arrays with mixed types are not supported

### ⚠️ Edge Cases
- **Empty strings** - Usually supported
- **Zero/false** - Usually supported (falsy but valid)
- **Empty arrays** - May or may not be supported depending on implementation

## Use Cases

### 1. Verify Data Type Support
Before using a data type in production spans, test it:
```bash
curl http://localhost:8080/test/datatypes | jq '.summary.supported_types'
```

### 2. Debug Attribute Issues
If attributes aren't appearing in traces, check if the data type is supported.

### 3. Documentation
Use the results to document which types your team can use in custom attributes.

### 4. Testing Different Backends
Different OpenTelemetry backends may handle types differently. Use this API to verify compatibility.

## Implementation Details

### Controller
- **File**: `controllers/datatypeTestController.js`
- **Method**: `testDataTypes(req, res)`
- **Span**: `DatatypeTestController.testDataTypes` (INTERNAL)

### Routes
- **File**: `routes/datatypeTestRoutes.js`
- **Path**: `/test/datatypes`
- **Method**: GET

### Swagger Documentation
Available at: `http://localhost:8080/swagger`
- Tag: **Testing**
- Full API documentation with examples

## Example Usage

### Test and View Results
```bash
# 1. Make the request
curl http://localhost:8080/test/datatypes | jq '.'

# 2. View supported types only
curl http://localhost:8080/test/datatypes | jq '.summary.supported_types'

# 3. View unsupported types only
curl http://localhost:8080/test/datatypes | jq '.summary.unsupported_types'

# 4. View errors only
curl http://localhost:8080/test/datatypes | jq '.errors'

# 5. Count supported types
curl http://localhost:8080/test/datatypes | jq '.summary.supported_types | length'
```

## Troubleshooting

### No Results?
- Ensure the server is running: `npm start`
- Check the endpoint: `http://localhost:8080/test/datatypes`

### Unexpected Results?
- Different OpenTelemetry SDK versions may support different types
- Check your SDK version: `npm list @opentelemetry/api`

### Traces Not Appearing?
- Ensure OpenTelemetry is configured
- Check Jaeger is running: `http://localhost:16686`
- Verify exporter configuration

## References
- [OpenTelemetry Attribute Specification](https://opentelemetry.io/docs/specs/otel/common/attribute-naming/)
- [OpenTelemetry JavaScript API](https://opentelemetry.io/docs/languages/js/)
- [Span Attributes](https://opentelemetry.io/docs/specs/otel/trace/api/#set-attributes)

---

**Endpoint**: GET `/test/datatypes`  
**Purpose**: Test OpenTelemetry span attribute data type support  
**Version**: 1.0.0

