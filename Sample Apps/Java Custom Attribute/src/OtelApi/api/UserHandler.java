package OtelApi.api;

import com.sun.net.httpserver.HttpExchange;
import com.sun.net.httpserver.HttpHandler;
import OtelApi.model.User;
import OtelApi.repository.UserRepository;
import OtelApi.util.MotadataDynamicInstrumentation;

import java.io.*;
import java.nio.charset.StandardCharsets;
import java.sql.SQLException;
import java.util.List;
import java.util.Optional;
import java.util.stream.Collectors;

public class UserHandler implements HttpHandler {
    private final UserRepository userRepository = new UserRepository();

    @Override
    public void handle(HttpExchange exchange) throws IOException {
        // Add CORS headers
        addCorsHeaders(exchange);

        String method = exchange.getRequestMethod();
        String path = exchange.getRequestURI().getPath();

        // Handle CORS preflight
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
                case "PUT":
                    handlePut(exchange, path);
                    break;
                case "DELETE":
                    handleDelete(exchange, path);
                    break;
                default:
                    sendResponse(exchange, 405, "{\"error\":\"Method not allowed\"}");
            }
        } catch (SQLException e) {
            e.printStackTrace();
            sendResponse(exchange, 500, "{\"error\":\"Database error: " + e.getMessage() + "\"}");
        } catch (Exception e) {
            e.printStackTrace();
            sendResponse(exchange, 500, "{\"error\":\"Internal server error\"}");
        }
    }

    private void addCorsHeaders(HttpExchange exchange) {
        exchange.getResponseHeaders().set("Access-Control-Allow-Origin", "*");
        exchange.getResponseHeaders().set("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS");
        exchange.getResponseHeaders().set("Access-Control-Allow-Headers", "Content-Type, Authorization");
    }

    private void handleGet(HttpExchange exchange, String path) throws SQLException, IOException {
        // GET /users - get all users
        // GET /users/{username} - get specific user
        String[] parts = path.split("/");

        if (parts.length == 2) {
            // Get all users
            List<User> users = userRepository.findAll();

            MotadataDynamicInstrumentation.set("user.count", users.size());

            String json = "[" + users.stream().map(User::toJson).collect(Collectors.joining(",")) + "]";
            sendResponse(exchange, 200, json);
        } else if (parts.length == 3) {
            // Get specific user
            String username = parts[2];
            Optional<User> user = userRepository.findByUsername(username);
            if (user.isPresent()) {
                User u = user.get();

                MotadataDynamicInstrumentation.set("user.username", u.getUsername());
                MotadataDynamicInstrumentation.set("user.email", u.getEmail());
                MotadataDynamicInstrumentation.set("user.age", u.getAge());
                MotadataDynamicInstrumentation.set("user.salary", u.getSalary());
                MotadataDynamicInstrumentation.set("user.active", u.isActive());
                MotadataDynamicInstrumentation.setStringList("user.tags", u.getTags());

                sendResponse(exchange, 200, u.toJson());
            } else {
                sendResponse(exchange, 404, "{\"error\":\"User not found\"}");
            }
        } else {
            sendResponse(exchange, 400, "{\"error\":\"Invalid path\"}");
        }
    }

    private void handlePost(HttpExchange exchange) throws SQLException, IOException {
        String body = readRequestBody(exchange);
        User user = parseUser(body);

        if (user.getUsername() == null || user.getUsername().isEmpty()) {
            sendResponse(exchange, 400, "{\"error\":\"Username is required\"}");
            return;
        }

        User created = userRepository.create(user);

        MotadataDynamicInstrumentation.set("user.operation", "create");
        MotadataDynamicInstrumentation.set("user.username", created.getUsername());
        MotadataDynamicInstrumentation.set("user.email", created.getEmail());
        MotadataDynamicInstrumentation.set("user.age", created.getAge());
        MotadataDynamicInstrumentation.set("user.salary", created.getSalary());
        MotadataDynamicInstrumentation.set("user.active", created.isActive());
        MotadataDynamicInstrumentation.setStringList("user.tags", created.getTags());

        sendResponse(exchange, 201, created.toJson());
    }

    private void handlePut(HttpExchange exchange, String path) throws SQLException, IOException {
        String[] parts = path.split("/");
        if (parts.length != 3) {
            sendResponse(exchange, 400, "{\"error\":\"Username required in path\"}");
            return;
        }

        String username = parts[2];
        String body = readRequestBody(exchange);
        User user = parseUser(body);
        user.setUsername(username);

        try {
            User updated = userRepository.update(user);

            MotadataDynamicInstrumentation.set("user.operation", "update");
            MotadataDynamicInstrumentation.set("user.username", updated.getUsername());
            MotadataDynamicInstrumentation.set("user.email", updated.getEmail());
            MotadataDynamicInstrumentation.set("user.age", updated.getAge());
            MotadataDynamicInstrumentation.set("user.salary", updated.getSalary());
            MotadataDynamicInstrumentation.set("user.active", updated.isActive());
            MotadataDynamicInstrumentation.setStringList("user.tags", updated.getTags());

            sendResponse(exchange, 200, updated.toJson());
        } catch (SQLException e) {
            if (e.getMessage().contains("not found")) {
                sendResponse(exchange, 404, "{\"error\":\"User not found\"}");
            } else {
                throw e;
            }
        }
    }

    private void handleDelete(HttpExchange exchange, String path) throws SQLException, IOException {
        String[] parts = path.split("/");
        if (parts.length != 3) {
            sendResponse(exchange, 400, "{\"error\":\"Username required in path\"}");
            return;
        }

        String username = parts[2];
        boolean deleted = userRepository.delete(username);

        if (deleted) {
            MotadataDynamicInstrumentation.set("user.username", username);
            sendResponse(exchange, 200, "{\"message\":\"User deleted successfully\"}");
        } else {
            sendResponse(exchange, 404, "{\"error\":\"User not found\"}");
        }
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

    // Simple JSON parser for User object
    private User parseUser(String json) {
        User user = new User();
        user.setUsername(extractJsonValue(json, "username"));
        user.setEmail(extractJsonValue(json, "email"));
        user.setFullName(extractJsonValue(json, "fullName"));

        // Parse int: age
        String ageStr = extractJsonValue(json, "age");
        if (ageStr != null && !ageStr.isEmpty()) {
            try {
                user.setAge(Integer.parseInt(ageStr));
            } catch (NumberFormatException e) {
                user.setAge(0);
            }
        }

        // Parse double: salary
        String salaryStr = extractJsonValue(json, "salary");
        if (salaryStr != null && !salaryStr.isEmpty()) {
            try {
                user.setSalary(Double.parseDouble(salaryStr));
            } catch (NumberFormatException e) {
                user.setSalary(0.0);
            }
        }

        // Parse boolean: isActive
        String isActiveStr = extractJsonValue(json, "isActive");
        if (isActiveStr != null && !isActiveStr.isEmpty()) {
            user.setActive(Boolean.parseBoolean(isActiveStr));
        }

        // Parse List<String>: tags
        user.setTags(extractJsonArray(json, "tags"));

        return user;
    }

    // Extract JSON array values as List<String>
    private List<String> extractJsonArray(String json, String key) {
        List<String> result = new java.util.ArrayList<>();
        String pattern = "\"" + key + "\"";
        int keyIndex = json.indexOf(pattern);
        if (keyIndex == -1) return result;

        int colonIndex = json.indexOf(":", keyIndex);
        if (colonIndex == -1) return result;

        int bracketStart = json.indexOf("[", colonIndex);
        if (bracketStart == -1) return result;

        int bracketEnd = json.indexOf("]", bracketStart);
        if (bracketEnd == -1) return result;

        String arrayContent = json.substring(bracketStart + 1, bracketEnd).trim();
        if (arrayContent.isEmpty()) return result;

        // Parse array elements
        String[] elements = arrayContent.split(",");
        for (String element : elements) {
            element = element.trim();
            if (element.startsWith("\"") && element.endsWith("\"")) {
                result.add(element.substring(1, element.length() - 1));
            } else if (!element.isEmpty()) {
                result.add(element);
            }
        }
        return result;
    }

    private String extractJsonValue(String json, String key) {
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

