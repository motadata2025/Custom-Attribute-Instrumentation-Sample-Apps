package OtelApiTracerProvider.api;

import com.sun.net.httpserver.HttpExchange;
import com.sun.net.httpserver.HttpHandler;

import java.io.IOException;
import java.io.OutputStream;
import java.nio.charset.StandardCharsets;

/**
 * Swagger UI Handler for OtelApiTracerProvider demo.
 * Provides interactive API documentation for the Order endpoints.
 */
public class SwaggerHandler implements HttpHandler {

    private static final String SWAGGER_UI_HTML = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>OtelApiTracerProvider - Order API</title>
            <link rel="stylesheet" href="https://unpkg.com/swagger-ui-dist@5.9.0/swagger-ui.css" />
            <style>
                body { margin: 0; padding: 0; }
                .swagger-ui .topbar { display: none; }
            </style>
        </head>
        <body>
            <div id="swagger-ui"></div>
            <script src="https://unpkg.com/swagger-ui-dist@5.9.0/swagger-ui-bundle.js"></script>
            <script src="https://unpkg.com/swagger-ui-dist@5.9.0/swagger-ui-standalone-preset.js"></script>
            <script>
                window.onload = function() {
                    const spec = {
                        "openapi": "3.0.3",
                        "info": {
                            "title": "OtelApiTracerProvider - Order API",
                            "description": "Demonstrates manual span creation using OpenTelemetry Tracer API with custom attributes",
                            "version": "1.0.0"
                        },
                        "servers": [{"url": "http://localhost:8082"}],
                        "paths": {
                            "/orders": {
                                "get": {
                                    "summary": "Get All Orders",
                                    "description": "Retrieves all orders from the database.",
                                    "tags": ["Orders"],
                                    "responses": {
                                        "200": {
                                            "description": "List of orders",
                                            "content": {"application/json": {"schema": {"type": "array", "items": {"$ref": "#/components/schemas/Order"}}}}
                                        }
                                    }
                                },
                                "post": {
                                    "summary": "Create Order",
                                    "description": "Creates a new order. Demonstrates ROOT span with setNoParent() and CHILD spans for validation, payment, shipment, and database save.",
                                    "tags": ["Orders"],
                                    "requestBody": {
                                        "required": true,
                                        "content": {
                                            "application/json": {
                                                "schema": {"$ref": "#/components/schemas/OrderRequest"},
                                                "example": {"orderId": "ORD-NEW-001", "total": 99.99, "customerId": "CUST-001"}
                                            }
                                        }
                                    },
                                    "responses": {
                                        "201": {
                                            "description": "Order created successfully",
                                            "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Order"}}}
                                        },
                                        "500": {"description": "Internal server error"}
                                    }
                                }
                            },
                            "/orders/{orderId}": {
                                "get": {
                                    "summary": "Get Order",
                                    "description": "Retrieves order details by order ID.",
                                    "tags": ["Orders"],
                                    "parameters": [{
                                        "name": "orderId",
                                        "in": "path",
                                        "required": true,
                                        "schema": {"type": "string"},
                                        "example": "ORD-123"
                                    }],
                                    "responses": {
                                        "200": {
                                            "description": "Order found",
                                            "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Order"}}}
                                        },
                                        "400": {"description": "Order ID required"}
                                    }
                                }
                            }
                        },
                        "components": {
                            "schemas": {
                                "OrderRequest": {
                                    "type": "object",
                                    "properties": {
                                        "orderId": {"type": "string", "description": "Order ID (auto-generated if not provided)"},
                                        "total": {"type": "number", "description": "Order total amount"},
                                        "customerId": {"type": "string", "description": "Customer ID"}
                                    }
                                },
                                "Order": {
                                    "type": "object",
                                    "properties": {
                                        "orderId": {"type": "string"},
                                        "total": {"type": "number"},
                                        "customerId": {"type": "string"},
                                        "paymentId": {"type": "string"},
                                        "trackingNumber": {"type": "string"},
                                        "status": {"type": "string"}
                                    }
                                }
                            }
                        }
                    };
                    SwaggerUIBundle({
                        spec: spec,
                        dom_id: '#swagger-ui',
                        presets: [SwaggerUIBundle.presets.apis, SwaggerUIStandalonePreset],
                        layout: "StandaloneLayout"
                    });
                };
            </script>
        </body>
        </html>
        """;

    @Override
    public void handle(HttpExchange exchange) throws IOException {
        exchange.getResponseHeaders().set("Content-Type", "text/html");
        byte[] bytes = SWAGGER_UI_HTML.getBytes(StandardCharsets.UTF_8);
        exchange.sendResponseHeaders(200, bytes.length);
        try (OutputStream os = exchange.getResponseBody()) {
            os.write(bytes);
        }
    }
}

