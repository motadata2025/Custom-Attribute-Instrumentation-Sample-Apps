using System.Diagnostics;

namespace WebApplicationCore9.Telemetry;

/// <summary>
/// Central telemetry configuration for the application.
/// This class provides ActivitySource for creating custom spans in business logic.
/// </summary>
public static class AppTelemetry
{
    /// <summary>
    /// The name of the ActivitySource. This must match the value in OTEL_DOTNET_AUTO_TRACES_ADDITIONAL_SOURCES.
    /// </summary>
    public const string SourceName = "WebApplicationCore9.Business";
    
    /// <summary>
    /// The version of the ActivitySource.
    /// </summary>
    public const string SourceVersion = "1.0.0";
    
    /// <summary>
    /// The ActivitySource instance for creating custom spans.
    /// This is a singleton that should be reused throughout the application.
    /// </summary>
    public static readonly ActivitySource ActivitySource = new ActivitySource(SourceName, SourceVersion);
}

