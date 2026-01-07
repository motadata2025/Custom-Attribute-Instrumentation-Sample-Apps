package OtelApiTracerProvider.service;

import io.opentelemetry.api.GlobalOpenTelemetry;
import io.opentelemetry.api.common.AttributeKey;
import io.opentelemetry.api.common.Attributes;
import io.opentelemetry.api.trace.Span;
import io.opentelemetry.api.trace.SpanKind;
import io.opentelemetry.api.trace.StatusCode;
import io.opentelemetry.api.trace.Tracer;
import io.opentelemetry.context.Scope;

import OtelApiTracerProvider.model.Order;
import OtelApiTracerProvider.repository.OrderRepository;

import java.sql.SQLException;
import java.util.List;
import java.util.Optional;

/**
 * OrderService demonstrates manual span creation using OpenTelemetry Tracer API.
 * 
 * Key concepts demonstrated:
 * 1. Getting Tracer from GlobalOpenTelemetry
 * 2. Creating root spans with setNoParent()
 * 3. Creating child spans (auto-parented via Scope)
 * 4. Adding custom attributes to spans
 * 5. Setting span status and recording exceptions
 * 6. Proper span lifecycle management (try-finally with end())
 */
public class OrderService {

    // Get Tracer - the instrumentation name identifies your component
    private static final Tracer tracer =
            GlobalOpenTelemetry.get().getTracer("com.example.order-service", "1.0.0");

    private final OrderRepository orderRepository = new OrderRepository();

    /**
     * Process an order - demonstrates ROOT span with CHILD spans
     */
    public Order processOrder(String orderId, double total, String customerId) {
        
        // ============================================================
        // ROOT SPAN - setNoParent() creates a NEW trace
        // ============================================================
        Span rootSpan = tracer.spanBuilder("order.process")
                .setSpanKind(SpanKind.SERVER)
                .setNoParent()  // Creates a new trace (no parent)
                .startSpan();

        try (Scope rootScope = rootSpan.makeCurrent()) {
            
            // Add custom attributes to ROOT span
            rootSpan.setAttribute("order.id", orderId);
            rootSpan.setAttribute("order.total", total);
            rootSpan.setAttribute("order.customer_id", customerId);
            rootSpan.setAttribute("order.currency", "USD");
            
            // ============================================================
            // CHILD SPAN 1: Validate Order
            // ============================================================
            boolean isValid = validateOrder(orderId, total);
            
            // ============================================================
            // CHILD SPAN 2: Process Payment
            // ============================================================
            String paymentId = processPayment(orderId, total, customerId);
            
            // ============================================================
            // CHILD SPAN 3: Create Shipment
            // ============================================================
            String trackingNumber = createShipment(orderId, customerId);

            // ============================================================
            // CHILD SPAN 4: Save to Database
            // ============================================================
            Order order = new Order(orderId, total, customerId, paymentId, trackingNumber, "COMPLETED");
            order.setCurrency("USD");
            order.setPaymentMethod("CREDIT_CARD");
            order.setCarrier("FedEx");
            order.setShippingMethod("EXPRESS");

            saveOrderToDatabase(order);

            // Update root span with results
            rootSpan.setAttribute("order.payment_id", paymentId);
            rootSpan.setAttribute("order.tracking_number", trackingNumber);
            rootSpan.setAttribute("order.status", "COMPLETED");
            rootSpan.setStatus(StatusCode.OK);

            return order;
            
        } catch (Exception e) {
            rootSpan.recordException(e);
            rootSpan.setStatus(StatusCode.ERROR, e.getMessage());
            throw e;
        } finally {
            rootSpan.end();  // Always end the span!
        }
    }

    /**
     * Validate order - CHILD span (auto-parented to current span in context)
     */
    private boolean validateOrder(String orderId, double total) {
        Span span = tracer.spanBuilder("order.validate")
                .setSpanKind(SpanKind.INTERNAL)
                .startSpan();  // No setNoParent() = child of current span

        try (Scope scope = span.makeCurrent()) {
            // Add custom attributes
            span.setAttribute("validation.order_id", orderId);
            span.setAttribute("validation.total", total);
            span.setAttribute("validation.min_amount", 1.0);
            span.setAttribute("validation.max_amount", 10000.0);
            
            // Simulate validation logic
            boolean isValid = total > 0 && total < 10000;
            
            span.setAttribute("validation.result", isValid ? "PASSED" : "FAILED");
            span.setAttribute("validation.checks_performed", 3);
            
            if (isValid) {
                span.setStatus(StatusCode.OK);
            } else {
                span.setStatus(StatusCode.ERROR, "Validation failed");
            }
            
            return isValid;
        } finally {
            span.end();
        }
    }

