package OtelApiTracerProvider.repository;

import OtelApiTracerProvider.db.DatabaseUtil;
import OtelApiTracerProvider.model.Order;

import java.sql.*;
import java.util.ArrayList;
import java.util.List;
import java.util.Optional;

/**
 * Repository for Order CRUD operations.
 * Performs database operations on the orders table.
 */
public class OrderRepository {

    /**
     * Create a new order in the database.
     */
    public Order create(Order order) throws SQLException {
        String sql = "INSERT INTO orders (order_id, customer_id, total, currency, status, " +
                     "payment_id, payment_method, tracking_number, carrier, shipping_method) " +
                     "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)";

        try (Connection conn = DatabaseUtil.getConnection();
             PreparedStatement stmt = conn.prepareStatement(sql)) {

            stmt.setString(1, order.getOrderId());
            stmt.setString(2, order.getCustomerId());
            stmt.setDouble(3, order.getTotal());
            stmt.setString(4, order.getCurrency() != null ? order.getCurrency() : "USD");
            stmt.setString(5, order.getStatus() != null ? order.getStatus() : "PENDING");
            stmt.setString(6, order.getPaymentId());
            stmt.setString(7, order.getPaymentMethod());
            stmt.setString(8, order.getTrackingNumber());
            stmt.setString(9, order.getCarrier());
            stmt.setString(10, order.getShippingMethod());

            stmt.executeUpdate();
            return order;
        }
    }

    /**
     * Find an order by its ID.
     */
    public Optional<Order> findById(String orderId) throws SQLException {
        String sql = "SELECT order_id, customer_id, total, currency, status, " +
                     "payment_id, payment_method, tracking_number, carrier, shipping_method, " +
                     "created_at, updated_at FROM orders WHERE order_id = ?";

        try (Connection conn = DatabaseUtil.getConnection();
             PreparedStatement stmt = conn.prepareStatement(sql)) {

            stmt.setString(1, orderId);

            try (ResultSet rs = stmt.executeQuery()) {
                if (rs.next()) {
                    return Optional.of(mapRowToOrder(rs));
                }
            }
        }
        return Optional.empty();
    }

    /**
     * Find all orders.
     */
    public List<Order> findAll() throws SQLException {
        String sql = "SELECT order_id, customer_id, total, currency, status, " +
                     "payment_id, payment_method, tracking_number, carrier, shipping_method, " +
                     "created_at, updated_at FROM orders ORDER BY created_at DESC";
        List<Order> orders = new ArrayList<>();

        try (Connection conn = DatabaseUtil.getConnection();
             Statement stmt = conn.createStatement();
             ResultSet rs = stmt.executeQuery(sql)) {

            while (rs.next()) {
                orders.add(mapRowToOrder(rs));
            }
        }
        return orders;
    }

    /**
     * Find orders by customer ID.
     */
    public List<Order> findByCustomerId(String customerId) throws SQLException {
        String sql = "SELECT order_id, customer_id, total, currency, status, " +
                     "payment_id, payment_method, tracking_number, carrier, shipping_method, " +
                     "created_at, updated_at FROM orders WHERE customer_id = ? ORDER BY created_at DESC";
        List<Order> orders = new ArrayList<>();

        try (Connection conn = DatabaseUtil.getConnection();
             PreparedStatement stmt = conn.prepareStatement(sql)) {

            stmt.setString(1, customerId);

            try (ResultSet rs = stmt.executeQuery()) {
                while (rs.next()) {
                    orders.add(mapRowToOrder(rs));
                }
            }
        }
        return orders;
    }

    /**
     * Update an existing order.
     */
    public Order update(Order order) throws SQLException {
        String sql = "UPDATE orders SET status = ?, payment_id = ?, payment_method = ?, " +
                     "tracking_number = ?, carrier = ?, shipping_method = ?, updated_at = CURRENT_TIMESTAMP " +
                     "WHERE order_id = ?";

        try (Connection conn = DatabaseUtil.getConnection();
             PreparedStatement stmt = conn.prepareStatement(sql)) {

            stmt.setString(1, order.getStatus());
            stmt.setString(2, order.getPaymentId());
            stmt.setString(3, order.getPaymentMethod());
            stmt.setString(4, order.getTrackingNumber());
            stmt.setString(5, order.getCarrier());
            stmt.setString(6, order.getShippingMethod());
            stmt.setString(7, order.getOrderId());

            int rowsAffected = stmt.executeUpdate();
            if (rowsAffected == 0) {
                throw new SQLException("Order not found: " + order.getOrderId());
            }
            return order;
        }
    }

    /**
     * Delete an order by ID.
     */
    public boolean delete(String orderId) throws SQLException {
        String sql = "DELETE FROM orders WHERE order_id = ?";

        try (Connection conn = DatabaseUtil.getConnection();
             PreparedStatement stmt = conn.prepareStatement(sql)) {

            stmt.setString(1, orderId);
            int rowsAffected = stmt.executeUpdate();
            return rowsAffected > 0;
        }
    }

    private Order mapRowToOrder(ResultSet rs) throws SQLException {
        return new Order(
            rs.getString("order_id"),
            rs.getString("customer_id"),
            rs.getDouble("total"),
            rs.getString("currency"),
            rs.getString("status"),
            rs.getString("payment_id"),
            rs.getString("payment_method"),
            rs.getString("tracking_number"),
            rs.getString("carrier"),
            rs.getString("shipping_method"),
            rs.getTimestamp("created_at"),
            rs.getTimestamp("updated_at")
        );
    }
}

