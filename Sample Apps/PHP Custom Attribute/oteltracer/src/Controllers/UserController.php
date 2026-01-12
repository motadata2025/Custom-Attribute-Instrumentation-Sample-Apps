<?php

namespace App\Controllers;

use App\Models\User;
use App\Repositories\UserRepository;
use Exception;
use OpenTelemetry\API\Globals;
use OpenTelemetry\API\Trace\SpanKind;
use OpenTelemetry\Context\Context;
use Psr\Http\Message\ResponseInterface as Response;
use Psr\Http\Message\ServerRequestInterface as Request;

/**
 * UserController - Demonstrates Approach 2️⃣: Tracer-Based Span Creation
 *
 * This controller implements Method 2 from methods.md:
 * - Case A: Creating child spans in the SAME TRACE (with parent context using setParent(Context::getCurrent()))
 * - Case B: Creating root spans in a NEW TRACE (with setParent(false) - see /jobs/daily-report endpoint in index.php)
 */
class UserController
{
    private UserRepository $userRepository;

    public function __construct(UserRepository $userRepository)
    {
        $this->userRepository = $userRepository;
    }

    /**
     * GET /users - Get all users
     *
     * ✅ Approach 2️⃣ - Case A: Tracer-Based Child Span (Same Trace)
     *
     * Demonstrates creating child spans for list/query operations.
     */
    public function index(Request $request, Response $response): Response
    {
        $queryParams = $request->getQueryParams();
        $filters = [];

        if (isset($queryParams['is_active'])) {
            $filters['is_active'] = filter_var($queryParams['is_active'], FILTER_VALIDATE_BOOLEAN);
        }

        // ✅ APPROACH 2 - CASE A: Create a child span for user list operation
        $tracer = Globals::tracerProvider()->getTracer('business-tracer');

        $listSpan = $tracer
            ->spanBuilder('user.list')
            ->setParent(Context::getCurrent())
            ->setSpanKind(SpanKind::KIND_INTERNAL)
            ->startSpan();

        $listSpan->setAttribute('apm.operation.type', 'list');
        $listSpan->setAttribute('apm.db.operation', 'SELECT');
        $listSpan->setAttribute('apm.query.has_filters', !empty($filters));

        if (!empty($filters)) {
            $listSpan->setAttribute('apm.query.filters', json_encode($filters));
        }

        $listScope = $listSpan->storeInContext(Context::getCurrent())->activate();

        try {
            $users = $this->userRepository->findAll($filters);

            $listSpan->setAttribute('apm.operation.status', 'success');
            $listSpan->setAttribute('apm.result.count', count($users));

            $payload = json_encode([
                'success' => true,
                'data' => $users,
                'count' => count($users),
            ], JSON_PRETTY_PRINT);

            $response->getBody()->write($payload);
            return $response->withHeader('Content-Type', 'application/json');
        } catch (Exception $e) {
            $listSpan->setAttribute('apm.operation.status', 'failed');
            $listSpan->setAttribute('apm.error.message', $e->getMessage());
            throw $e;
        } finally {
            $listSpan->end();
            $listScope->detach();
        }
    }

    /**
     * GET /users/{id} - Get user by ID
     *
     * ✅ Approach 2️⃣ - Case A: Tracer-Based Child Span (Same Trace)
     *
     * Demonstrates creating child spans for single record retrieval.
     */
    public function show(Request $request, Response $response, array $args): Response
    {
        $id = (int) $args['id'];

        // ✅ APPROACH 2 - CASE A: Create a child span for user retrieval
        $tracer = Globals::tracerProvider()->getTracer('business-tracer');

        $getSpan = $tracer
            ->spanBuilder('user.get')
            ->setParent(Context::getCurrent())
            ->setSpanKind(SpanKind::KIND_INTERNAL)
            ->startSpan();

        $getSpan->setAttribute('apm.user.id', $id);
        $getSpan->setAttribute('apm.operation.type', 'get');
        $getSpan->setAttribute('apm.db.operation', 'SELECT');

        $getScope = $getSpan->storeInContext(Context::getCurrent())->activate();

        try {
            $user = $this->userRepository->findById($id);

            if (!$user) {
                $getSpan->setAttribute('apm.operation.status', 'not_found');
                $getSpan->setAttribute('apm.result.found', false);

                $payload = json_encode([
                    'success' => false,
                    'error' => 'User not found',
                ], JSON_PRETTY_PRINT);

                $response->getBody()->write($payload);
                return $response
                    ->withHeader('Content-Type', 'application/json')
                    ->withStatus(404);
            }

            $getSpan->setAttribute('apm.operation.status', 'success');
            $getSpan->setAttribute('apm.result.found', true);
            $getSpan->setAttribute('apm.user.username', $user->getUsername());
            $getSpan->setAttribute('apm.user.email', $user->getEmail());

            $payload = json_encode([
                'success' => true,
                'data' => $user,
            ], JSON_PRETTY_PRINT);

            $response->getBody()->write($payload);
            return $response->withHeader('Content-Type', 'application/json');
        } catch (Exception $e) {
            $getSpan->setAttribute('apm.operation.status', 'failed');
            $getSpan->setAttribute('apm.error.message', $e->getMessage());
            throw $e;
        } finally {
            $getSpan->end();
            $getScope->detach();
        }
    }

