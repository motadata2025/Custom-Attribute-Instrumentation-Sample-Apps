# .NET Product Management API - Multi-Version Demo

This repository contains two clean, production-ready RESTful API implementations for product inventory management, built with different versions of .NET to demonstrate framework evolution and best practices.

## 📁 Repository Structure

```
DotNet Custom Attribute/
├── Core/
│   ├── WebApplicationCore8/     # .NET 8.0 Implementation
│   │   ├── README.md            # Detailed documentation
│   │   └── WebApplicationCore8/
│   │       ├── Controllers/
│   │       ├── Models/
│   │       ├── Data/
│   │       └── Program.cs
│   │
│   └── WebApplicationCore9/     # .NET 9.0 Implementation
│       ├── README.md            # Detailed documentation
│       └── WebApplicationCore9/
│           ├── Controllers/
│           ├── Models/
│           ├── Data/
│           ├── Migrations/
│           └── Program.cs
│
└── README.md                    # This file
```

## 🎯 Projects Overview

### WebApplicationCore8 (.NET 8.0)
A stable, production-ready API built with .NET 8.0 LTS (Long-Term Support).

**Key Features:**
- ✅ ASP.NET Core 8.0 Web API
- ✅ Entity Framework Core 8.0
- ✅ PostgreSQL database integration
- ✅ Full CRUD operations
- ✅ Swagger/OpenAPI documentation
- ✅ MVC architecture pattern
- ✅ Manual database migrations

**Port:** `http://localhost:5035`  
**Documentation:** [WebApplicationCore8/README.md](Core/WebApplicationCore8/README.md)

---

### WebApplicationCore9 (.NET 9.0)
A modern API showcasing the latest .NET 9.0 features and improvements.

**Key Features:**
- ✅ ASP.NET Core 9.0 Web API
- ✅ Entity Framework Core 9.0
- ✅ PostgreSQL database integration
- ✅ Full CRUD operations
- ✅ Swagger/OpenAPI documentation
- ✅ MVC architecture pattern
- ✅ **Automatic database migrations on startup**
- ✅ Enhanced performance and features

**Port:** `http://localhost:5255`  
**Documentation:** [WebApplicationCore9/README.md](Core/WebApplicationCore9/README.md)

## 🚀 Quick Start

### Prerequisites

