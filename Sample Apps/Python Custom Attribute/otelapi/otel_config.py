"""
OpenTelemetry configuration for API-based instrumentation

This module sets up OpenTelemetry with OTLP exporter for Jaeger.
API-BASED APPROACH - No decorators, enriches existing auto-instrumented spans
"""
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.instrumentation.psycopg2 import Psycopg2Instrumentor

def setup_opentelemetry(app, service_name="PythonCustomAttributesAPI"):
    """
    Setup OpenTelemetry with OTLP exporter for Jaeger
    
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
    
    # Create tracer provider
    provider = TracerProvider(resource=resource)
    
    # Configure OTLP exporter (Jaeger supports OTLP)
    otlp_exporter = OTLPSpanExporter(
        endpoint="http://localhost:4317",  # Jaeger OTLP gRPC endpoint
        insecure=True
    )
    
    # Add span processor
    processor = BatchSpanProcessor(otlp_exporter)
    provider.add_span_processor(processor)
    
    # Set global tracer provider
    trace.set_tracer_provider(provider)
    
    # Auto-instrument Flask (creates HTTP spans automatically)
    # FlaskInstrumentor().instrument_app(app)
    
    # Auto-instrument requests library
    # RequestsInstrumentor().instrument()
    
    # Auto-instrument PostgreSQL
    # Psycopg2Instrumentor().instrument()
    
    print(f"✅ OpenTelemetry initialized for service: {service_name}")
    print(f"📊 Exporting traces to: http://localhost:4317 (OTLP)")
    print(f"🔍 View traces at: http://localhost:16686 (Jaeger UI)")

def get_tracer(name=__name__):
    """
    Get a tracer instance
    
    Args:
        name: Name for the tracer (typically __name__)
        
    Returns:
        Tracer instance
    """
    return trace.get_tracer(name)