    /**
     * POST /users - Create a new user
     *
     * ✅ Approach 2️⃣ - Case A: Tracer-Based Child Span (Same Trace)
     *
     * Demonstrates creating child spans using a tracer with parent context.
     * The spans will be children of the HTTP request span created by auto-instrumentation.
     */
    public function store(Request $request, Response $response): Response
    {
        $data = $request->getParsedBody();

        if (!$data) {
            $payload = json_encode([
                'success' => false,
                'error' => 'Invalid JSON data',
            ], JSON_PRETTY_PRINT);

            $response->getBody()->write($payload);
            return $response
                ->withHeader('Content-Type', 'application/json')
                ->withStatus(400);
        }

        // Validate required fields
        if (empty($data['username']) || empty($data['email'])) {
            $payload = json_encode([
                'success' => false,
                'error' => 'Username and email are required',
            ], JSON_PRETTY_PRINT);

            $response->getBody()->write($payload);
            return $response
                ->withHeader('Content-Type', 'application/json')
                ->withStatus(400);
        }

        // ✅ APPROACH 2 - CASE A: Create a child span for user validation
        // Step 1: Get tracer from global provider
        $tracer = Globals::tracerProvider()->getTracer('business-tracer');

        // Step 2: Create span with parent context (SAME TRACE)
        $validationSpan = $tracer
            ->spanBuilder('user.validation')
            ->setParent(Context::getCurrent())  // 👈 SAME TRACE - uses current context
            ->setSpanKind(SpanKind::KIND_INTERNAL)
            ->startSpan();

        // Step 3: Set custom attributes AFTER span is started
        $validationSpan->setAttribute('apm.user.username', $data['username']);
        $validationSpan->setAttribute('apm.user.email', $data['email']);
        $validationSpan->setAttribute('apm.operation.type', 'validation');

        // Step 4: Activate the span
        $scope = $validationSpan->storeInContext(Context::getCurrent())->activate();

        try {
            // Check if username already exists
            $existingUser = $this->userRepository->findByUsername($data['username']);

            if ($existingUser) {
                $validationSpan->setAttribute('apm.validation.result', 'failed');
                $validationSpan->setAttribute('apm.validation.reason', 'username_exists');

                $payload = json_encode([
                    'success' => false,
                    'error' => 'Username already exists',
                ], JSON_PRETTY_PRINT);

                $response->getBody()->write($payload);
                return $response
                    ->withHeader('Content-Type', 'application/json')
                    ->withStatus(409);
            }

            $validationSpan->setAttribute('apm.validation.result', 'passed');
        } finally {
            // Step 5: Always end the span and detach scope
            $validationSpan->end();
            $scope->detach();
        }

        try {
            // ✅ APPROACH 2 - CASE A: Create another child span for user creation
            $createSpan = $tracer
                ->spanBuilder('user.create')
                ->setParent(Context::getCurrent())  // 👈 SAME TRACE
                ->setSpanKind(SpanKind::KIND_INTERNAL)
                ->startSpan();

            // Set custom attributes AFTER span is started
            $createSpan->setAttribute('apm.user.username', $data['username']);
            $createSpan->setAttribute('apm.user.email', $data['email']);
            $createSpan->setAttribute('apm.operation.type', 'create');
            $createSpan->setAttribute('apm.db.operation', 'INSERT');

            $createScope = $createSpan->storeInContext(Context::getCurrent())->activate();

            try {
                $user = new User($data);
                $createdUser = $this->userRepository->create($user);

                $createSpan->setAttribute('apm.user.id', $createdUser->getId());
                $createSpan->setAttribute('apm.operation.status', 'success');

                $payload = json_encode([
                    'success' => true,
                    'data' => $createdUser,
                    'message' => 'User created successfully',
                ], JSON_PRETTY_PRINT);

                $response->getBody()->write($payload);
                return $response
                    ->withHeader('Content-Type', 'application/json')
                    ->withStatus(201);
            } finally {
                $createSpan->end();
                $createScope->detach();
            }
        } catch (Exception $e) {
            $payload = json_encode([
                'success' => false,
                'error' => 'Failed to create user: ' . $e->getMessage(),
            ], JSON_PRETTY_PRINT);

            $response->getBody()->write($payload);
            return $response
                ->withHeader('Content-Type', 'application/json')
                ->withStatus(500);
        }
    }

