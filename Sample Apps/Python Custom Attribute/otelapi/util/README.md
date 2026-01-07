# MotadataDynamicInstrumentation Utility Class

> **Type-safe, null-safe utility for adding custom attributes to OpenTelemetry spans**

## Overview

`MotadataDynamicInstrumentation` is a static utility class that provides a safe and convenient way to add custom business attributes to the current OpenTelemetry span. It automatically handles:

- ✅ **Automatic prefixing** - Adds `apm.` prefix to all attribute keys
- ✅ **Null safety** - Silently ignores null keys and values
- ✅ **Type safety** - Supports all OpenTelemetry attribute types
- ✅ **Error suppression** - Never throws exceptions, ensuring application stability
- ✅ **Span validation** - Checks if span is recording before setting attributes

## Why Use This Utility?

### Without Utility (Manual Approach)

```python
from opentelemetry import trace

def process_order(order_id, total):
    span = trace.get_current_span()

    # Manual null checks
    if span and span.is_recording():
        # Manual prefixing
        if order_id is not None:
            span.set_attribute("apm.order.id", order_id)
        if total is not None:
            span.set_attribute("apm.order.total", total)

    # Business logic...
```

### With Utility (Recommended)

```python
from otelapi.util.MotadataDynamicInstrumentation import MotadataDynamicInstrumentation

def process_order(order_id, total):
    # Clean, safe, automatic
    MotadataDynamicInstrumentation.set("order.id", order_id)
    MotadataDynamicInstrumentation.set("order.total", total)

    # Business logic...
```

## Installation

The utility class is included in the `otelapi/util/` directory. Simply import it:

```python
from otelapi.util.MotadataDynamicInstrumentation import MotadataDynamicInstrumentation
```

## API Reference

### Scalar Value Methods

#### `set(key: str, value: Optional[bool | int | float | str]) -> None`

Sets a scalar attribute on the current span.

**Parameters:**
- `key` (str): Attribute key (will be prefixed with `apm.` if not already)
- `value` (bool | int | float | str): Attribute value

**Example:**
```python
MotadataDynamicInstrumentation.set("user.id", "12345")           # String
MotadataDynamicInstrumentation.set("user.age", 30)               # Integer
MotadataDynamicInstrumentation.set("order.total", 99.99)         # Float
MotadataDynamicInstrumentation.set("user.is_premium", True)      # Boolean
```

**Result in Jaeger:**
```
apm.user.id = "12345"
apm.user.age = 30
apm.order.total = 99.99
apm.user.is_premium = true
```

### List Value Methods

#### `set_bool_list(key: str, value: Optional[Sequence[bool]]) -> None`

Sets a boolean list attribute.

**Example:**
```python
MotadataDynamicInstrumentation.set_bool_list("features.enabled", [True, False, True])
```

#### `set_int_list(key: str, value: Optional[Sequence[int]]) -> None`

Sets an integer list attribute.

**Example:**
```python
MotadataDynamicInstrumentation.set_int_list("order.item_ids", [101, 102, 103])
```

#### `set_float_list(key: str, value: Optional[Sequence[float]]) -> None`

Sets a float list attribute.

**Example:**
```python
MotadataDynamicInstrumentation.set_float_list("order.prices", [19.99, 29.99, 9.99])
```

#### `set_string_list(key: str, value: Optional[Sequence[str]]) -> None`

Sets a string list attribute.

**Example:**
```python
MotadataDynamicInstrumentation.set_string_list("order.items", ["Laptop", "Mouse", "Keyboard"])
```

## Usage Examples

### Basic Usage

```python
from otelapi.util.MotadataDynamicInstrumentation import MotadataDynamicInstrumentation

def create_user(username, email, age):
    # Add custom attributes
    MotadataDynamicInstrumentation.set("operation", "create_user")
    MotadataDynamicInstrumentation.set("user.username", username)
    MotadataDynamicInstrumentation.set("user.email", email)
    MotadataDynamicInstrumentation.set("user.age", age)

    # Business logic
    user = User.create(username, email, age)

    # Add result attributes
    MotadataDynamicInstrumentation.set("user.created", True)
    MotadataDynamicInstrumentation.set("user.id", user.id)

    return user
```

### Advanced Usage with Lists

```python
def process_order(order_data):
    MotadataDynamicInstrumentation.set("order.id", order_data["id"])
    MotadataDynamicInstrumentation.set("order.total", order_data["total"])

    # Add list of item names
    item_names = [item["name"] for item in order_data["items"]]
    MotadataDynamicInstrumentation.set_string_list("order.item_names", item_names)

    # Add list of item prices
    item_prices = [item["price"] for item in order_data["items"]]
    MotadataDynamicInstrumentation.set_float_list("order.item_prices", item_prices)

    # Business logic...
```

