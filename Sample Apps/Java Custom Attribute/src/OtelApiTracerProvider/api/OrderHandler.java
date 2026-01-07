package OtelApiTracerProvider.api;

import com.sun.net.httpserver.HttpExchange;
import com.sun.net.httpserver.HttpHandler;

import OtelApiTracerProvider.model.Order;
import OtelApiTracerProvider.service.OrderService;

import java.io.*;
import java.util.List;
import java.util.Optional;
import java.nio.charset.StandardCharsets;
import java.util.stream.Collectors;

/**
 * HTTP Handler for Order endpoints.
 * Delegates to OrderService which demonstrates manual span creation.
 */
public class OrderHandler implements HttpHandler {
    
    private final OrderService orderService = new OrderService();

    @Override
    public void handle(HttpExchange exchange) throws IOException {
        addCorsHeaders(exchange);

        String method = exchange.getRequestMethod();
        String path = exchange.getRequestURI().getPath();

        if ("OPTIONS".equals(method)) {
            exchange.sendResponseHeaders(204, -1);
            return;
        }

        try {
            switch (method) {
                case "GET":
                    handleGet(exchange, path);
                    break;
                case "POST":
                    handlePost(exchange);
                    break;
                default:
                    sendResponse(exchange, 405, "{\"error\":\"Method not allowed\"}");
            }
        } catch (Exception e) {
            e.printStackTrace();
            sendResponse(exchange, 500, "{\"error\":\"" + e.getMessage() + "\"}");
        }
    }

    private void addCorsHeaders(HttpExchange exchange) {
        exchange.getResponseHeaders().set("Access-Control-Allow-Origin", "*");
        exchange.getResponseHeaders().set("Access-Control-Allow-Methods", "GET, POST, OPTIONS");
        exchange.getResponseHeaders().set("Access-Control-Allow-Headers", "Content-Type");
    }

    /**
     * GET /orders - Get all orders
     * GET /orders/{orderId} - Get order by ID
     */
    private void handleGet(HttpExchange exchange, String path) throws IOException {
        String[] parts = path.split("/");

        if (parts.length == 3 && !parts[2].isEmpty()) {
            // GET /orders/{orderId}
            String orderId = parts[2];
            Optional<Order> order = orderService.getOrderById(orderId);

            if (order.isPresent()) {
                sendResponse(exchange, 200, order.get().toJson());
            } else {
                sendResponse(exchange, 404, "{\"error\":\"Order not found: " + orderId + "\"}");
            }
        } else {
            // GET /orders - return all orders
            List<Order> orders = orderService.getAllOrders();
            StringBuilder json = new StringBuilder("[");
            for (int i = 0; i < orders.size(); i++) {
                json.append(orders.get(i).toJson());
                if (i < orders.size() - 1) {
                    json.append(",");
                }
            }
            json.append("]");
            sendResponse(exchange, 200, json.toString());
        }
    }

    /**
     * POST /orders - Create a new order
     * This triggers the OrderService.processOrder() which demonstrates:
     * - Root span creation with setNoParent()
     * - Child span creation (auto-parented)
     * - Custom attributes on all spans
     */
    private void handlePost(HttpExchange exchange) throws IOException {
        String body = readRequestBody(exchange);
        
        // Parse request
        String orderId = extractJsonValue(body, "orderId");
        String totalStr = extractJsonValue(body, "total");
        String customerId = extractJsonValue(body, "customerId");
        
        if (orderId == null || orderId.isEmpty()) {
            orderId = "ORD-" + System.currentTimeMillis();
        }
        if (customerId == null || customerId.isEmpty()) {
            customerId = "CUST-DEFAULT";
        }
        
        double total = 0.0;
        try {
            total = totalStr != null ? Double.parseDouble(totalStr) : 99.99;
        } catch (NumberFormatException e) {
            total = 99.99;
        }
        
        // Process order - this creates spans with custom attributes
        Order order = orderService.processOrder(orderId, total, customerId);
        
        sendResponse(exchange, 201, order.toJson());
    }

    private String readRequestBody(HttpExchange exchange) throws IOException {
        try (BufferedReader reader = new BufferedReader(
                new InputStreamReader(exchange.getRequestBody(), StandardCharsets.UTF_8))) {
            return reader.lines().collect(Collectors.joining("\n"));
        }
    }

    private void sendResponse(HttpExchange exchange, int statusCode, String response) throws IOException {
        exchange.getResponseHeaders().set("Content-Type", "application/json");
        byte[] bytes = response.getBytes(StandardCharsets.UTF_8);
        exchange.sendResponseHeaders(statusCode, bytes.length);
        try (OutputStream os = exchange.getResponseBody()) {
            os.write(bytes);
        }
    }

    private String extractJsonValue(String json, String key) {
        if (json == null) return null;
        String pattern = "\"" + key + "\"";
        int keyIndex = json.indexOf(pattern);
        if (keyIndex == -1) return null;
        
        int colonIndex = json.indexOf(":", keyIndex);
        if (colonIndex == -1) return null;
        
        int start = colonIndex + 1;
        while (start < json.length() && Character.isWhitespace(json.charAt(start))) start++;
        
        if (start >= json.length()) return null;

        if (json.charAt(start) == '"') {
            int end = json.indexOf("\"", start + 1);
            return end > start ? json.substring(start + 1, end) : null;
        } else {
            int end = start;
            while (end < json.length() && !",}".contains(String.valueOf(json.charAt(end)))) end++;
            return json.substring(start, end).trim();
        }
    }
}

