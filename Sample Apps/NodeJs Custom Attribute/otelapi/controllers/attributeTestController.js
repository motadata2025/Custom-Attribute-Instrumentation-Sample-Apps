const { trace } = require('@opentelemetry/api');
const MotadataDynamicInstrumentation = require('../util/MotadataDynamicInstrumentation');

class AttributeTestController {
  /**
   * Test all supported data types using MotadataDynamicInstrumentation utility
   * GET /attributes/test
   */
  static async testAttributes(req, res) {
    const span = trace.getActiveSpan();

    if (!span) {
      return res.status(500).json({
        success: false,
        message: 'No active span found. OpenTelemetry may not be initialized.'
      });
    }

    try {
      // Test 1: String
      MotadataDynamicInstrumentation.set('test.string', 'Hello OpenTelemetry');
      
      // Test 2: Number (integer)
      MotadataDynamicInstrumentation.set('test.number.integer', 42);
      
      // Test 3: Number (decimal)
      MotadataDynamicInstrumentation.set('test.number.decimal', 3.14159);
      
      // Test 4: Boolean (true)
      MotadataDynamicInstrumentation.set('test.boolean.true', true);
      
      // Test 5: Boolean (false)
      MotadataDynamicInstrumentation.set('test.boolean.false', false);
      
      // Test 6: String Array
      MotadataDynamicInstrumentation.setStringList('test.array.strings', [
        'apple',
        'banana',
        'cherry'
      ]);
      
      // Test 7: Number Array
      MotadataDynamicInstrumentation.setNumberList('test.array.numbers', [
        1, 2, 3, 4, 5
      ]);
      
      // Test 8: Boolean Array
      MotadataDynamicInstrumentation.setBooleanList('test.array.booleans', [
        true, false, true, false
      ]);

      // Test edge cases (should be safely ignored)
      MotadataDynamicInstrumentation.set('test.null', null); // Should be ignored
      MotadataDynamicInstrumentation.set(null, 'value'); // Should be ignored
      MotadataDynamicInstrumentation.setStringList('test.empty.array', []); // Should be ignored

      res.status(200).json({
        success: true,
        message: 'All data types tested successfully using MotadataDynamicInstrumentation',
        attributes_set: {
          'apm.test.string': 'Hello OpenTelemetry',
          'apm.test.number.integer': 42,
          'apm.test.number.decimal': 3.14159,
          'apm.test.boolean.true': true,
          'apm.test.boolean.false': false,
          'apm.test.array.strings': ['apple', 'banana', 'cherry'],
          'apm.test.array.numbers': [1, 2, 3, 4, 5],
          'apm.test.array.booleans': [true, false, true, false]
        },
        supported_types: [
          'string',
          'number',
          'boolean',
          'string[]',
          'number[]',
          'boolean[]'
        ],
        edge_cases_tested: [
          'null value (ignored)',
          'null key (ignored)',
          'empty array (ignored)'
        ],
        note: 'All attributes are prefixed with "apm." automatically'
      });
    } catch (error) {
      console.error('Error in testAttributes:', error);
      
      res.status(500).json({
        success: false,
        message: 'Error testing attributes',
        error: error.message
      });
    }
  }
}

module.exports = AttributeTestController;

