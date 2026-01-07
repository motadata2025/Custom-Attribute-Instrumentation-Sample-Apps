namespace WebApplicationCore8.Models;

public class Product
{
    public int Id { get; set; }
    public string Name { get; set; } = string.Empty;
    public bool IsAvailable { get; set; }
    public double Price { get; set; }
    public float Weight { get; set; }
    public int Quantity { get; set; }
    public long Barcode { get; set; }
    public float Discount { get; set; }
    public bool[] Flags { get; set; } = [];
    public double[] Dimensions { get; set; } = [];
    public float[] Ratings { get; set; } = [];
    public int[] Serials { get; set; } = [];
    public long[] Categories { get; set; } = [];
    public string[] Tags { get; set; } = [];
}