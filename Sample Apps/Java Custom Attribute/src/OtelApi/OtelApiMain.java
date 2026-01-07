package OtelApi;

import OtelApi.api.InstrumentationTestHandler;
import OtelApi.api.SwaggerHandler;
import OtelApi.api.UserHandler;
import com.sun.net.httpserver.HttpServer;

import java.io.IOException;
import java.net.InetSocketAddress;

public class OtelApiMain {
    private static final int PORT = Integer.parseInt(System.getenv().getOrDefault("PORT", "8080"));

    public static void main(String[] args) {
        try {
            HttpServer server = HttpServer.create(new InetSocketAddress(PORT), 0);

            // Register handlers
            server.createContext("/users", new UserHandler());
            server.createContext("/test-instrumentation", new InstrumentationTestHandler());

            // Swagger UI and OpenAPI spec
            server.createContext("/swagger", new SwaggerHandler());

            server.setExecutor(null); // Use default executor
            server.start();

            System.out.println("Server started on port " + PORT);
            System.out.println("Swagger UI: http://localhost:" + PORT + "/swagger");

        } catch (IOException e) {
            System.err.println("Failed to start server: " + e.getMessage());
            e.printStackTrace();
            System.exit(1);
        }
    }
}