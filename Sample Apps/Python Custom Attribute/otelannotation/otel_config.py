"""
OpenTelemetry configuration and initialization
"""
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.psycopg2 import Psycopg2Instrumentor
from opentelemetry.semconv.resource import ResourceAttributes
import os

def init_telemetry(app):
    """
    Initialize OpenTelemetry instrumentation
    
    Args:
        app: Flask application instance
    """
    # Create resource with service information
    resource = Resource(attributes={
        ResourceAttributes.SERVICE_NAME: "otelannotation-service",
        ResourceAttributes.SERVICE_VERSION: "1.0.0",
        ResourceAttributes.DEPLOYMENT_ENVIRONMENT: os.getenv("ENVIRONMENT", "development"),
        "service.instance.id": os.getenv("HOSTNAME", "localhost"),
    })
    
    # Create tracer provider
    provider = TracerProvider(resource=resource)
    
    # Configure exporters
    # Console exporter for development
    console_exporter = ConsoleSpanExporter()
    provider.add_span_processor(BatchSpanProcessor(console_exporter))
    
    # OTLP exporter (uncomment when you have a collector running)
    # otlp_exporter = OTLPSpanExporter(
    #     endpoint=os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4317"),
    #     insecure=True
    # )
    # provider.add_span_processor(BatchSpanProcessor(otlp_exporter))
    
    # Set global tracer provider
    trace.set_tracer_provider(provider)
    
    # Auto-instrument Flask
    FlaskInstrumentor().instrument_app(app)
    
    # Auto-instrument Psycopg2
    Psycopg2Instrumentor().instrument()
    
    print("✅ OpenTelemetry instrumentation initialized successfully")
    print(f"   Service Name: otelannotation-service")
    print(f"   Environment: {os.getenv('ENVIRONMENT', 'development')}")
    print(f"   Exporters: Console (active), OTLP (commented)")

def get_tracer(name=__name__):
    """
    Get a tracer instance
    
    Args:
        name: Name for the tracer (typically __name__)
        
    Returns:
        Tracer instance
    """
    return trace.get_tracer(name)

