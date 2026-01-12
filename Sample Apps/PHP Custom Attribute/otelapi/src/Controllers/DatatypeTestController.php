<?php

namespace App\Controllers;

use Psr\Http\Message\ResponseInterface as Response;
use Psr\Http\Message\ServerRequestInterface as Request;
use OpenTelemetry\API\Trace\Span;

/**
 * DatatypeTestController - Tests all OpenTelemetry supported datatypes
 * 
 * This controller demonstrates custom attribute injection with various datatypes:
 * - bool
 * - int
 * - float
 * - string
 * - bool[]
 * - int[]
 * - float[]
 * - string[]
 */
class DatatypeTestController
{
    /**
     * Helper method to add custom attributes to the active span
     * Approach 1: Active Span Enrichment (Same Span)
     */
    private function enrichActiveSpan(array $attributes): void
    {
        try {
            $span = Span::getCurrent();

            if ($span->isRecording()) {
                foreach ($attributes as $key => $value) {
                    $span->setAttribute($key, $value);
                }
            }
        } catch (\Throwable $e) {
            error_log("OpenTelemetry error (ignored): " . $e->getMessage());
        }
    }

    /**
     * Helper method to add span events
     */
    private function addSpanEvent(string $name, array $attributes = []): void
    {
        try {
            $span = Span::getCurrent();
            if ($span->isRecording()) {
                $span->addEvent($name, $attributes);
            }
        } catch (\Throwable $e) {
            error_log("OpenTelemetry error (ignored): " . $e->getMessage());
        }
    }

    /**
     * Helper method to set span status
     */
    private function setSpanStatus(string $code, string $description = ''): void
    {
        try {
            $span = Span::getCurrent();
            if ($span->isRecording()) {
                if (class_exists('OpenTelemetry\API\Trace\StatusCode')) {
                    $statusCode = constant('OpenTelemetry\API\Trace\StatusCode::' . $code);
                    $span->setStatus($statusCode, $description);
                } else {
                    $span->setStatus($code, $description);
                }
            }
        } catch (\Throwable $e) {
            error_log("OpenTelemetry error (ignored): " . $e->getMessage());
        }
    }

    /**
     * GET /test/datatypes - Test all OpenTelemetry supported datatypes
     * 
     * This endpoint tests custom attribute injection with all supported datatypes:
     * - Scalar types: bool, int, float, string
     * - Array types: bool[], int[], float[], string[]
     */
    public function testDatatypes(Request $request, Response $response): Response
    {
        // Add event for test start
        $this->addSpanEvent('datatype.test.start', [
            'test.type' => 'all_datatypes',
        ]);

        // Test all datatypes as custom attributes
        $this->enrichActiveSpan([
            // Scalar types
            'apm.test.bool.true' => true,
            'apm.test.bool.false' => false,
            'apm.test.int.positive' => 42,
            'apm.test.int.negative' => -100,
            'apm.test.int.zero' => 0,
            'apm.test.float.positive' => 3.14159,
            'apm.test.float.negative' => -99.99,
            'apm.test.float.zero' => 0.0,
            'apm.test.string.simple' => 'Hello OpenTelemetry',
            'apm.test.string.empty' => '',
            'apm.test.string.special' => 'Special chars: @#$%^&*()',

            // Array types
            'apm.test.bool.array' => [true, false, true, true, false],
            'apm.test.int.array' => [1, 2, 3, 4, 5, -10, 0, 100],
            'apm.test.float.array' => [1.1, 2.2, 3.3, -4.4, 0.0, 99.99],
            'apm.test.string.array' => ['apple', 'banana', 'cherry', 'date', 'elderberry'],

            // Additional metadata
            'apm.test.operation.type' => 'datatype_validation',
            'apm.test.endpoint' => '/test/datatypes',
            'apm.test.http.method' => 'GET',
            'apm.test.timestamp' => time(),
        ]);

        // Set span status to success
        $this->setSpanStatus('STATUS_OK', 'All datatypes tested successfully');

        // Add event for test completion
        $this->addSpanEvent('datatype.test.complete', [
            'test.result' => 'success',
            'datatypes.tested' => 8,
        ]);

        // Prepare response with all tested values
        $payload = json_encode([
            'success' => true,
            'message' => 'All OpenTelemetry datatypes tested successfully',
            'tested_datatypes' => [
                'scalar' => [
                    'bool' => ['true' => true, 'false' => false],
                    'int' => ['positive' => 42, 'negative' => -100, 'zero' => 0],
                    'float' => ['positive' => 3.14159, 'negative' => -99.99, 'zero' => 0.0],
                    'string' => ['simple' => 'Hello OpenTelemetry', 'empty' => '', 'special' => 'Special chars: @#$%^&*()'],
                ],
                'arrays' => [
                    'bool[]' => [true, false, true, true, false],
                    'int[]' => [1, 2, 3, 4, 5, -10, 0, 100],
                    'float[]' => [1.1, 2.2, 3.3, -4.4, 0.0, 99.99],
                    'string[]' => ['apple', 'banana', 'cherry', 'date', 'elderberry'],
                ],
            ],
            'timestamp' => date('c'),
        ], JSON_PRETTY_PRINT);

        $response->getBody()->write($payload);
        return $response->withHeader('Content-Type', 'application/json');
    }
}

