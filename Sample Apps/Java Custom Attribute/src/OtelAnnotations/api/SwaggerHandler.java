package OtelAnnotations.api;

import com.sun.net.httpserver.HttpExchange;
import com.sun.net.httpserver.HttpHandler;

import java.io.IOException;
import java.io.OutputStream;
import java.nio.charset.StandardCharsets;

public class SwaggerHandler implements HttpHandler {

    private static final String SWAGGER_UI_HTML = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>User CRUD API - Swagger UI</title>
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
                        "info": {"title": "User CRUD API", "version": "1.0.0"},
                        "servers": [{"url": "http://localhost:8081"}],
                        "paths": {
                            "/users": {
                                "get": {"summary": "Get all users", "tags": ["Users"], "responses": {"200": {"description": "Success"}}},
                                "post": {"summary": "Create user", "tags": ["Users"], "requestBody": {"required": true, "content": {"application/json": {"schema": {"$ref": "#/components/schemas/User"}}}}, "responses": {"201": {"description": "Created"}}}
                            },
                            "/users/{username}": {
                                "get": {"summary": "Get user by username", "tags": ["Users"], "parameters": [{"name": "username", "in": "path", "required": true, "schema": {"type": "string"}}], "responses": {"200": {"description": "Success"}}},
                                "put": {"summary": "Update user", "tags": ["Users"], "parameters": [{"name": "username", "in": "path", "required": true, "schema": {"type": "string"}}], "requestBody": {"required": true, "content": {"application/json": {"schema": {"$ref": "#/components/schemas/User"}}}}, "responses": {"200": {"description": "Updated"}}},
                                "delete": {"summary": "Delete user", "tags": ["Users"], "parameters": [{"name": "username", "in": "path", "required": true, "schema": {"type": "string"}}], "responses": {"200": {"description": "Deleted"}}}
                            }
                        },
                        "components": {
                            "schemas": {
                                "User": {"type": "object", "properties": {"username": {"type": "string"}, "email": {"type": "string"}, "fullName": {"type": "string"}, "age": {"type": "integer"}, "salary": {"type": "number"}, "isActive": {"type": "boolean"}, "tags": {"type": "array", "items": {"type": "string"}}}}
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

