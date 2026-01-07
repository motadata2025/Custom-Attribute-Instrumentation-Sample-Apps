using Microsoft.EntityFrameworkCore;
using WebApplicationCore9.Models;

namespace WebApplicationCore9.Data;

public class ProductDbContext : DbContext
{
    public ProductDbContext(DbContextOptions<ProductDbContext> options) : base(options) { }

    public DbSet<Product> Products { get; set; }
}

