package main

import (
	"context"
	"encoding/json"
	"fmt"
	"io"
	"log"
	"net/http"
	"time"

	"go.opentelemetry.io/otel"
	"go.opentelemetry.io/otel/attribute"
	"go.opentelemetry.io/otel/trace"
)

var tracer trace.Tracer

func init() {
	// Get the global tracer
	// Auto-instrumentation will set up the tracer provider for us
	tracer = otel.Tracer("go-otel-demo")
}

// Handler for the home page - serves HTML with a button
func homeHandler(w http.ResponseWriter, r *http.Request) {
	html := `
	<!DOCTYPE html>
	<html>
	<head>
		<title>OpenTelemetry Demo</title>
	</head>
	<body>
		<h1>OpenTelemetry Go Auto-Instrumentation Demo</h1>
		<button onclick="callAPI()">Click to Call External API</button>
		<button onclick="callTestAttributesAPI()">Test All Attributes</button>
		<div id="result"></div>
		
		<script>
			async function callAPI() {
				const resultDiv = document.getElementById('result');
				resultDiv.innerHTML = 'Loading...';
				
				try {
					const response = await fetch('/api/call');
					const data = await response.json();
					resultDiv.innerHTML = '<pre>' + JSON.stringify(data, null, 2) + '</pre>';
				} catch (error) {
					resultDiv.innerHTML = 'Error: ' + error;
				}
			}

			async function callTestAttributesAPI() {
				const resultDiv = document.getElementById('result');
				resultDiv.innerHTML = 'Testing attributes...';
				
				try {
					const response = await fetch('/api/test-attributes');
					const data = await response.json();
					resultDiv.innerHTML = '<pre>' + JSON.stringify(data, null, 2) + '</pre>';
				} catch (error) {
					resultDiv.innerHTML = 'Error: ' + error;
				}
			}
		</script>
	</body>
	</html>
	`
	w.Header().Set("Content-Type", "text/html")
	w.Write([]byte(html))
}

// Handler that calls external API
func apiCallHandler(w http.ResponseWriter, r *http.Request) {
	ctx := r.Context()

	// Create a custom span to add our attributes
	ctx, span := tracer.Start(ctx, "handle_api_button_click")
	defer span.End()

	// Set custom attributes on the span
	span.SetAttributes(
		attribute.String("user.action", "button_click"),
		attribute.String("operation", "external_api_call"),
		attribute.String("apm.custom.attribute", "demo_value"),
		attribute.String("app.component", "api_handler"),
		attribute.String("apm.business.operation", "fetch_post_data"),
	)

	log.Printf("Button clicked - calling external API")

	// Call external API
	result, err := callExternalAPI(ctx)
	if err != nil {
		span.SetAttributes(
			attribute.Bool("apm.error", true),
			attribute.String("apm.error.message", err.Error()),
		)
		span.RecordError(err)

		log.Printf("Error calling external API: %v", err)
		http.Error(w, fmt.Sprintf("Error: %v", err), http.StatusInternalServerError)
		return
	}

	// Mark success
	span.SetAttributes(
		attribute.Bool("sapm.uccess", true),
		attribute.String("apm.result.type", "json"),
	)

	// Send response
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(result)
}

