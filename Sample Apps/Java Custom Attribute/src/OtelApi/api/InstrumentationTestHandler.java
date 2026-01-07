package OtelApi.api;

import com.sun.net.httpserver.HttpExchange;
import com.sun.net.httpserver.HttpHandler;
import OtelApi.util.MotadataDynamicInstrumentation;

import java.io.IOException;
import java.io.OutputStream;
import java.nio.charset.StandardCharsets;
import java.util.List;

/**
 * Test API to verify all data types supported by MotadataDynamicInstrumentation.
 * GET /test-instrumentation - Tests all primitive, boxed, and list types
 */
public class InstrumentationTestHandler implements HttpHandler {

    @Override
    public void handle(HttpExchange exchange) throws IOException {
        addCorsHeaders(exchange);

        if ("OPTIONS".equals(exchange.getRequestMethod())) {
            exchange.sendResponseHeaders(204, -1);
            return;
        }

        if (!"GET".equals(exchange.getRequestMethod())) {
            sendResponse(exchange, 405, "{\"error\":\"Method not allowed\"}");
            return;
        }

        // ========== Test Primitive Types ==========
        
        // String
        MotadataDynamicInstrumentation.set("test.string", "hello world");
        
        // boolean (primitive)
        MotadataDynamicInstrumentation.set("test.boolean.primitive", true);
        
        // double (primitive)
        MotadataDynamicInstrumentation.set("test.double.primitive", 3.14159);
        
        // int (primitive) - goes to long overload
        MotadataDynamicInstrumentation.set("test.int.primitive", 42);
        
        // long (primitive)
        MotadataDynamicInstrumentation.set("test.long.primitive", 9876543210L);

        // ========== Test Boxed Types (null-safe) ==========
        
        // Boolean (boxed)
        Boolean boxedBoolean = Boolean.FALSE;
        MotadataDynamicInstrumentation.set("test.boolean.boxed", boxedBoolean);
        
        // Double (boxed)
        Double boxedDouble = 2.71828;
        MotadataDynamicInstrumentation.set("test.double.boxed", boxedDouble);
        
        // Integer (boxed)
        Integer boxedInteger = 100;
        MotadataDynamicInstrumentation.set("test.integer.boxed", boxedInteger);
        
        // Long (boxed)
        Long boxedLong = 1234567890L;
        MotadataDynamicInstrumentation.set("test.long.boxed", boxedLong);

        // ========== Test Null Values (should be ignored) ==========
        
        MotadataDynamicInstrumentation.set("test.null.string", (String) null);
        MotadataDynamicInstrumentation.set("test.null.boolean", (Boolean) null);
        MotadataDynamicInstrumentation.set("test.null.double", (Double) null);
        MotadataDynamicInstrumentation.set("test.null.integer", (Integer) null);
        MotadataDynamicInstrumentation.set("test.null.long", (Long) null);

        // ========== Test List Types ==========
        
        // List<String>
        MotadataDynamicInstrumentation.setStringList("test.list.string", List.of("apple", "banana", "cherry"));
        
        // List<Boolean>
        MotadataDynamicInstrumentation.setBooleanList("test.list.boolean", List.of(true, false, true));
        
        // List<Double>
        MotadataDynamicInstrumentation.setDoubleList("test.list.double", List.of(1.1, 2.2, 3.3));
        
        // List<Integer>
        MotadataDynamicInstrumentation.setIntegerList("test.list.integer", List.of(10, 20, 30));
        
        // List<Long>
        MotadataDynamicInstrumentation.setLongList("test.list.long", List.of(100L, 200L, 300L));

        // Build response
        String response = """
            {
                "status": "success",
                "message": "All instrumentation methods tested",
                "tested_types": {
                    "primitives": ["String", "boolean", "double", "int", "long"],
                    "boxed": ["Boolean", "Double", "Integer", "Long"],
                    "lists": ["List<String>", "List<Boolean>", "List<Double>", "List<Integer>", "List<Long>"],
                    "null_handling": ["null values ignored for all types", "empty lists ignored"]
                },
                "expected_attributes": [
                    "apm.test.string",
                    "apm.test.boolean.primitive",
                    "apm.test.double.primitive",
                    "apm.test.int.primitive",
                    "apm.test.long.primitive",
                    "apm.test.boolean.boxed",
                    "apm.test.double.boxed",
                    "apm.test.integer.boxed",
                    "apm.test.long.boxed",
                    "apm.test.list.string",
                    "apm.test.list.boolean",
                    "apm.test.list.double",
                    "apm.test.list.integer",
                    "apm.test.list.long"
                ]
            }
            """;

        sendResponse(exchange, 200, response);
    }

    private void addCorsHeaders(HttpExchange exchange) {
        exchange.getResponseHeaders().add("Access-Control-Allow-Origin", "*");
        exchange.getResponseHeaders().add("Access-Control-Allow-Methods", "GET, OPTIONS");
        exchange.getResponseHeaders().add("Access-Control-Allow-Headers", "Content-Type");
    }

    private void sendResponse(HttpExchange exchange, int statusCode, String response) throws IOException {
        exchange.getResponseHeaders().add("Content-Type", "application/json");
        byte[] bytes = response.getBytes(StandardCharsets.UTF_8);
        exchange.sendResponseHeaders(statusCode, bytes.length);
        try (OutputStream os = exchange.getResponseBody()) {
            os.write(bytes);
        }
    }
}

