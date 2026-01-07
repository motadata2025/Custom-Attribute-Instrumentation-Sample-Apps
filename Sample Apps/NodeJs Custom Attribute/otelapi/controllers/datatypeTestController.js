const { trace } = require('@opentelemetry/api');

class DatatypeTestController {
  static async testDataTypes(req, res) {
    const span = trace.getActiveSpan();

    if (!span) {
      return res.status(500).json({
        success: false,
        message: 'No active span found. OpenTelemetry may not be initialized.'
      });
    }

    // Test the 6 supported data types
    // 1. string
    span.setAttribute('apm.test.string', 'test-string-value');

    // 2. number
    span.setAttribute('apm.test.number', 42);

    // 3. boolean
    span.setAttribute('apm.test.boolean', true);

    // 4. string[]
    span.setAttribute('apm.test.stringArray', ['value1', 'value2', 'value3']);

    // 5. number[]
    span.setAttribute('apm.test.numberArray', [1, 2, 3, 4, 5]);

    // 6. boolean[]
    span.setAttribute('apm.test.booleanArray', [true, false, true]);

    res.status(200).json({
      success: true,
      message: 'Data type testing completed',
      attributes_set: {
        'apm.test.string': 'test-string-value',
        'apm.test.number': 42,
        'apm.test.boolean': true,
        'apm.test.stringArray': ['value1', 'value2', 'value3'],
        'apm.test.numberArray': [1, 2, 3, 4, 5],
        'apm.test.booleanArray': [true, false, true]
      },
      supported_types: ['string', 'number', 'boolean', 'string[]', 'number[]', 'boolean[]']
    });
  }
}

module.exports = DatatypeTestController;