# Custom ActivitySource Implementation for OpenTelemetry

This implementation demonstrates **Technique #3: Custom ActivitySource with Additional Sources Configuration** for adding custom attributes and business logic spans to your .NET application using OpenTelemetry zero-code instrumentation.

## What Was Implemented

### 1. **AppTelemetry Class** (`Telemetry/AppTelemetry.cs`)

A centralized telemetry configuration class that provides:
- Static `ActivitySource` instance named `"WebApplicationCore9.Business"`
- Reusable across the entire application
- Single source of truth for custom span creation

### 2. **Enhanced ProductsController** (`Controllers/ProductsController.cs`)

All CRUD operations now include custom business logic spans with rich attributes:

#### **GET /api/Products** - List all products
- Span name: `GetAllProducts`
- Attributes: operation type, entity name, product count, status

#### **GET /api/Products/{id}** - Get single product
- Span name: `GetProductById`
- Attributes: product ID, name, price, quantity, availability, status

#### **POST /api/Products** - Create product
- Span name: `CreateProduct`
- Attributes: product details (name, price, quantity, weight, discount, tags, categories), generated ID, status

#### **PUT /api/Products/{id}** - Update product
- Span name: `UpdateProduct`
- Attributes: product ID, updated details, status, error handling for concurrency

#### **DELETE /api/Products/{id}** - Delete product
- Span name: `DeleteProduct`
- Attributes: product ID, name, price, deletion status

### 3. **Environment Configuration Scripts**

- `setup-otel-linux.sh` - For Linux/macOS
- `setup-otel-windows.ps1` - For Windows PowerShell
- `setup-otel-windows.cmd` - For Windows Command Prompt

## How to Use

### Step 1: Set Environment Variable

The custom ActivitySource must be registered with OpenTelemetry auto-instrumentation.

**Linux/macOS:**
```bash
source ./setup-otel-linux.sh
```

Or manually:
```bash
export OTEL_DOTNET_AUTO_TRACES_ADDITIONAL_SOURCES="WebApplicationCore9.Business"
```

**Windows PowerShell:**
```powershell
.\setup-otel-windows.ps1
```

Or manually:
```powershell
$env:OTEL_DOTNET_AUTO_TRACES_ADDITIONAL_SOURCES="WebApplicationCore9.Business"
```

**Windows Command Prompt:**
```cmd
setup-otel-windows.cmd
```

Or manually:
```cmd
set OTEL_DOTNET_AUTO_TRACES_ADDITIONAL_SOURCES=WebApplicationCore9.Business
```

### Step 2: Run the Application

```bash
dotnet run --project WebApplicationCore9/WebApplicationCore9.csproj
```

### Step 3: Test the Endpoints

The custom spans will be created automatically for all API calls:

```bash
# Create a product
curl -X POST http://localhost:5255/api/Products \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Product",
    "price": 99.99,
    "quantity": 10,
    "isAvailable": true,
    "weight": 1.5,
    "discount": 0.1,
    "barcode": 1234567890,
    "flags": [true, false],
    "dimensions": [10.0, 20.0, 30.0],
    "ratings": [4.5, 4.8],
    "serials": [1001, 1002],
    "categories": [101, 102],
    "tags": ["electronics", "new"]
  }'

# Get all products
curl http://localhost:5255/api/Products

# Get single product
curl http://localhost:5255/api/Products/1
```

## Key Benefits

✅ **Full control over span creation** - Create spans exactly where needed in business logic
✅ **Measures specific operation duration** - Each business operation has its own span
✅ **Creates child spans within the same trace** - Maintains trace context automatically
✅ **Works with zero-code instrumentation** - No need to manually configure OpenTelemetry SDK
✅ **Rich business context** - Custom attributes provide business-specific insights

## Custom Attributes Added

All spans include:
- `business.operation` - Type of operation (create, update, delete, get, list)
- `business.entity` - Entity type (Product)
- `business.status` - Operation status (success, error, not_found, bad_request)
- `business.product_*` - Product-specific attributes (id, name, price, quantity, etc.)
- `business.error` - Error messages when operations fail

## Viewing Traces

When connected to an OpenTelemetry collector and trace backend (like Jaeger, Zipkin, or Application Insights), you'll see:

1. **HTTP request span** (auto-instrumented by OpenTelemetry)
   - Child: **Custom business logic span** (your ActivitySource)
     - Child: **Database operation span** (auto-instrumented)

All spans share the same trace ID, making it easy to correlate business operations with infrastructure metrics.

