<?php

use App\Config\Database;
use App\Controllers\UserController;
use App\Controllers\DatatypeTestController;
use App\Repositories\UserRepository;
use Dotenv\Dotenv;
use Psr\Http\Message\ResponseInterface as Response;
use Psr\Http\Message\ServerRequestInterface as Request;
use Slim\Factory\AppFactory;
use Slim\Routing\RouteCollectorProxy;

require __DIR__ . '/../vendor/autoload.php';

// Load environment variables
$dotenv = Dotenv::createImmutable(__DIR__ . '/..');
$dotenv->load();

// Create Slim App
$app = AppFactory::create();

// Add Error Middleware
$errorMiddleware = $app->addErrorMiddleware(true, true, true);

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
$datatypeTestController = new DatatypeTestController();

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

// Swagger UI endpoint (alternative with .html extension)
$app->get('/swagger.html', function (Request $request, Response $response) {
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

// Test routes for OpenTelemetry datatype validation
$app->group('/test', function (RouteCollectorProxy $group) use ($datatypeTestController) {
    // GET /test/datatypes - Test all supported datatypes
    $group->get('/datatypes', [$datatypeTestController, 'testDatatypes']);
});

// Add Routing Middleware (MUST be added AFTER all routes are defined)
$app->addRoutingMiddleware();

// Run the application
$app->run();

