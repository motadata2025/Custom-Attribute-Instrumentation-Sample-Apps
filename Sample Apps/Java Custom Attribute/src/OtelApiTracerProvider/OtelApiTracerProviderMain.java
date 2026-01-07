package OtelApiTracerProvider;

import OtelApiTracerProvider.api.OrderHandler;
import OtelApiTracerProvider.api.SwaggerHandler;
import com.sun.net.httpserver.HttpServer;

import java.io.IOException;
import java.net.InetSocketAddress;

/**
 * Main entry point for OtelApiTracerProvider demo.
 * 
 * This package demonstrates manual span creation using:
 * - GlobalOpenTelemetry.get().getTracer() - Get tracer instance
 * - tracer.spanBuilder("name").startSpan() - Create spans manually
 * - span.makeCurrent() with Scope - Context propagation
 * - setNoParent() - Create root span (new trace)
 * - setAttribute() - Add custom attributes to spans
 * 
 * Run with Java Agent:
 * java -javaagent:"/path/to/opentelemetry-javaagent.jar" \
 *      -Dotel.service.name=otel-tracer-provider-demo \
 *      -jar OtelApiTracerProvider-fat.jar
 */
public class OtelApiTracerProviderMain {
    private static final int PORT = Integer.parseInt(System.getenv().getOrDefault("PORT", "8082"));

    public static void main(String[] args) {
        try {
            HttpServer server = HttpServer.create(new InetSocketAddress(PORT), 0);

            // Register handlers
            server.createContext("/orders", new OrderHandler());
            server.createContext("/swagger", new SwaggerHandler());

            server.setExecutor(null);
            server.start();

            System.out.println("==============================================");
            System.out.println("OtelApiTracerProvider Demo Server Started!");
            System.out.println("==============================================");
            System.out.println("Port: " + PORT);
            System.out.println();
            System.out.println("Endpoints:");
            System.out.println("  POST /orders              - Create order (demonstrates root span + child spans)");
            System.out.println("  GET  /orders/{orderId}    - Get order (demonstrates child spans with attributes)");
            System.out.println();
            System.out.println("Swagger UI:");
            System.out.println("  http://localhost:" + PORT + "/swagger");
            System.out.println();
            System.out.println("Example:");
            System.out.println("  curl -X POST http://localhost:" + PORT + "/orders \\");
            System.out.println("       -H 'Content-Type: application/json' \\");
            System.out.println("       -d '{\"orderId\":\"ORD-123\",\"total\":99.99,\"customerId\":\"CUST-456\"}'");
            System.out.println();

        } catch (IOException e) {
            System.err.println("Failed to start server: " + e.getMessage());
            e.printStackTrace();
            System.exit(1);
        }
    }
}

