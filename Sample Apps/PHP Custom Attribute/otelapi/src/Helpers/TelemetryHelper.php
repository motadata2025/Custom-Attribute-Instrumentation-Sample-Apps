<?php

namespace App\Helpers;

use OpenTelemetry\API\Trace\Span;

/**
 * TelemetryHelper - Helper class for adding custom attributes to OpenTelemetry traces
 *
 * This class implements Method 1: Active Span Enrichment
 * It adds custom attributes to the currently active span without creating new spans.
 */
class TelemetryHelper
{
    /**
     * Active Span Enrichment
     *
     * Adds custom attributes to the currently active span created by auto-instrumentation.
     * This does NOT create a new span - it enriches the existing one.
     *
     * Use this when:
     * - You want to add business metadata to traces
     * - You want zero visual noise in the trace UI
     * - You don't need a separate logical operation
     * - You want to enrich HTTP request spans with custom data
     *
     * IMPORTANT: Wrapped in try-catch to prevent OpenTelemetry errors from crashing the application
     *
     * @param array<string, mixed> $attributes Key-value pairs to add to the active span
     */
    public function enrichActiveSpan(array $attributes): void
    {
        try {
            $span = Span::getCurrent();

            if ($span->isRecording()) {
                foreach ($attributes as $key => $value) {
                    $span->setAttribute($key, $value);
                }
            }
        } catch (\Throwable $e) {
            // Silently ignore OpenTelemetry errors - application should never crash due to tracing
            // Optionally log the error for debugging
            error_log("OpenTelemetry error in TelemetryHelper (ignored): " . $e->getMessage());
        }
    }
}

