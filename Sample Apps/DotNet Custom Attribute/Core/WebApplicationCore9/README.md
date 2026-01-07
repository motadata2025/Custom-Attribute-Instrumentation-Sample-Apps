# WebApplicationCore9 - Product Management API

A modern RESTful API built with **ASP.NET Core 9.0** for managing product inventory. This application showcases the latest .NET features with Entity Framework Core and PostgreSQL integration, including automatic database migrations on startup.

## 🚀 Features

- **Full CRUD Operations** - Create, Read, Update, and Delete products
- **RESTful API** - Clean and intuitive API endpoints
- **Entity Framework Core 9.0** - Latest ORM with improved performance
- **PostgreSQL Database** - Robust relational database integration
- **Auto Migrations** - Database migrations applied automatically on startup
- **Swagger/OpenAPI** - Interactive API documentation and testing
- **MVC Architecture** - Proper separation of concerns with Controllers, Models, and Data layers
- **.NET 9.0** - Built with the latest .NET framework

## 📋 Prerequisites

- [.NET 9.0 SDK](https://dotnet.microsoft.com/download/dotnet/9.0)
- [PostgreSQL](https://www.postgresql.org/download/) (version 12 or higher)
- A code editor (Visual Studio, VS Code, or Rider)

## 🏗️ Project Structure

```
WebApplicationCore9/
├── Controllers/
│   └── ProductsController.cs    # API endpoints for product operations
├── Models/
│   └── Product.cs                # Product entity model
├── Data/
│   └── ProductDbContext.cs       # EF Core database context
├── Migrations/                   # EF Core migration files
│   ├── 20240725120000_InitialCreate.cs
│   └── ProductDbContextModelSnapshot.cs
├── Program.cs                    # Application entry point and configuration
├── appsettings.json              # Application configuration
└── WebApplicationCore9.csproj    # Project dependencies
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
cd Core/WebApplicationCore9
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

**Note:** Unlike WebApplicationCore8, this application automatically applies migrations on startup, so you don't need to run `dotnet ef database update` manually.

### 4. Build the Project

```bash
dotnet build
```

### 5. Run the Application

```bash
dotnet run
```

The application will:
1. Start up
2. Automatically apply any pending database migrations
3. Begin listening for requests

**Application URLs:**
- **HTTP**: `http://localhost:5255`
- **Swagger UI**: `http://localhost:5255/swagger`

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
curl http://localhost:5255/api/products
```

**Get product by ID:**
```bash
curl http://localhost:5255/api/products/1
```

**Create a new product:**
```bash
curl -X POST http://localhost:5255/api/products \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Gaming Laptop",
    "isAvailable": true,
    "price": 1999.99,
    "weight": 2.5,
    "quantity": 25,
    "barcode": 9876543210987,
    "discount": 0.15,
    "flags": [true, true],
    "dimensions": [40.0, 28.0, 2.0],
    "ratings": [4.8, 4.9, 5.0],
    "serials": [5001, 5002, 5003],
    "categories": [101, 202, 303],
    "tags": ["electronics", "gaming", "laptop"]
  }'
```

**Update a product:**
```bash
curl -X PUT http://localhost:5255/api/products/1 \
  -H "Content-Type: application/json" \
  -d '{
    "id": 1,
    "name": "Updated Gaming Laptop",
    "isAvailable": true,
    "price": 1799.99,
    ...
  }'
```

**Delete a product:**
```bash
curl -X DELETE http://localhost:5255/api/products/1
```

### Using Swagger UI

Navigate to `http://localhost:5255/swagger` for interactive API documentation and testing.

## 🛠️ Technologies Used

- **ASP.NET Core 9.0** - Latest web framework with improved performance
- **Entity Framework Core 9.0** - Modern ORM with enhanced features
- **Npgsql.EntityFrameworkCore.PostgreSQL 9.0** - PostgreSQL provider for EF Core
- **Swashbuckle.AspNetCore 6.7.1** - Swagger/OpenAPI documentation
- **PostgreSQL** - Relational database

## ✨ What's New in .NET 9

This project leverages .NET 9 features:
- **Improved Performance** - Faster startup and runtime performance
- **Enhanced EF Core** - Better query performance and new features
- **Modern C# Features** - Latest C# language improvements
- **Better Diagnostics** - Improved logging and debugging capabilities

## 📝 Development

### Adding New Migrations

After modifying the `Product` model:

```bash
dotnet ef migrations add MigrationName
```

The migration will be automatically applied on next application startup.

### Manually Applying Migrations

If you prefer manual migration:

```bash
dotnet ef database update
```

### Removing Last Migration

```bash
dotnet ef migrations remove
```

### Viewing Migration SQL

```bash
dotnet ef migrations script
```

## 🔄 Auto-Migration Feature

This application includes automatic database migration on startup. The following code in `Program.cs` handles this:

```csharp
using (var scope = app.Services.CreateScope())
{
    var db = scope.ServiceProvider.GetRequiredService<ProductDbContext>();
    db.Database.Migrate();
}
```

**Benefits:**
- No manual migration commands needed
- Ensures database is always up-to-date
- Simplifies deployment process
- Great for development and testing environments

**Production Consideration:** For production environments, consider using manual migrations or migration scripts for better control.

## 🐛 Troubleshooting

### Database Connection Issues

1. Ensure PostgreSQL is running:
   ```bash
   sudo systemctl status postgresql  # Linux
   # or check Windows Services for PostgreSQL
   ```

2. Verify connection string in `appsettings.json`
3. Check PostgreSQL logs for authentication errors
4. Ensure the database exists (create it if needed)

### Migration Issues

If auto-migration fails:
1. Check database permissions
2. Verify connection string
3. Try manual migration: `dotnet ef database update`
4. Check migration files in `Migrations/` folder

### Port Already in Use

If port 5255 is already in use, modify `Properties/launchSettings.json`:

```json
{
  "applicationUrl": "http://localhost:YOUR_PORT"
}
```

## 🔐 Security Notes

- **Production Deployment**: Never commit connection strings with real credentials
- Use **User Secrets** for development: `dotnet user-secrets set "ConnectionStrings:DefaultConnection" "your-connection-string"`
- Use **Environment Variables** or **Azure Key Vault** for production
- Enable **HTTPS** in production environments

## 📄 License

This project is part of a demonstration/learning repository.

## 👥 Contributing

This is a modern .NET 9 application template. Feel free to use it as a starting point for your projects.

## 🆚 Comparison with WebApplicationCore8

| Feature | WebApplicationCore8 | WebApplicationCore9 |
|---------|---------------------|---------------------|
| .NET Version | 8.0 | 9.0 |
| EF Core Version | 8.0 | 9.0 |
| Auto Migrations | ❌ Manual | ✅ Automatic |
| Performance | Fast | Faster |
| Port | 5035 | 5255 |

Both applications share the same clean architecture and API design, with WebApplicationCore9 showcasing the latest .NET features.