    /**
     * PUT /users/{id} - Update a user
     *
     * ✅ Approach 2: Case A - Tracer-Based Child Span (Same Trace)
     *
     * This method demonstrates creating multiple child spans for different
     * business operations within the same trace.
     */
    public function update(Request $request, Response $response, array $args): Response
    {
        $id = (int) $args['id'];
        $data = $request->getParsedBody();

        if (!$data) {
            $payload = json_encode([
                'success' => false,
                'error' => 'Invalid JSON data',
            ], JSON_PRETTY_PRINT);

            $response->getBody()->write($payload);
            return $response
                ->withHeader('Content-Type', 'application/json')
                ->withStatus(400);
        }

        // ✅ APPROACH 2 - CASE A: Create a child span for user lookup
        $tracer = Globals::tracerProvider()->getTracer('business-tracer');

        $lookupSpan = $tracer
            ->spanBuilder('user.lookup')
            ->setParent(Context::getCurrent())
            ->setSpanKind(SpanKind::KIND_INTERNAL)
            ->startSpan();

        $lookupSpan->setAttribute('apm.user.id', $id);
        $lookupSpan->setAttribute('apm.operation.type', 'lookup');

        $lookupScope = $lookupSpan->storeInContext(Context::getCurrent())->activate();

        try {
            $existingUser = $this->userRepository->findById($id);

            if ($existingUser) {
                $lookupSpan->setAttribute('apm.lookup.result', 'found');
                $lookupSpan->setAttribute('apm.user.username', $existingUser->getUsername());
            } else {
                $lookupSpan->setAttribute('apm.lookup.result', 'not_found');
            }
        } finally {
            $lookupSpan->end();
            $lookupScope->detach();
        }

        if (!$existingUser) {
            $payload = json_encode([
                'success' => false,
                'error' => 'User not found',
            ], JSON_PRETTY_PRINT);

            $response->getBody()->write($payload);
            return $response
                ->withHeader('Content-Type', 'application/json')
                ->withStatus(404);
        }

        try {
            // ✅ APPROACH 2 - CASE A: Create a child span for user update
            $updateSpan = $tracer
                ->spanBuilder('user.update')
                ->setParent(Context::getCurrent())
                ->setSpanKind(SpanKind::KIND_INTERNAL)
                ->startSpan();

            $updateSpan->setAttribute('apm.user.id', $id);
            $updateSpan->setAttribute('apm.user.username', $data['username'] ?? 'N/A');
            $updateSpan->setAttribute('apm.operation.type', 'update');
            $updateSpan->setAttribute('apm.db.operation', 'UPDATE');

            $updateScope = $updateSpan->storeInContext(Context::getCurrent())->activate();

            try {
                $user = new User($data);
                $updatedUser = $this->userRepository->update($id, $user);

                if ($updatedUser) {
                    $updateSpan->setAttribute('apm.operation.status', 'success');
                    $updateSpan->setAttribute('apm.user.updated_fields', implode(',', array_keys($data)));
                } else {
                    $updateSpan->setAttribute('apm.operation.status', 'failed');
                }
            } finally {
                $updateSpan->end();
                $updateScope->detach();
            }

            if (!$updatedUser) {
                $payload = json_encode([
                    'success' => false,
                    'error' => 'User not found',
                ], JSON_PRETTY_PRINT);

                $response->getBody()->write($payload);
                return $response
                    ->withHeader('Content-Type', 'application/json')
                    ->withStatus(404);
            }

            $payload = json_encode([
                'success' => true,
                'data' => $updatedUser,
                'message' => 'User updated successfully',
            ], JSON_PRETTY_PRINT);

            $response->getBody()->write($payload);
            return $response->withHeader('Content-Type', 'application/json');
        } catch (Exception $e) {
            $payload = json_encode([
                'success' => false,
                'error' => 'Failed to update user: ' . $e->getMessage(),
            ], JSON_PRETTY_PRINT);

            $response->getBody()->write($payload);
            return $response
                ->withHeader('Content-Type', 'application/json')
                ->withStatus(500);
        }
    }