### Null Safety Example

```python
def get_user(username):
    # These will be safely ignored if None
    MotadataDynamicInstrumentation.set("user.username", username)  # OK if None

    user = User.get_by_username(username)

    # Safe even if user is None
    MotadataDynamicInstrumentation.set("user.email", user.email if user else None)
    MotadataDynamicInstrumentation.set("user.found", user is not None)
```

## How It Works Internally

### Automatic Prefixing

Every attribute key is automatically prefixed with `apm.` if not already present:

```python
# Input
MotadataDynamicInstrumentation.set("user.id", "123")

# Internal processing
final_key = "apm.user.id"  # Prefix added automatically

# Result in trace
apm.user.id = "123"
```

### Null Safety

The utility performs multiple null checks to ensure safety:

```python
# Simplified internal logic
@staticmethod
def set(key: str, value: any) -> None:
    # 1. Check for None
    if key is None or value is None:
        return  # Silently ignore

    # 2. Add prefix
    prefixed = _add_prefix(key)

    # 3. Try to set attribute
    try:
        span = trace.get_current_span()
        if span.is_recording():
            span.set_attribute(prefixed, value)
    except Exception:
        pass  # Silently ignore all errors
```

## Best Practices

### ✅ DO

```python
# Use descriptive attribute names
MotadataDynamicInstrumentation.set("user.id", user_id)
MotadataDynamicInstrumentation.set("order.total", total)

# Add attributes at relevant points in your code
def process_payment(amount):
    MotadataDynamicInstrumentation.set("payment.amount", amount)
    result = payment_gateway.charge(amount)
    MotadataDynamicInstrumentation.set("payment.status", result.status)

# Use appropriate list methods for collections
MotadataDynamicInstrumentation.set_string_list("order.items", item_names)
```

### ❌ DON'T

```python
# Don't manually add the 'apm.' prefix (it's automatic)
MotadataDynamicInstrumentation.set("apm.user.id", user_id)  # Redundant

# Don't worry about null checks (handled internally)
if user_id is not None:  # Unnecessary
    MotadataDynamicInstrumentation.set("user.id", user_id)

# Don't use generic attribute names
MotadataDynamicInstrumentation.set("id", user_id)  # Too generic
```

## Supported Data Types

| Python Type | Method | OpenTelemetry Type | Example |
|-------------|--------|-------------------|---------|
| `str` | `set()` | String | `"john_doe"` |
| `int` | `set()` | Integer (Long) | `42` |
| `float` | `set()` | Double | `99.99` |
| `bool` | `set()` | Boolean | `True` |
| `Sequence[str]` | `set_string_list()` | String Array | `["a", "b", "c"]` |
| `Sequence[int]` | `set_int_list()` | Integer Array | `[1, 2, 3]` |
| `Sequence[float]` | `set_float_list()` | Double Array | `[1.1, 2.2, 3.3]` |
| `Sequence[bool]` | `set_bool_list()` | Boolean Array | `[True, False]` |

## Troubleshooting

### Attributes Not Appearing in Jaeger

**Problem:** Attributes set with the utility don't appear in traces.

**Solutions:**

1. **Verify span is recording:**
   ```python
   from opentelemetry import trace

   span = trace.get_current_span()
   print(f"Span recording: {span.is_recording()}")  # Should be True
   ```

2. **Check if auto-instrumentation is enabled:**
   ```python
   # In otel_config.py
   FlaskInstrumentor().instrument_app(app)  # Must be called
   ```

3. **Verify Jaeger is receiving traces:**
   ```bash
   docker logs jaeger
   ```

## Related Documentation

- [otelapi/README.md](../README.md) - Method 2: API-Based implementation
- [../../README.md](../../README.md) - Main repository README
- [OpenTelemetry Python API](https://opentelemetry-python.readthedocs.io/en/latest/api/trace.html)

---

**This utility is production-ready and used in the Method 2 (API-Based) implementation.**
    item_names = [item["name"] for item in order_data["items"]]
    MotadataDynamicInstrumentation.set_string_list("order.item_names", item_names)

    # Add list of item prices
    item_prices = [item["price"] for item in order_data["items"]]
    MotadataDynamicInstrumentation.set_float_list("order.item_prices", item_prices)

    # Business logic...
```

