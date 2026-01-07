# WebApplicationCore8 - Product Management API

A clean and simple RESTful API built with **ASP.NET Core 8.0** for managing product inventory. This application demonstrates modern .NET development practices with Entity Framework Core and PostgreSQL integration.

## 🚀 Features

- **Full CRUD Operations** - Create, Read, Update, and Delete products
- **RESTful API** - Clean and intuitive API endpoints
- **Entity Framework Core** - Code-first database approach with migrations
- **PostgreSQL Database** - Robust relational database integration
- **Swagger/OpenAPI** - Interactive API documentation and testing
- **MVC Architecture** - Proper separation of concerns with Controllers, Models, and Data layers

## 📋 Prerequisites

- [.NET 8.0 SDK](https://dotnet.microsoft.com/download/dotnet/8.0)
- [PostgreSQL](https://www.postgresql.org/download/) (version 12 or higher)
- A code editor (Visual Studio, VS Code, or Rider)

## 🏗️ Project Structure

```
WebApplicationCore8/
├── Controllers/
│   └── ProductsController.cs    # API endpoints for product operations
├── Models/
│   └── Product.cs                # Product entity model
├── Data/
│   └── ProductDbContext.cs       # EF Core database context
├── Program.cs                    # Application entry point and configuration
├── appsettings.json              # Application configuration
└── WebApplicationCore8.csproj    # Project dependencies
```

## 🔧 Configuration

### Database Connection

Update the connection string in `appsettings.json`:

```json
{
  "ConnectionStrings": {
    "DefaultConnection": "Host=localhost;Port=5432;Database=productdb;Username=postgres;Password=postgres"
  }
}
```

**Connection String Parameters:**
- `Host`: PostgreSQL server address (default: localhost)
- `Port`: PostgreSQL port (default: 5432)
- `Database`: Database name (default: productdb)
- `Username`: PostgreSQL username
- `Password`: PostgreSQL password

## 📦 Installation & Setup

### 1. Clone the Repository

```bash
cd Core/WebApplicationCore8
```

### 2. Install Dependencies

```bash
dotnet restore
```

### 3. Setup PostgreSQL Database

Create the database in PostgreSQL:

```sql
CREATE DATABASE productdb;
```

### 4. Apply Database Migrations

```bash
dotnet ef database update
```

### 5. Build the Project

```bash
dotnet build
```

### 6. Run the Application

```bash
dotnet run
```

The application will start on:
- **HTTP**: `http://localhost:5035`
- **Swagger UI**: `http://localhost:5035/swagger`

## 📚 API Endpoints

### Base URL: `/api/products`

| Method | Endpoint | Description | Request Body |
|--------|----------|-------------|--------------|
| GET | `/api/products` | Get all products | - |
| GET | `/api/products/{id}` | Get product by ID | - |
| POST | `/api/products` | Create new product | Product JSON |
| PUT | `/api/products/{id}` | Update existing product | Product JSON |
| DELETE | `/api/products/{id}` | Delete product | - |

### Product Model

```json
{
  "id": 0,
  "name": "string",
  "isAvailable": true,
  "price": 0.0,
  "weight": 0.0,
  "quantity": 0,
  "barcode": 0,
  "discount": 0.0,
  "flags": [true, false],
  "dimensions": [0.0, 0.0, 0.0],
  "ratings": [0.0],
  "serials": [0],
  "categories": [0],
  "tags": ["string"]
}
```

## 🧪 Testing the API

### Using cURL

**Get all products:**
```bash
curl http://localhost:5035/api/products
```

**Get product by ID:**
```bash
curl http://localhost:5035/api/products/1
```

**Create a new product:**
```bash
curl -X POST http://localhost:5035/api/products \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Laptop Pro",
    "isAvailable": true,
    "price": 1499.99,
    "weight": 1.8,
    "quantity": 50,
    "barcode": 1234567890123,
    "discount": 0.1,
    "flags": [true, false],
    "dimensions": [35.79, 24.59, 1.55],
    "ratings": [4.5, 4.8],
    "serials": [1001, 1002],
    "categories": [101, 202],
    "tags": ["electronics", "computer"]
  }'
```

**Update a product:**
```bash
curl -X PUT http://localhost:5035/api/products/1 \
  -H "Content-Type: application/json" \
  -d '{
    "id": 1,
    "name": "Updated Product",
    "isAvailable": true,
    "price": 999.99,
    ...
  }'
```

**Delete a product:**
```bash
curl -X DELETE http://localhost:5035/api/products/1
```

### Using Swagger UI

Navigate to `http://localhost:5035/swagger` for interactive API documentation and testing.

## 🛠️ Technologies Used

- **ASP.NET Core 8.0** - Web framework
- **Entity Framework Core 8.0** - ORM for database operations
- **Npgsql.EntityFrameworkCore.PostgreSQL 8.0** - PostgreSQL provider
- **Swashbuckle.AspNetCore 6.6.2** - Swagger/OpenAPI documentation
- **PostgreSQL** - Relational database

## 📝 Development

### Adding New Migrations

After modifying the `Product` model:

```bash
dotnet ef migrations add MigrationName
dotnet ef database update
```

### Removing Last Migration

```bash
dotnet ef migrations remove
```

## 🐛 Troubleshooting

### Database Connection Issues

1. Ensure PostgreSQL is running:
   ```bash
   sudo systemctl status postgresql  # Linux
   # or check Windows Services for PostgreSQL
   ```

2. Verify connection string in `appsettings.json`
3. Check PostgreSQL logs for authentication errors

### Port Already in Use

If port 5035 is already in use, modify `Properties/launchSettings.json`:

```json
{
  "applicationUrl": "http://localhost:YOUR_PORT"
}
```

## 📄 License

This project is part of a demonstration/learning repository.

## 👥 Contributing

This is a clean, simple .NET application template. Feel free to use it as a starting point for your projects.

