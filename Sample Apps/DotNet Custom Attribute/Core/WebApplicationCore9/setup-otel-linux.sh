#!/bin/bash

# OpenTelemetry Zero-Code Instrumentation Setup Script for Linux/macOS
# This script sets up environment variables for custom ActivitySource instrumentation

echo "Setting up OpenTelemetry environment variables for Linux/macOS..."

# Register custom ActivitySource with OpenTelemetry auto-instrumentation
export OTEL_DOTNET_AUTO_TRACES_ADDITIONAL_SOURCES="WebApplicationCore9.Business"

# Optional: Configure OpenTelemetry exporter (uncomment and modify as needed)
# export OTEL_EXPORTER_OTLP_ENDPOINT="http://localhost:4317"
# export OTEL_SERVICE_NAME="WebApplicationCore9"
# export OTEL_RESOURCE_ATTRIBUTES="deployment.environment=development"

echo "✅ Environment variables set successfully!"
echo ""
echo "Registered ActivitySources:"
echo "  - WebApplicationCore9.Business"
echo ""
echo "To verify, run: echo \$OTEL_DOTNET_AUTO_TRACES_ADDITIONAL_SOURCES"
echo ""
echo "To make these permanent, add the export commands to your ~/.bashrc or ~/.zshrc file"
echo ""
echo "Now you can run your application with:"
echo "  dotnet run --project WebApplicationCore9/WebApplicationCore9.csproj"

