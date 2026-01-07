"""
OpenTelemetry configuration for Manual Tracer approach

This module demonstrates:
- Auto-instrumentation for Flask and PostgreSQL (creates base spans)
- Manual tracer creation for custom span hierarchies
- Full control over span lifecycle
"""
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.psycopg2 import Psycopg2Instrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor


def setup_opentelemetry(app, service_name="PythonCustomAttributesTracer"):
    """
    Setup OpenTelemetry with auto-instrumentation and manual tracer
    
    Args:
        app: Flask application instance
        service_name: Name of the service for tracing
    """
    # Create resource with service name
    resource = Resource(attributes={
        "service.name": service_name,
        "service.version": "1.0.0",
        "deployment.environment": "development"
    })
    
    # Set up the tracer provider
    provider = TracerProvider(resource=resource)
    
    # Configure OTLP exporter (sends to Jaeger via OTLP)
    otlp_exporter = OTLPSpanExporter(
        endpoint="http://localhost:4317",  # Jaeger OTLP endpoint
        insecure=True
    )
    
    # Add span processor
    provider.add_span_processor(BatchSpanProcessor(otlp_exporter))
    
    # Set the global tracer provider
    trace.set_tracer_provider(provider)
    
    # Auto-instrument Flask (creates HTTP spans automatically)
    FlaskInstrumentor().instrument_app(app)
    
    # Auto-instrument PostgreSQL (creates DB spans automatically)
    Psycopg2Instrumentor().instrument()
    
    # Auto-instrument requests library (if making external HTTP calls)
    RequestsInstrumentor().instrument()
    
    print(f"✅ OpenTelemetry initialized for service: {service_name}")
    print(f"📊 Exporting traces to: http://localhost:4317 (OTLP)")
    print(f"🔍 View traces at: http://localhost:16686 (Jaeger UI)")
    print(f"🎯 Method: Manual Tracer & Span Creation (Method 3)")

