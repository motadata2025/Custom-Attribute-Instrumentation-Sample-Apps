const { trace } = require('@opentelemetry/api');

/**
 * Utility for adding custom attributes to OpenTelemetry spans.
 * All attribute keys are prefixed with "apm.".
 *
 * Supports only OpenTelemetry-compatible types:
 * string, number, boolean, string[], number[], boolean[]
 *
 * This class is thread-safe and exception-safe.
 * All methods silently ignore null values and will never throw exceptions.
 *
 * @since 1.0
 */
class MotadataDynamicInstrumentation {
  static DEFAULT_PREFIX = 'apm.';

  /**
   * Private helper to prefix keys with "apm."
   * @param {string} key - The attribute key
   * @returns {string|null} Prefixed key or null if invalid
   */
  static prefixKey(key) {
    try {
      if (key == null) {
        return null;
      }

      return key.startsWith(this.DEFAULT_PREFIX) ? key : this.DEFAULT_PREFIX + key;
    } catch (exception) {
      return null;
    }
  }

  /**
   * Core helper method to validate key and set attribute.
   * Executes the provided setter action if key is valid.
   *
   * @param {string} key - The attribute key
   * @param {*} value - The attribute value (for null check)
   * @param {Function} setter - The action to execute if validation passes
   */
  static safeSet(key, value, setter) {
    try {
      if (key == null || value == null) {
        return;
      }

      const prefixed = this.prefixKey(key);

      if (prefixed == null) {
        return;
      }

      // Pass prefixed key to setter to avoid calling prefixKey twice
      setter(prefixed);
    } catch (exception) {
      // Ignore all exceptions
    }
  }

  /**
   * Sets a String, Number, or Boolean attribute on the current span.
   *
   * @param {string} key - The attribute key
   * @param {string|number|boolean} value - The attribute value
   */
  static set(key, value) {
    // Handle string type
    if (typeof value === 'string') {
      this.safeSet(key, value, (prefixed) => {
        const span = trace.getActiveSpan();
        if (span) {
          span.setAttribute(prefixed, value);
        }
      });
    }
    // Handle number type
    else if (typeof value === 'number') {
      this.safeSet(key, value, (prefixed) => {
        const span = trace.getActiveSpan();
        if (span) {
          span.setAttribute(prefixed, value);
        }
      });
    }
    // Handle boolean type
    else if (typeof value === 'boolean') {
      this.safeSet(key, value, (prefixed) => {
        const span = trace.getActiveSpan();
        if (span) {
          span.setAttribute(prefixed, value);
        }
      });
    }
  }

  /**
   * Sets a List of Boolean values attribute on the current span.
   *
   * @param {string} key - The attribute key
   * @param {boolean[]} value - The list of boolean values
   */
  static setBooleanList(key, value) {
    try {
      if (key == null || value == null || !Array.isArray(value) || value.length === 0) {
        return;
      }

      const prefixed = this.prefixKey(key);

      if (prefixed == null) {
        return;
      }

      const span = trace.getActiveSpan();
      if (span) {
        span.setAttribute(prefixed, value);
      }
    } catch (exception) {
      // Ignore all exceptions
    }
  }

  /**
   * Sets a List of Number values attribute on the current span.
   *
   * @param {string} key - The attribute key
   * @param {number[]} value - The list of number values
   */
  static setNumberList(key, value) {
    try {
      if (key == null || value == null || !Array.isArray(value) || value.length === 0) {
        return;
      }

      const prefixed = this.prefixKey(key);

      if (prefixed == null) {
        return;
      }

      const span = trace.getActiveSpan();
      if (span) {
        span.setAttribute(prefixed, value);
      }
    } catch (exception) {
      // Ignore all exceptions
    }
  }

  /**
   * Sets a List of String values attribute on the current span.
   *
   * @param {string} key - The attribute key
   * @param {string[]} value - The list of string values
   */
  static setStringList(key, value) {
    try {
      if (key == null || value == null || !Array.isArray(value) || value.length === 0) {
        return;
      }

      const prefixed = this.prefixKey(key);

      if (prefixed == null) {
        return;
      }

      const span = trace.getActiveSpan();
      if (span) {
        span.setAttribute(prefixed, value);
      }
    } catch (exception) {
      // Ignore all exceptions
    }
  }
}

module.exports = MotadataDynamicInstrumentation;