- [.NET 8.0 SDK](https://dotnet.microsoft.com/download/dotnet/8.0) (for WebApplicationCore8)
- [.NET 9.0 SDK](https://dotnet.microsoft.com/download/dotnet/9.0) (for WebApplicationCore9)
- [PostgreSQL](https://www.postgresql.org/download/) (version 12+)
- Code editor (Visual Studio, VS Code, or Rider)

### Database Setup

Both applications use the same PostgreSQL database. Create it once:

```sql
CREATE DATABASE productdb;
```

### Running WebApplicationCore8

```bash
cd Core/WebApplicationCore8/WebApplicationCore8
dotnet restore
dotnet ef database update
dotnet run
```

Access at: `http://localhost:5035/swagger`

### Running WebApplicationCore9

```bash
cd Core/WebApplicationCore9/WebApplicationCore9
dotnet restore
dotnet run  # Migrations applied automatically
```

Access at: `http://localhost:5255/swagger`

## 📊 Feature Comparison

| Feature | WebApplicationCore8 | WebApplicationCore9 |
|---------|---------------------|---------------------|
| **Framework** | .NET 8.0 LTS | .NET 9.0 |
| **EF Core** | 8.0 | 9.0 |
| **Npgsql** | 8.0 | 9.0 |
| **Swagger** | 6.6.2 | 6.7.1 |
| **Auto Migrations** | ❌ Manual | ✅ Automatic |
| **Performance** | Excellent | Enhanced |
| **Support** | LTS (until Nov 2026) | STS (until May 2025) |
| **Port** | 5035 | 5255 |
| **Architecture** | MVC | MVC |
| **Database** | PostgreSQL | PostgreSQL |

## 🏗️ Architecture

Both applications follow the same clean architecture pattern:

```
┌─────────────────────────────────────┐
│         Controllers Layer           │
│  (API Endpoints & HTTP Handling)    │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│          Models Layer                │
│     (Business Entities)              │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│          Data Layer                  │
│  (EF Core DbContext & Database)      │
└─────────────────────────────────────┘
```

### Shared Components

**Product Model:**
```csharp
public class Product
{
    public int Id { get; set; }
    public string Name { get; set; }
    public bool IsAvailable { get; set; }
    public double Price { get; set; }
    public float Weight { get; set; }
    public int Quantity { get; set; }
    public long Barcode { get; set; }
    public float Discount { get; set; }
    public bool[] Flags { get; set; }
    public double[] Dimensions { get; set; }
    public float[] Ratings { get; set; }
    public int[] Serials { get; set; }
    public long[] Categories { get; set; }
    public string[] Tags { get; set; }
}
```

**API Endpoints (Both Projects):**
- `GET /api/products` - List all products
- `GET /api/products/{id}` - Get specific product
- `POST /api/products` - Create new product
- `PUT /api/products/{id}` - Update product
- `DELETE /api/products/{id}` - Delete product

## 🧪 Testing Both Applications

### Test Script (Bash/Linux/Mac)

```bash
#!/bin/bash

# Test WebApplicationCore8
echo "Testing WebApplicationCore8..."
curl http://localhost:5035/api/products

# Test WebApplicationCore9
echo "Testing WebApplicationCore9..."
curl http://localhost:5255/api/products

# Create product in Core8
curl -X POST http://localhost:5035/api/products \
  -H "Content-Type: application/json" \
  -d '{"name":"Test Product","isAvailable":true,"price":99.99,"weight":1.0,"quantity":10,"barcode":1111111111111,"discount":0.0,"flags":[true],"dimensions":[10,20,30],"ratings":[5.0],"serials":[1000],"categories":[100],"tags":["test"]}'

# Create product in Core9
curl -X POST http://localhost:5255/api/products \
  -H "Content-Type: application/json" \
  -d '{"name":"Test Product","isAvailable":true,"price":99.99,"weight":1.0,"quantity":10,"barcode":1111111111111,"discount":0.0,"flags":[true],"dimensions":[10,20,30],"ratings":[5.0],"serials":[1000],"categories":[100],"tags":["test"]}'
```

### Using Swagger UI

- **WebApplicationCore8**: http://localhost:5035/swagger
- **WebApplicationCore9**: http://localhost:5255/swagger

## 🛠️ Technology Stack

### Common Technologies
- **Language**: C# 12
- **Database**: PostgreSQL
- **ORM**: Entity Framework Core
- **API Documentation**: Swagger/OpenAPI
- **Architecture**: MVC Pattern

### Version-Specific
| Technology | Core8 | Core9 |
|-----------|-------|-------|
| ASP.NET Core | 8.0 | 9.0 |
| EF Core | 8.0 | 9.0 |
| Npgsql | 8.0.0 | 9.0.0 |

## 📝 Configuration

Both applications use the same configuration structure in `appsettings.json`:

```json
{
  "ConnectionStrings": {
    "DefaultConnection": "Host=localhost;Port=5432;Database=productdb;Username=postgres;Password=postgres"
  },
  "Logging": {
    "LogLevel": {
      "Default": "Information",
      "Microsoft.AspNetCore": "Warning"
    }
  }
}
```

## 🔐 Security Best Practices

Both applications implement:
- ✅ Parameterized queries (via EF Core)
- ✅ Input validation
- ✅ HTTPS support (configurable)
- ✅ CORS configuration
- ✅ Proper error handling

**For Production:**
- Use environment variables for connection strings
- Enable HTTPS
- Implement authentication/authorization
- Use Azure Key Vault or similar for secrets
- Enable rate limiting
- Add logging and monitoring

## 📚 Learning Resources

### .NET 8.0
- [Official Documentation](https://learn.microsoft.com/en-us/aspnet/core/release-notes/aspnetcore-8.0)
- [What's New in .NET 8](https://learn.microsoft.com/en-us/dotnet/core/whats-new/dotnet-8)

### .NET 9.0
- [Official Documentation](https://learn.microsoft.com/en-us/aspnet/core/release-notes/aspnetcore-9.0)
- [What's New in .NET 9](https://learn.microsoft.com/en-us/dotnet/core/whats-new/dotnet-9)

### Entity Framework Core
- [EF Core Documentation](https://learn.microsoft.com/en-us/ef/core/)
- [Migrations Overview](https://learn.microsoft.com/en-us/ef/core/managing-schemas/migrations/)

## 🐛 Troubleshooting

### Common Issues

**1. Database Connection Failed**
- Verify PostgreSQL is running
- Check connection string in `appsettings.json`
- Ensure database exists

**2. Port Already in Use**
- Change port in `Properties/launchSettings.json`
- Or stop the conflicting application

**3. Migration Issues**
- For Core8: Run `dotnet ef database update`
- For Core9: Restart application (auto-migration)
- Check database permissions

**4. Build Errors**
- Ensure correct .NET SDK is installed
- Run `dotnet restore`
- Clean and rebuild: `dotnet clean && dotnet build`

## 🎓 Use Cases

These applications are perfect for:
- ✅ Learning .NET Web API development
- ✅ Understanding EF Core and database integration
- ✅ Comparing .NET versions
- ✅ API design and RESTful principles
- ✅ Starting point for production applications
- ✅ Teaching/training purposes

## 📄 License

This project is provided as-is for educational and demonstration purposes.

## 🤝 Contributing

Feel free to use these projects as templates for your own applications. Both implementations follow .NET best practices and clean code principles.

## 📞 Support

For detailed information about each project, refer to their individual README files:
- [WebApplicationCore8 Documentation](Core/WebApplicationCore8/README.md)
- [WebApplicationCore9 Documentation](Core/WebApplicationCore9/README.md)

---

**Built with ❤️ using .NET 8.0 and .NET 9.0**

