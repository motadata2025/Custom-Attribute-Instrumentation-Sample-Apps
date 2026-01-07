package OtelApiTracerProvider.model;

import java.sql.Timestamp;

/**
 * Order model for the OtelApiTracerProvider demo.
 * Maps to the orders table in PostgreSQL.
 */
public class Order {
    private String orderId;
    private String customerId;
    private double total;
    private String currency;
    private String status;
    private String paymentId;
    private String paymentMethod;
    private String trackingNumber;
    private String carrier;
    private String shippingMethod;
    private Timestamp createdAt;
    private Timestamp updatedAt;

    public Order() {}

    // Simple constructor for basic order creation
    public Order(String orderId, double total, String customerId,
                 String paymentId, String trackingNumber, String status) {
        this.orderId = orderId;
        this.total = total;
        this.customerId = customerId;
        this.paymentId = paymentId;
        this.trackingNumber = trackingNumber;
        this.status = status;
        this.currency = "USD";
    }

    // Full constructor matching database schema
    public Order(String orderId, String customerId, double total, String currency,
                 String status, String paymentId, String paymentMethod,
                 String trackingNumber, String carrier, String shippingMethod,
                 Timestamp createdAt, Timestamp updatedAt) {
        this.orderId = orderId;
        this.customerId = customerId;
        this.total = total;
        this.currency = currency;
        this.status = status;
        this.paymentId = paymentId;
        this.paymentMethod = paymentMethod;
        this.trackingNumber = trackingNumber;
        this.carrier = carrier;
        this.shippingMethod = shippingMethod;
        this.createdAt = createdAt;
        this.updatedAt = updatedAt;
    }

    // Getters and Setters
    public String getOrderId() { return orderId; }
    public void setOrderId(String orderId) { this.orderId = orderId; }

    public String getCustomerId() { return customerId; }
    public void setCustomerId(String customerId) { this.customerId = customerId; }

    public double getTotal() { return total; }
    public void setTotal(double total) { this.total = total; }

    public String getCurrency() { return currency; }
    public void setCurrency(String currency) { this.currency = currency; }

    public String getStatus() { return status; }
    public void setStatus(String status) { this.status = status; }

    public String getPaymentId() { return paymentId; }
    public void setPaymentId(String paymentId) { this.paymentId = paymentId; }

    public String getPaymentMethod() { return paymentMethod; }
    public void setPaymentMethod(String paymentMethod) { this.paymentMethod = paymentMethod; }

    public String getTrackingNumber() { return trackingNumber; }
    public void setTrackingNumber(String trackingNumber) { this.trackingNumber = trackingNumber; }

    public String getCarrier() { return carrier; }
    public void setCarrier(String carrier) { this.carrier = carrier; }

    public String getShippingMethod() { return shippingMethod; }
    public void setShippingMethod(String shippingMethod) { this.shippingMethod = shippingMethod; }

    public Timestamp getCreatedAt() { return createdAt; }
    public void setCreatedAt(Timestamp createdAt) { this.createdAt = createdAt; }

    public Timestamp getUpdatedAt() { return updatedAt; }
    public void setUpdatedAt(Timestamp updatedAt) { this.updatedAt = updatedAt; }

    public String toJson() {
        return String.format(
            "{\"orderId\":\"%s\",\"customerId\":\"%s\",\"total\":%.2f,\"currency\":\"%s\"," +
            "\"status\":\"%s\",\"paymentId\":\"%s\",\"paymentMethod\":\"%s\"," +
            "\"trackingNumber\":\"%s\",\"carrier\":\"%s\",\"shippingMethod\":\"%s\"}",
            orderId != null ? orderId : "",
            customerId != null ? customerId : "",
            total,
            currency != null ? currency : "USD",
            status != null ? status : "",
            paymentId != null ? paymentId : "",
            paymentMethod != null ? paymentMethod : "",
            trackingNumber != null ? trackingNumber : "",
            carrier != null ? carrier : "",
            shippingMethod != null ? shippingMethod : ""
        );
    }
}

