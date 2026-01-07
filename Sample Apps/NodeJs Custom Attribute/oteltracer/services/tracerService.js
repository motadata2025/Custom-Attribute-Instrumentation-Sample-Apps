/**
 * Tracer Service for Method 2: Span Creation
 * 
 * This service provides a centralized tracer instance for creating custom spans
 * with full control over span lifecycle, attributes, events, and status.
 */

const { trace, SpanStatusCode, SpanKind } = require('@opentelemetry/api');

class TracerService {
  constructor() {
    // Get a tracer instance for this service
    // The tracer name should match your service name
    this.tracer = trace.getTracer('oteltracer-service', '1.0.0');
  }

  /**
   * Get the tracer instance
   * @returns {Tracer} OpenTelemetry tracer
   */
  getTracer() {
    return this.tracer;
  }

  /**
   * Execute a function within a custom span
   * This is a helper method that handles span lifecycle automatically
   * 
   * @param {string} spanName - Name of the span
   * @param {Function} fn - Async function to execute within the span
   * @param {Object} options - Span options (kind, attributes, etc.)
   * @returns {Promise<any>} Result of the function
   */
  async executeInSpan(spanName, fn, options = {}) {
    return this.tracer.startActiveSpan(spanName, options, async (span) => {
      try {
        // Add initial attributes if provided
        if (options.attributes) {
          Object.entries(options.attributes).forEach(([key, value]) => {
            span.setAttribute(key, value);
          });
        }

        // Execute the function
        const result = await fn(span);

        // Set success status
        span.setStatus({ code: SpanStatusCode.OK });
        
        return result;
      } catch (error) {
        // Record the exception
        span.recordException(error);
        
        // Set error status
        span.setStatus({
          code: SpanStatusCode.ERROR,
          message: error.message
        });
        
        // Add error attributes
        span.setAttribute('apm.error.occurred', true);
        span.setAttribute('apm.error.message', error.message);
        span.setAttribute('apm.error.type', error.constructor.name);
        
        // Re-throw the error
        throw error;
      } finally {
        // Always end the span
        span.end();
      }
    });
  }

  /**
   * Create a manual span (non-active)
   * Use this when you need more control over the span lifecycle
   * 
   * @param {string} spanName - Name of the span
   * @param {Object} options - Span options
   * @returns {Span} OpenTelemetry span
   */
  createSpan(spanName, options = {}) {
    return this.tracer.startSpan(spanName, options);
  }

  /**
   * Helper to add common APM attributes to a span
   * 
   * @param {Span} span - OpenTelemetry span
   * @param {Object} metadata - Metadata object
   */
  addCommonAttributes(span, metadata = {}) {
    const {
      operation,
      controller,
      method,
      endpoint,
      userId,
      username,
      ...customAttributes
    } = metadata;

    if (operation) span.setAttribute('apm.operation', operation);
    if (controller) span.setAttribute('apm.controller', controller);
    if (method) span.setAttribute('apm.method', method);
    if (endpoint) span.setAttribute('apm.endpoint', endpoint);
    if (userId) span.setAttribute('apm.user.id', userId);
    if (username) span.setAttribute('apm.user.username', username);

    // Add any additional custom attributes
    Object.entries(customAttributes).forEach(([key, value]) => {
      span.setAttribute(key, value);
    });
  }

  /**
   * Add success attributes to a span
   * 
   * @param {Span} span - OpenTelemetry span
   * @param {number} statusCode - HTTP status code
   * @param {Object} data - Additional data to add as attributes
   */
  addSuccessAttributes(span, statusCode = 200, data = {}) {
    span.setAttribute('apm.result.success', true);
    span.setAttribute('apm.http.status_code', statusCode);
    
    Object.entries(data).forEach(([key, value]) => {
      span.setAttribute(key, value);
    });
  }

  /**
   * Add error attributes to a span
   * 
   * @param {Span} span - OpenTelemetry span
   * @param {Error} error - Error object
   * @param {number} statusCode - HTTP status code
   */
  addErrorAttributes(span, error, statusCode = 500) {
    span.setAttribute('apm.result.success', false);
    span.setAttribute('apm.error.occurred', true);
    span.setAttribute('apm.error.message', error.message);
    span.setAttribute('apm.error.type', error.constructor.name);
    span.setAttribute('apm.http.status_code', statusCode);
    
    // Record the exception
    span.recordException(error);
    
    // Set error status
    span.setStatus({
      code: SpanStatusCode.ERROR,
      message: error.message
    });
  }
}

// Export a singleton instance
module.exports = new TracerService();