// Handler for testing all attribute types
func testAttributesHandler(w http.ResponseWriter, r *http.Request) {
	ctx := r.Context()

	// Create a span
	_, span := tracer.Start(ctx, "test_all_attribute_types")
	defer span.End()

	// Set attributes of all requested types
	span.SetAttributes(
		// Primitives
		attribute.Bool("apm.test.bool", true),
		attribute.Int64("apm.test.int64", 9876543210),
		attribute.Float64("apm.test.float64", 123.456),
		attribute.String("apm.test.string", "hello world"),

		// Slices
		attribute.BoolSlice("apm.test.bool_slice", []bool{true, false, true}),
		attribute.Int64Slice("apm.test.int64_slice", []int64{10, 20, 30}),
		attribute.Float64Slice("apm.test.float64_slice", []float64{1.5, 2.5, 3.5}),
		attribute.StringSlice("apm.test.string_slice", []string{"apple", "banana", "cherry"}),
	)

	response := map[string]interface{}{
		"message": "All attribute types set on span",
		"attributes_set": []string{
			"bool", "int64", "float64", "string",
			"[]bool", "[]int64", "[]float64", "[]string",
		},
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(response)
}

// Function that makes the actual external API call
func callExternalAPI(ctx context.Context) (map[string]interface{}, error) {
	// Create a custom span for the external API call logic
	ctx, span := tracer.Start(ctx, "call_external_api")
	defer span.End()

	// Using JSONPlaceholder as a free test API
	apiURL := "https://jsonplaceholder.typicode.com/posts/1"

	// Set custom attributes
	span.SetAttributes(
		attribute.String("apm.external.api.url", apiURL),
		attribute.String("apm.external.api.method", "GET"),
		attribute.String("apm.custom.request.id", "req-12345"),
		attribute.String("apm.external.api.provider", "jsonplaceholder"),
		attribute.String("apm.data.type", "post"),
	)

	// Create HTTP client with timeout
	client := &http.Client{
		Timeout: 10 * time.Second,
	}

	// Create request
	req, err := http.NewRequestWithContext(ctx, "GET", apiURL, nil)
	if err != nil {
		span.RecordError(err)
		span.SetAttributes(attribute.String("apm.error.type", "request_creation_failed"))
		return nil, fmt.Errorf("failed to create request: %w", err)
	}

	// Add custom header
	req.Header.Set("User-Agent", "GoOtelDemo/1.0")

	// Make the request
	startTime := time.Now()
	resp, err := client.Do(req)
	if err != nil {
		span.RecordError(err)
		span.SetAttributes(attribute.String("apm.error.type", "http_request_failed"))
		return nil, fmt.Errorf("failed to call external API: %w", err)
	}
	defer resp.Body.Close()

	duration := time.Since(startTime)

	// Set response attributes
	span.SetAttributes(
		attribute.Int64("apm.external.api.duration_ms", duration.Milliseconds()),
		attribute.Int("apm.external.api.status_code", resp.StatusCode),
		attribute.String("apm.external.api.status", resp.Status),
		attribute.Int64("apm.external.api.response.content_length", resp.ContentLength),
	)

	log.Printf("External API called: status=%d, duration=%dms", resp.StatusCode, duration.Milliseconds())

	// Read response body
	body, err := io.ReadAll(resp.Body)
	if err != nil {
		span.RecordError(err)
		span.SetAttributes(attribute.String("error.type", "response_read_failed"))
		return nil, fmt.Errorf("failed to read response: %w", err)
	}

	span.SetAttributes(
		attribute.Int("apm.external.api.response.body_size_bytes", len(body)),
	)

	// Parse JSON response
	var result map[string]interface{}
	if err := json.Unmarshal(body, &result); err != nil {
		span.RecordError(err)
		span.SetAttributes(attribute.String("apm.error.type", "json_parse_failed"))
		return nil, fmt.Errorf("failed to parse JSON: %w", err)
	}

	// Add some metadata to the response
	result["_metadata"] = map[string]interface{}{
		"duration_ms":           duration.Milliseconds(),
		"status_code":           resp.StatusCode,
		"custom_field":          "This was auto-instrumented!",
		"traced_with_otel":      true,
		"custom_attributes_set": true,
	}

	span.SetAttributes(
		attribute.Bool("apm.response.parsed", true),
	)

	return result, nil
}

func main() {
	// Register handlers
	http.HandleFunc("/", homeHandler)
	http.HandleFunc("/api/call", apiCallHandler)
	http.HandleFunc("/api/test-attributes", testAttributesHandler)

	// Start server
	port := "8082"
	log.Printf("Server starting on port %s", port)
	log.Printf("Open http://localhost:%s in your browser", port)
	log.Printf("Ready for OpenTelemetry auto-instrumentation v0.22.1")

	if err := http.ListenAndServe(":"+port, nil); err != nil {
		log.Fatal(err)
	}
}
