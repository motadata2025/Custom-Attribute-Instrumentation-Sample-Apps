@echo off
REM OpenTelemetry Zero-Code Instrumentation Setup Script for Windows Command Prompt
REM This script sets up environment variables for custom ActivitySource instrumentation

echo Setting up OpenTelemetry environment variables for Windows...
echo.

REM Register custom ActivitySource with OpenTelemetry auto-instrumentation
set OTEL_DOTNET_AUTO_TRACES_ADDITIONAL_SOURCES=WebApplicationCore9.Business

REM Optional: Configure OpenTelemetry exporter (uncomment and modify as needed)
REM set OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317
REM set OTEL_SERVICE_NAME=WebApplicationCore9
REM set OTEL_RESOURCE_ATTRIBUTES=deployment.environment=development

echo ✅ Environment variables set successfully!
echo.
echo Registered ActivitySources:
echo   - WebApplicationCore9.Business
echo.
echo To verify, run: echo %OTEL_DOTNET_AUTO_TRACES_ADDITIONAL_SOURCES%
echo.
echo Note: These variables are set for the current command prompt session only.
echo To make them permanent, use System Properties ^> Environment Variables
echo.
echo Now you can run your application with:
echo   dotnet run --project WebApplicationCore9\WebApplicationCore9.csproj
echo.
pause

