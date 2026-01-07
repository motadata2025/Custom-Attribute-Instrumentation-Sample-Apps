using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using WebApplicationCore8.Data;
using WebApplicationCore8.Models;
using WebApplicationCore8.Util;

namespace WebApplicationCore8.Controllers
{
    [Route("api/[controller]")]
    [ApiController]
    public class ProductsController : ControllerBase
    {
        private readonly ProductDbContext _context;

        public ProductsController(ProductDbContext context)
        {
            _context = context;
        }

        // GET: api/Products        [HttpGet("test-attributes")]

        [HttpGet]
        public async Task<ActionResult<IEnumerable<Product>>> GetProducts()
        {
            // Add custom business attributes
            MotadataDynamicInstrumentation.Set("apm.operation", "list_products");
            MotadataDynamicInstrumentation.Set("apm.user_id", User?.Identity?.Name ?? "anonymous");
            MotadataDynamicInstrumentation.Set("apm.endpoint", "GetProducts");

            var products = await _context.Products.ToListAsync();

            // Add result attributes
            MotadataDynamicInstrumentation.Set("apm.result_count", products.Count);
            MotadataDynamicInstrumentation.Set("apm.result", "success");

            return products;
        }

        // GET: api/Products/5
        [HttpGet("{id}")]
        public async Task<ActionResult<Product>> GetProduct(int id)
        {
            // Add custom business attributes
            MotadataDynamicInstrumentation.Set("apm.operation", "get_product");
            MotadataDynamicInstrumentation.Set("apm.product_id", id);
            MotadataDynamicInstrumentation.Set("apm.user_id", User?.Identity?.Name ?? "anonymous");
            MotadataDynamicInstrumentation.Set("apm.endpoint", "GetProduct");

            var product = await _context.Products.FindAsync(id);

            if (product == null)
            {
                MotadataDynamicInstrumentation.Set("apm.result", "not_found");
                MotadataDynamicInstrumentation.Set("apm.error_reason", "product_not_found");
                return NotFound();
            }

            // Add product-specific attributes
            MotadataDynamicInstrumentation.Set("apm.result", "success");
            MotadataDynamicInstrumentation.Set("apm.product_name", product.Name);
            MotadataDynamicInstrumentation.Set("apm.product_price", product.Price);
            MotadataDynamicInstrumentation.Set("apm.product_available", product.IsAvailable);
            MotadataDynamicInstrumentation.Set("apm.product_quantity", product.Quantity);

            return product;
        }

        // PUT: api/Products/5
        [HttpPut("{id}")]
        public async Task<IActionResult> PutProduct(int id, Product product)
        {
            // Add custom business attributes
            MotadataDynamicInstrumentation.Set("apm.operation", "update_product");
            MotadataDynamicInstrumentation.Set("apm.product_id", id);
            MotadataDynamicInstrumentation.Set("apm.user_id", User?.Identity?.Name ?? "anonymous");
            MotadataDynamicInstrumentation.Set("apm.endpoint", "PutProduct");

            if (id != product.Id)
            {
                MotadataDynamicInstrumentation.Set("apm.result", "bad_request");
                MotadataDynamicInstrumentation.Set("apm.error_reason", "id_mismatch");
                return BadRequest();
            }

            // Add product update details
            MotadataDynamicInstrumentation.Set("apm.product_name", product.Name);
            MotadataDynamicInstrumentation.Set("apm.product_price", product.Price);
            MotadataDynamicInstrumentation.Set("apm.product_quantity", product.Quantity);

            _context.Entry(product).State = EntityState.Modified;
    
            try
            {
                await _context.SaveChangesAsync();
                MotadataDynamicInstrumentation.Set("apm.result", "success");
                MotadataDynamicInstrumentation.Set("apm.status", "updated");
            }
            catch (DbUpdateConcurrencyException ex)
            {
                if (!ProductExists(id))
                {
                    MotadataDynamicInstrumentation.Set("apm.result", "not_found");
                    MotadataDynamicInstrumentation.Set("apm.error_reason", "product_not_found");
                    return NotFound();
                }
                else
                {
                    MotadataDynamicInstrumentation.Set("apm.result", "error");
                    MotadataDynamicInstrumentation.Set("apm.error_type", "concurrency_exception");
                    MotadataDynamicInstrumentation.Set("apm.error_message", ex.Message);
                    throw;
                }
            }

            return NoContent();
        }