    /**
     * DELETE /users/{id} - Delete a user
     *
     * ✅ Approach 2️⃣ - Case A: Tracer-Based Child Span (Same Trace)
     *
     * Demonstrates creating child spans for delete operations with validation.
     */
    public function delete(Request $request, Response $response, array $args): Response
    {
        $id = (int) $args['id'];

        // ✅ APPROACH 2 - CASE A: Create a child span for user lookup before delete
        $tracer = Globals::tracerProvider()->getTracer('business-tracer');

        $lookupSpan = $tracer
            ->spanBuilder('user.delete.lookup')
            ->setParent(Context::getCurrent())
            ->setSpanKind(SpanKind::KIND_INTERNAL)
            ->startSpan();

        $lookupSpan->setAttribute('apm.user.id', $id);
        $lookupSpan->setAttribute('apm.operation.type', 'delete_lookup');
        $lookupSpan->setAttribute('apm.db.operation', 'SELECT');

        $lookupScope = $lookupSpan->storeInContext(Context::getCurrent())->activate();

        try {
            $existingUser = $this->userRepository->findById($id);

            if (!$existingUser) {
                $lookupSpan->setAttribute('apm.lookup.result', 'not_found');
                $lookupSpan->setAttribute('apm.operation.status', 'failed');

                $payload = json_encode([
                    'success' => false,
                    'error' => 'User not found',
                ], JSON_PRETTY_PRINT);

                $response->getBody()->write($payload);
                return $response
                    ->withHeader('Content-Type', 'application/json')
                    ->withStatus(404);
            }

            $lookupSpan->setAttribute('apm.lookup.result', 'found');
            $lookupSpan->setAttribute('apm.user.username', $existingUser->getUsername());
        } finally {
            $lookupSpan->end();
            $lookupScope->detach();
        }

        // ✅ APPROACH 2 - CASE A: Create a child span for actual delete operation
        $deleteSpan = $tracer
            ->spanBuilder('user.delete')
            ->setParent(Context::getCurrent())
            ->setSpanKind(SpanKind::KIND_INTERNAL)
            ->startSpan();

        $deleteSpan->setAttribute('apm.user.id', $id);
        $deleteSpan->setAttribute('apm.user.username', $existingUser->getUsername());
        $deleteSpan->setAttribute('apm.operation.type', 'delete');
        $deleteSpan->setAttribute('apm.db.operation', 'DELETE');

        $deleteScope = $deleteSpan->storeInContext(Context::getCurrent())->activate();

        try {
            $deleted = $this->userRepository->delete($id);

            if (!$deleted) {
                $deleteSpan->setAttribute('apm.operation.status', 'failed');
                $deleteSpan->setAttribute('apm.error.reason', 'delete_operation_failed');

                $payload = json_encode([
                    'success' => false,
                    'error' => 'Failed to delete user',
                ], JSON_PRETTY_PRINT);

                $response->getBody()->write($payload);
                return $response
                    ->withHeader('Content-Type', 'application/json')
                    ->withStatus(500);
            }

            $deleteSpan->setAttribute('apm.operation.status', 'success');
            $deleteSpan->setAttribute('apm.result.deleted', true);

            $payload = json_encode([
                'success' => true,
                'message' => 'User deleted successfully',
            ], JSON_PRETTY_PRINT);

            $response->getBody()->write($payload);
            return $response->withHeader('Content-Type', 'application/json');
        } catch (Exception $e) {
            $deleteSpan->setAttribute('apm.operation.status', 'failed');
            $deleteSpan->setAttribute('apm.error.message', $e->getMessage());

            $payload = json_encode([
                'success' => false,
                'error' => 'Failed to delete user: ' . $e->getMessage(),
            ], JSON_PRETTY_PRINT);

            $response->getBody()->write($payload);
            return $response
                ->withHeader('Content-Type', 'application/json')
                ->withStatus(500);
        } finally {
            $deleteSpan->end();
            $deleteScope->detach();
        }
    }
}

