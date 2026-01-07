# OpenTelemetry Zero-Code Instrumentation Setup Script for Windows PowerShell
# This script sets up environment variables for custom ActivitySource instrumentation

Write-Host "Setting up OpenTelemetry environment variables for Windows..." -ForegroundColor Green

# Register custom ActivitySource with OpenTelemetry auto-instrumentation
$env:OTEL_DOTNET_AUTO_TRACES_ADDITIONAL_SOURCES = "WebApplicationCore9.Business"

# Optional: Configure OpenTelemetry exporter (uncomment and modify as needed)
# $env:OTEL_EXPORTER_OTLP_ENDPOINT = "http://localhost:4317"
# $env:OTEL_SERVICE_NAME = "WebApplicationCore9"
# $env:OTEL_RESOURCE_ATTRIBUTES = "deployment.environment=development"

Write-Host "✅ Environment variables set successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "Registered ActivitySources:" -ForegroundColor Cyan
Write-Host "  - WebApplicationCore9.Business"
Write-Host ""
Write-Host "To verify, run: `$env:OTEL_DOTNET_AUTO_TRACES_ADDITIONAL_SOURCES" -ForegroundColor Yellow
Write-Host ""
Write-Host "Note: These variables are set for the current PowerShell session only." -ForegroundColor Yellow
Write-Host "To make them permanent, use:" -ForegroundColor Yellow
Write-Host "  [System.Environment]::SetEnvironmentVariable('OTEL_DOTNET_AUTO_TRACES_ADDITIONAL_SOURCES', 'WebApplicationCore9.Business', 'User')" -ForegroundColor Gray
Write-Host ""
Write-Host "Now you can run your application with:" -ForegroundColor Cyan
Write-Host "  dotnet run --project WebApplicationCore9\WebApplicationCore9.csproj"