        // POST: api/Products
        [HttpPost]
        public async Task<ActionResult<Product>> PostProduct(Product product)
        {
            // Add custom business attributes
            MotadataDynamicInstrumentation.Set("apm.operation", "create_product");
            MotadataDynamicInstrumentation.Set("apm.user_id", User?.Identity?.Name ?? "anonymous");
            MotadataDynamicInstrumentation.Set("apm.endpoint", "PostProduct");
            MotadataDynamicInstrumentation.Set("apm.product_name", product.Name);
            MotadataDynamicInstrumentation.Set("apm.product_price", product.Price);
            MotadataDynamicInstrumentation.Set("apm.product_quantity", product.Quantity);
            MotadataDynamicInstrumentation.Set("apm.product_available", product.IsAvailable);

            _context.Products.Add(product);
            await _context.SaveChangesAsync();

            // Add result attributes
            MotadataDynamicInstrumentation.Set("apm.product_id", product.Id);
            MotadataDynamicInstrumentation.Set("apm.result", "success");
            MotadataDynamicInstrumentation.Set("apm.status", "created");

            return CreatedAtAction("GetProduct", new { id = product.Id }, product);
        }

        // DELETE: api/Products/5
        [HttpDelete("{id}")]
        public async Task<IActionResult> DeleteProduct(int id)
        {
            // Add custom business attributes
            MotadataDynamicInstrumentation.Set("apm.operation", "delete_product");
            MotadataDynamicInstrumentation.Set("apm.product_id", id);
            MotadataDynamicInstrumentation.Set("apm.user_id", User?.Identity?.Name ?? "anonymous");
            MotadataDynamicInstrumentation.Set("apm.endpoint", "DeleteProduct");

            var product = await _context.Products.FindAsync(id);
            if (product == null)
            {
                MotadataDynamicInstrumentation.Set("apm.result", "not_found");
                MotadataDynamicInstrumentation.Set("apm.error_reason", "product_not_found");
                return NotFound();
            }

            // Add product details before deletion
            MotadataDynamicInstrumentation.Set("apm.product_name", product.Name);
            MotadataDynamicInstrumentation.Set("apm.product_price", product.Price);

            _context.Products.Remove(product);
            await _context.SaveChangesAsync();

            // Add result attributes
            MotadataDynamicInstrumentation.Set("apm.result", "success");
            MotadataDynamicInstrumentation.Set("apm.status", "deleted");

            return NoContent();
        }

        // GET: api/Products/test-attributes
        [HttpGet("test-attributes")]
        public ActionResult<object> TestCustomAttributes()
        {
            // Test all data types
            bool boolValue = true;
            double doubleValue = 123.456;
            float floatValue = 789.012f;
            int intValue = 42;
            long longValue = 9876543210L;
            string stringValue = "Hello OpenTelemetry";

            bool[] boolArray = new[] { true, false, true };
            double[] doubleArray = new[] { 1.1, 2.2, 3.3 };
            float[] floatArray = new[] { 4.4f, 5.5f, 6.6f };
            int[] intArray = new[] { 10, 20, 30 };
            long[] longArray = new[] { 100L, 200L, 300L };
            string[] stringArray = new[] { "first", "second", "third" };

            // Add all data types as custom attributes
            MotadataDynamicInstrumentation.Set("apm.test.bool", boolValue);
            MotadataDynamicInstrumentation.Set("apm.test.double", doubleValue);
            MotadataDynamicInstrumentation.Set("apm.test.float", floatValue);
            MotadataDynamicInstrumentation.Set("apm.test.int", intValue);
            MotadataDynamicInstrumentation.Set("apm.test.long", longValue);
            MotadataDynamicInstrumentation.Set("apm.test.string", stringValue);

            MotadataDynamicInstrumentation.SetBoolArray("apm.test.bool_array", boolArray);
            MotadataDynamicInstrumentation.SetDoubleArray("apm.test.double_array", doubleArray);
            MotadataDynamicInstrumentation.SetFloatArray("apm.test.float_array", floatArray);
            MotadataDynamicInstrumentation.SetIntArray("apm.test.int_array", intArray);
            MotadataDynamicInstrumentation.SetLongArray("apm.test.long_array", longArray);
            MotadataDynamicInstrumentation.SetStringArray("apm.test.string_array", stringArray);

            // Return all values for verification
            return Ok(new
            {
                bool_value = boolValue,
                double_value = doubleValue,
                float_value = floatValue,
                int_value = intValue,
                long_value = longValue,
                string_value = stringValue,
                bool_array = boolArray,
                double_array = doubleArray,
                float_array = floatArray,
                int_array = intArray,
                long_array = longArray,
                string_array = stringArray,
                message = "Check the trace for all custom attributes with apm.test.* prefix"
            });
        }

        private bool ProductExists(int id)
        {
            return _context.Products.Any(e => e.Id == id);
        }
    }
}