    /**
     * Process payment - CHILD span with payment-specific attributes
     */
    private String processPayment(String orderId, double total, String customerId) {
        Span span = tracer.spanBuilder("order.payment")
                .setSpanKind(SpanKind.CLIENT)  // External service call
                .startSpan();

        try (Scope scope = span.makeCurrent()) {
            // Add payment-specific custom attributes
            span.setAttribute("payment.order_id", orderId);
            span.setAttribute("payment.amount", total);
            span.setAttribute("payment.customer_id", customerId);
            span.setAttribute("payment.method", "CREDIT_CARD");
            span.setAttribute("payment.provider", "stripe");
            span.setAttribute("payment.currency", "USD");
            
            // Simulate payment processing
            String paymentId = "PAY-" + System.currentTimeMillis();
            
            span.setAttribute("payment.id", paymentId);
            span.setAttribute("payment.status", "SUCCESS");
            span.setAttribute("payment.processing_time_ms", 150);
            
            // Add event to span
            span.addEvent("payment.authorized", Attributes.of(
                    AttributeKey.stringKey("auth_code"), "AUTH123",
                    AttributeKey.booleanKey("fraud_check_passed"), true
            ));
            
            span.setStatus(StatusCode.OK);
            return paymentId;
        } finally {
            span.end();
        }
    }

    /**
     * Create shipment - CHILD span with shipping attributes
     */
    private String createShipment(String orderId, String customerId) {
        Span span = tracer.spanBuilder("order.shipment")
                .setSpanKind(SpanKind.CLIENT)
                .startSpan();

        try (Scope scope = span.makeCurrent()) {
            // Add shipment-specific custom attributes
            span.setAttribute("shipment.order_id", orderId);
            span.setAttribute("shipment.customer_id", customerId);
            span.setAttribute("shipment.carrier", "FedEx");
            span.setAttribute("shipment.method", "EXPRESS");
            span.setAttribute("shipment.estimated_days", 3);
            
            // Simulate shipment creation
            String trackingNumber = "TRK-" + System.currentTimeMillis();
            
            span.setAttribute("shipment.tracking_number", trackingNumber);
            span.setAttribute("shipment.status", "CREATED");
            span.setAttribute("shipment.weight_kg", 2.5);
            
            span.setStatus(StatusCode.OK);
            return trackingNumber;
        } finally {
            span.end();
        }
    }

    /**
     * Save order to database - CHILD span for database operation
     */
    private void saveOrderToDatabase(Order order) {
        Span span = tracer.spanBuilder("order.save_to_db")
                .setSpanKind(SpanKind.CLIENT)
                .startSpan();

        try (Scope scope = span.makeCurrent()) {
            span.setAttribute("db.system", "postgresql");
            span.setAttribute("db.name", "orderdb");
            span.setAttribute("db.operation", "INSERT");
            span.setAttribute("db.table", "orders");
            span.setAttribute("order.id", order.getOrderId());

            orderRepository.create(order);

            span.setAttribute("db.rows_affected", 1);
            span.setStatus(StatusCode.OK);
        } catch (SQLException e) {
            span.recordException(e);
            span.setStatus(StatusCode.ERROR, "Failed to save order: " + e.getMessage());
            // Log but don't fail the order - order was processed successfully
            System.err.println("Warning: Failed to save order to database: " + e.getMessage());
        } finally {
            span.end();
        }
    }

    /**
     * Get order by ID - demonstrates database read with span
     */
    public Optional<Order> getOrderById(String orderId) {
        Span span = tracer.spanBuilder("order.get_by_id")
                .setSpanKind(SpanKind.CLIENT)
                .startSpan();

        try (Scope scope = span.makeCurrent()) {
            span.setAttribute("db.system", "postgresql");
            span.setAttribute("db.name", "orderdb");
            span.setAttribute("db.operation", "SELECT");
            span.setAttribute("db.table", "orders");
            span.setAttribute("order.id", orderId);

            Optional<Order> order = orderRepository.findById(orderId);

            span.setAttribute("order.found", order.isPresent());
            if (order.isPresent()) {
                span.setAttribute("order.status", order.get().getStatus());
                span.setAttribute("order.total", order.get().getTotal());
            }
            span.setStatus(StatusCode.OK);
            return order;
        } catch (SQLException e) {
            span.recordException(e);
            span.setStatus(StatusCode.ERROR, e.getMessage());
            throw new RuntimeException("Failed to get order: " + e.getMessage(), e);
        } finally {
            span.end();
        }
    }

    /**
     * Get all orders - demonstrates database read with span
     */
    public List<Order> getAllOrders() {
        Span span = tracer.spanBuilder("order.get_all")
                .setSpanKind(SpanKind.CLIENT)
                .startSpan();

        try (Scope scope = span.makeCurrent()) {
            span.setAttribute("db.system", "postgresql");
            span.setAttribute("db.name", "orderdb");
            span.setAttribute("db.operation", "SELECT");
            span.setAttribute("db.table", "orders");

            List<Order> orders = orderRepository.findAll();

            span.setAttribute("order.count", orders.size());
            span.setStatus(StatusCode.OK);
            return orders;
        } catch (SQLException e) {
            span.recordException(e);
            span.setStatus(StatusCode.ERROR, e.getMessage());
            throw new RuntimeException("Failed to get orders: " + e.getMessage(), e);
        } finally {
            span.end();
        }
    }
}

