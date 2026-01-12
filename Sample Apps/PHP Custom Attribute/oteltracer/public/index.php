<?php

use App\Config\Database;
use App\Controllers\UserController;
use App\Repositories\UserRepository;
use Dotenv\Dotenv;
use Psr\Http\Message\ResponseInterface as Response;
use Psr\Http\Message\ServerRequestInterface as Request;
use Slim\Factory\AppFactory;
use Slim\Routing\RouteCollectorProxy;
use Slim\Exception\HttpNotFoundException;
use Slim\Exception\HttpMethodNotAllowedException;

// Enable OpenTelemetry auto-instrumentation for trace generation
// If you experience segfaults, you may need to disable this
// putenv('OTEL_PHP_AUTOLOAD_ENABLED=false');

require __DIR__ . '/../vendor/autoload.php';

// Register shutdown handler to catch fatal errors
register_shutdown_function(function() {
    $error = error_get_last();
    if ($error !== null && in_array($error['type'], [E_ERROR, E_CORE_ERROR, E_COMPILE_ERROR, E_PARSE])) {
        http_response_code(500);
        header('Content-Type: application/json');
        echo json_encode([
            'success' => false,
            'error' => 'Fatal Error',
            'message' => $error['message'],
            'file' => $error['file'],
            'line' => $error['line'],
        ], JSON_PRETTY_PRINT);
    }
});

// Load environment variables
$dotenv = Dotenv::createImmutable(__DIR__ . '/..');
$dotenv->load();

// Create Slim App
$app = AppFactory::create();

// Add Error Middleware (first, so it catches everything)
$errorMiddleware = $app->addErrorMiddleware(true, true, true);

// Custom error handler for 404 Not Found
$errorMiddleware->setErrorHandler(
    HttpNotFoundException::class,
    function (Request $request, Throwable $exception, bool $displayErrorDetails) use ($app) {
        $response = $app->getResponseFactory()->createResponse();
        $payload = json_encode([
            'success' => false,
            'error' => 'Not Found',
            'message' => 'The requested resource was not found',
            'path' => $request->getUri()->getPath(),
        ], JSON_PRETTY_PRINT);

        $response->getBody()->write($payload);
        return $response
            ->withHeader('Content-Type', 'application/json')
            ->withStatus(404);
    }
);

// Custom error handler for 405 Method Not Allowed
$errorMiddleware->setErrorHandler(
    HttpMethodNotAllowedException::class,
    function (Request $request, Throwable $exception, bool $displayErrorDetails) use ($app) {
        $response = $app->getResponseFactory()->createResponse();
        $payload = json_encode([
            'success' => false,
            'error' => 'Method Not Allowed',
            'message' => 'The HTTP method is not allowed for this endpoint',
            'path' => $request->getUri()->getPath(),
            'method' => $request->getMethod(),
        ], JSON_PRETTY_PRINT);

        $response->getBody()->write($payload);
        return $response
            ->withHeader('Content-Type', 'application/json')
            ->withStatus(405);
    }
);

// CORS Middleware
$app->add(function (Request $request, $handler) {
    // Handle preflight OPTIONS requests
    if ($request->getMethod() === 'OPTIONS') {
        $response = new \Slim\Psr7\Response();
        return $response
            ->withHeader('Access-Control-Allow-Origin', '*')
            ->withHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization')
            ->withHeader('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
            ->withStatus(200);
    }

    $response = $handler->handle($request);
    return $response
        ->withHeader('Access-Control-Allow-Origin', '*')
        ->withHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        ->withHeader('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS');
});

// Add Body Parsing Middleware
$app->addBodyParsingMiddleware();

// Initialize database connection and dependencies
$database = new Database();
$db = $database->getConnection();
$userRepository = new UserRepository($db);
$userController = new UserController($userRepository);

// Root endpoint - redirect to Swagger UI
$app->get('/', function (Request $request, Response $response) {
    return $response
        ->withHeader('Location', '/swagger')
        ->withStatus(302);
});

// Health check endpoint
$app->get('/health', function (Request $request, Response $response) {
    $payload = json_encode([
        'success' => true,
        'status' => 'healthy',
        'service' => 'php-user-api-slim',
        'timestamp' => date('c'),
    ], JSON_PRETTY_PRINT);

    $response->getBody()->write($payload);
    return $response->withHeader('Content-Type', 'application/json');
});

// Swagger UI endpoint
$app->get('/swagger', function (Request $request, Response $response) {
    $html = file_get_contents(__DIR__ . '/swagger.html');
    $response->getBody()->write($html);
    return $response->withHeader('Content-Type', 'text/html');
});

// OpenAPI specification endpoint
$app->get('/openapi.json', function (Request $request, Response $response) {
    $json = file_get_contents(__DIR__ . '/openapi.json');
    $response->getBody()->write($json);
    return $response->withHeader('Content-Type', 'application/json');
});

// User routes
$app->group('/users', function (RouteCollectorProxy $group) use ($userController) {
    // GET /users - Get all users
    $group->get('', [$userController, 'index']);

    // POST /users - Create a new user
    $group->post('', [$userController, 'store']);

    // GET /users/{id} - Get user by ID
    $group->get('/{id:[0-9]+}', [$userController, 'show']);

    // PUT /users/{id} - Update user
    $group->put('/{id:[0-9]+}', [$userController, 'update']);

    // DELETE /users/{id} - Delete user
    $group->delete('/{id:[0-9]+}', [$userController, 'delete']);
});

// ✅ Approach 2️⃣ - Case B: Background Job (New Trace)
// This endpoint demonstrates creating a ROOT span without parent context
$app->get('/jobs/daily-report', function (Request $request, Response $response) use ($userRepository) {
    try {
        // ✅ APPROACH 2 - CASE B: Create a ROOT span (NEW TRACE)
        // Step 1: Get tracer
        $tracer = \OpenTelemetry\API\Globals::tracerProvider()->getTracer('background-tracer');

        // Step 2: Create span with NO parent (NEW TRACE)
        $rootSpan = $tracer
            ->spanBuilder('daily.user.report')
            ->setParent(false)  // 👈 CRITICAL: setParent(false) creates a NEW TRACE with new TraceID
            ->setSpanKind(\OpenTelemetry\API\Trace\SpanKind::KIND_INTERNAL)
            ->startSpan();

        // Step 3: Set custom attributes AFTER span is started
        $rootSpan->setAttribute('apm.report.type', 'daily_summary');
        $rootSpan->setAttribute('apm.execution.mode', 'batch');
        $rootSpan->setAttribute('apm.job.name', 'DailyUserReport');
        $rootSpan->setAttribute('apm.job.trigger', 'manual');

        // Step 4: Activate the span
        $scope = $rootSpan->storeInContext(\OpenTelemetry\Context\Context::getCurrent())->activate();

        try {
            // Fetch all users
            $users = $userRepository->findAll();

            // Calculate statistics
            $totalUsers = count($users);
            $activeUsers = count(array_filter($users, fn($u) => $u->isActive()));
            $inactiveUsers = $totalUsers - $activeUsers;

            $stats = [
                'total_users' => $totalUsers,
                'active_users' => $activeUsers,
                'inactive_users' => $inactiveUsers,
                'active_percentage' => $totalUsers > 0 ? round(($activeUsers / $totalUsers) * 100, 2) : 0,
            ];

            // Add attributes to the root span
            $rootSpan->setAttribute('apm.report.total_users', $totalUsers);
            $rootSpan->setAttribute('apm.report.active_users', $activeUsers);
            $rootSpan->setAttribute('apm.report.status', 'success');

            $report = [
                'report_date' => date('Y-m-d'),
                'generated_at' => date('c'),
                'statistics' => $stats,
                'status' => 'completed',
            ];

            $payload = json_encode([
                'success' => true,
                'data' => $report,
                'message' => 'Daily report generated successfully',
            ], JSON_PRETTY_PRINT);

            $response->getBody()->write($payload);
            return $response->withHeader('Content-Type', 'application/json');
        } finally {
            // Step 4: Always end the span and detach scope
            $rootSpan->end();
            $scope->detach();
        }
    } catch (\Throwable $e) {
        // Catch any OpenTelemetry errors - application should never crash due to tracing
        error_log("OpenTelemetry error in daily report (ignored): " . $e->getMessage());

        // Return response without tracing
        $users = $userRepository->findAll();
        $totalUsers = count($users);
        $activeUsers = count(array_filter($users, fn($u) => $u->isActive()));

        $payload = json_encode([
            'success' => true,
            'data' => [
                'report_date' => date('Y-m-d'),
                'generated_at' => date('c'),
                'statistics' => [
                    'total_users' => $totalUsers,
                    'active_users' => $activeUsers,
                ],
                'status' => 'completed',
            ],
            'message' => 'Daily report generated successfully (tracing disabled)',
        ], JSON_PRETTY_PRINT);

        $response->getBody()->write($payload);
        return $response->withHeader('Content-Type', 'application/json');
    }
});

// Add Routing Middleware (MUST be added AFTER all routes are defined)
$app->addRoutingMiddleware();

// Run the application with error handling to prevent segfaults
try {
    $app->run();
} catch (\Throwable $e) {
    // Catch any uncaught exceptions to prevent OpenTelemetry segfaults
    http_response_code(500);
    header('Content-Type: application/json');
    echo json_encode([
        'success' => false,
        'error' => 'Internal Server Error',
        'message' => $e->getMessage(),
        'file' => $e->getFile(),
        'line' => $e->getLine(),
    ], JSON_PRETTY_PRINT);
    exit(1);
}

