<?php

namespace App\Controllers;

use App\Models\User;
use App\Repositories\UserRepository;
use Exception;
use Psr\Http\Message\ResponseInterface as Response;
use Psr\Http\Message\ServerRequestInterface as Request;
use OpenTelemetry\API\Trace\Span;

class UserController
{
    private UserRepository $userRepository;

    public function __construct(UserRepository $userRepository)
    {
        $this->userRepository = $userRepository;
    }

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
     * Helper method to add span events for important actions
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
     * Compatible with both string-based and enum-based StatusCode
     */
    private function setSpanStatus(string $code, string $description = ''): void
    {
        try {
            $span = Span::getCurrent();
            if ($span->isRecording()) {
                // Try to use the enum if available, otherwise use string
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
     * GET /users/{id} - Get user by ID
     */
    public function show(Request $request, Response $response, array $args): Response
    {
        $id = (int) $args['id'];

        // Add custom attributes to active span
        $this->enrichActiveSpan([
            'apm.operation.type' => 'get_user',
            'apm.endpoint' => '/users/{id}',
            'apm.http.method' => 'GET',
            'apm.user.id' => $id,
        ]);

        // Add event for the query start
        $this->addSpanEvent('user.query.start', [
            'user.id' => $id,
        ]);

        $user = $this->userRepository->findById($id);

        if (!$user) {
            // Add error info to span
            $this->enrichActiveSpan([
                'apm.result.found' => false,
                'apm.error.type' => 'not_found',
            ]);

            // Set span status to error
            $this->setSpanStatus('STATUS_ERROR', 'User not found');

            // Add event for not found
            $this->addSpanEvent('user.not_found', [
                'user.id' => $id,
            ]);

            $payload = json_encode([
                'success' => false,
                'error' => 'User not found',
            ], JSON_PRETTY_PRINT);

            $response->getBody()->write($payload);
            return $response
                ->withHeader('Content-Type', 'application/json')
                ->withStatus(404);
        }

        // Add success info to span
        $this->enrichActiveSpan([
            'apm.result.found' => true,
            'apm.user.username' => $user->getUsername(),
        ]);

        // Set span status to OK
        $this->setSpanStatus('STATUS_OK');

        // Add event for successful query
        $this->addSpanEvent('user.query.success', [
            'user.id' => $id,
            'user.username' => $user->getUsername(),
        ]);

        $payload = json_encode([
            'success' => true,
            'data' => $user,
        ], JSON_PRETTY_PRINT);

        $response->getBody()->write($payload);
        return $response->withHeader('Content-Type', 'application/json');
    }

    /**
     * POST /users - Create a new user
     */
    public function store(Request $request, Response $response): Response
    {
        $this->enrichActiveSpan([
            'apm.operation.type' => 'create_user',
            'apm.endpoint' => '/users',
            'apm.http.method' => 'POST',
        ]);

        $data = $request->getParsedBody();

        if (!$data) {
            $this->enrichActiveSpan([
                'apm.error.type' => 'invalid_json',
                'apm.validation.failed' => true,
            ]);
            $this->setSpanStatus('STATUS_ERROR', 'Invalid JSON data');

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
            $this->enrichActiveSpan([
                'apm.error.type' => 'validation_error',
                'apm.validation.failed' => true,
                'apm.validation.missing_fields' => true,
            ]);
            $this->setSpanStatus('STATUS_ERROR', 'Validation failed');
            $this->addSpanEvent('validation.failed', [
                'missing_fields' => array_diff(['username', 'email'], array_keys($data)),
            ]);

            $payload = json_encode([
                'success' => false,
                'error' => 'Username and email are required',
            ], JSON_PRETTY_PRINT);

            $response->getBody()->write($payload);
            return $response
                ->withHeader('Content-Type', 'application/json')
                ->withStatus(400);
        }

        $this->enrichActiveSpan([
            'apm.user.username' => $data['username'],
            'apm.user.email' => $data['email'],
        ]);

        // Check for duplicate username
        $this->addSpanEvent('user.duplicate_check.start', [
            'username' => $data['username'],
        ]);

        $existingUser = $this->userRepository->findByUsername($data['username']);
        if ($existingUser) {
            $this->enrichActiveSpan([
                'apm.error.type' => 'duplicate_username',
                'apm.validation.failed' => true,
            ]);
            $this->setSpanStatus('STATUS_ERROR', 'Duplicate username');
            $this->addSpanEvent('user.duplicate_found', [
                'username' => $data['username'],
            ]);

            $payload = json_encode([
                'success' => false,
                'error' => 'Username already exists',
            ], JSON_PRETTY_PRINT);

            $response->getBody()->write($payload);
            return $response
                ->withHeader('Content-Type', 'application/json')
                ->withStatus(409);
        }

        try {
            $this->addSpanEvent('user.creation.start', [
                'username' => $data['username'],
            ]);

            $user = new User($data);
            $createdUser = $this->userRepository->create($user);

            $this->enrichActiveSpan([
                'apm.result.created' => true,
                'apm.user.id' => $createdUser->getId(),
            ]);
            $this->setSpanStatus('STATUS_OK');
            $this->addSpanEvent('user.creation.success', [
                'user.id' => $createdUser->getId(),
                'username' => $createdUser->getUsername(),
            ]);

            $payload = json_encode([
                'success' => true,
                'data' => $createdUser,
                'message' => 'User created successfully',
            ], JSON_PRETTY_PRINT);

            $response->getBody()->write($payload);
            return $response
                ->withHeader('Content-Type', 'application/json')
                ->withStatus(201);
        } catch (Exception $e) {
            $this->enrichActiveSpan([
                'apm.error.type' => 'database_error',
                'apm.error.message' => $e->getMessage(),
                'apm.result.created' => false,
            ]);
            $this->setSpanStatus('STATUS_ERROR', 'Database error: ' . $e->getMessage());
            $this->addSpanEvent('user.creation.failed', [
                'error' => $e->getMessage(),
                'error_code' => $e->getCode(),
            ]);

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
     * GET /users - Get all users
     */
    public function index(Request $request, Response $response): Response
    {
        $this->enrichActiveSpan([
            'apm.operation.type' => 'list_users',
            'apm.endpoint' => '/users',
            'apm.http.method' => 'GET',
        ]);

        $queryParams = $request->getQueryParams();
        $filters = [];

        if (isset($queryParams['is_active'])) {
            $filters['is_active'] = filter_var($queryParams['is_active'], FILTER_VALIDATE_BOOLEAN);
            $this->enrichActiveSpan([
                'apm.filter.is_active' => $queryParams['is_active'],
            ]);
        }

        $this->addSpanEvent('users.query.start', [
            'has_filters' => !empty($filters),
        ]);

        $users = $this->userRepository->findAll($filters);

        $this->enrichActiveSpan([
            'apm.result.count' => count($users),
            'apm.result.has_filters' => !empty($filters),
        ]);
        $this->setSpanStatus('STATUS_OK');
        $this->addSpanEvent('users.query.success', [
            'count' => count($users),
        ]);

        $payload = json_encode([
            'success' => true,
            'data' => $users,
            'count' => count($users),
        ], JSON_PRETTY_PRINT);

        $response->getBody()->write($payload);
        return $response->withHeader('Content-Type', 'application/json');
    }

    /**
     * PUT /users/{id} - Update a user
     */
    public function update(Request $request, Response $response, array $args): Response
    {
        $id = (int) $args['id'];

        $this->enrichActiveSpan([
            'apm.operation.type' => 'update_user',
            'apm.endpoint' => '/users/{id}',
            'apm.http.method' => 'PUT',
            'apm.user.id' => $id,
        ]);

        $data = $request->getParsedBody();

        if (!$data) {
            $this->enrichActiveSpan([
                'apm.error.type' => 'invalid_json',
                'apm.validation.failed' => true,
            ]);
            $this->setSpanStatus('STATUS_ERROR', 'Invalid JSON data');

            $payload = json_encode([
                'success' => false,
                'error' => 'Invalid JSON data',
            ], JSON_PRETTY_PRINT);

            $response->getBody()->write($payload);
            return $response
                ->withHeader('Content-Type', 'application/json')
                ->withStatus(400);
        }

        $existingUser = $this->userRepository->findById($id);
        if (!$existingUser) {
            $this->enrichActiveSpan([
                'apm.error.type' => 'not_found',
                'apm.result.found' => false,
            ]);
            $this->setSpanStatus('STATUS_ERROR', 'User not found');

            $payload = json_encode([
                'success' => false,
                'error' => 'User not found',
            ], JSON_PRETTY_PRINT);

            $response->getBody()->write($payload);
            return $response
                ->withHeader('Content-Type', 'application/json')
                ->withStatus(404);
        }

        $this->enrichActiveSpan([
            'apm.user.username' => $existingUser->getUsername(),
            'apm.update.fields' => implode(',', array_keys($data)),
        ]);
        $this->addSpanEvent('user.update.start', [
            'user.id' => $id,
            'fields' => array_keys($data),
        ]);

        try {
            $user = new User($data);
            $updatedUser = $this->userRepository->update($id, $user);

            if (!$updatedUser) {
                $this->enrichActiveSpan([
                    'apm.error.type' => 'update_failed',
                    'apm.result.updated' => false,
                ]);
                $this->setSpanStatus('STATUS_ERROR', 'Update failed');

                $payload = json_encode([
                    'success' => false,
                    'error' => 'User not found',
                ], JSON_PRETTY_PRINT);

                $response->getBody()->write($payload);
                return $response
                    ->withHeader('Content-Type', 'application/json')
                    ->withStatus(404);
            }

            $this->enrichActiveSpan([
                'apm.result.updated' => true,
            ]);
            $this->setSpanStatus('STATUS_OK');
            $this->addSpanEvent('user.update.success', [
                'user.id' => $id,
            ]);

            $payload = json_encode([
                'success' => true,
                'data' => $updatedUser,
                'message' => 'User updated successfully',
            ], JSON_PRETTY_PRINT);

            $response->getBody()->write($payload);
            return $response->withHeader('Content-Type', 'application/json');
        } catch (Exception $e) {
            $this->enrichActiveSpan([
                'apm.error.type' => 'database_error',
                'apm.error.message' => $e->getMessage(),
                'apm.result.updated' => false,
            ]);
            $this->setSpanStatus('STATUS_ERROR', 'Database error');
            $this->addSpanEvent('user.update.failed', [
                'error' => $e->getMessage(),
            ]);

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
     */
    public function delete(Request $request, Response $response, array $args): Response
    {
        $id = (int) $args['id'];

        $this->enrichActiveSpan([
            'apm.operation.type' => 'delete_user',
            'apm.endpoint' => '/users/{id}',
            'apm.http.method' => 'DELETE',
            'apm.user.id' => $id,
        ]);

        $existingUser = $this->userRepository->findById($id);
        if (!$existingUser) {
            $this->enrichActiveSpan([
                'apm.error.type' => 'not_found',
                'apm.result.found' => false,
            ]);
            $this->setSpanStatus('STATUS_ERROR', 'User not found');

            $payload = json_encode([
                'success' => false,
                'error' => 'User not found',
            ], JSON_PRETTY_PRINT);

            $response->getBody()->write($payload);
            return $response
                ->withHeader('Content-Type', 'application/json')
                ->withStatus(404);
        }

        $this->enrichActiveSpan([
            'apm.user.username' => $existingUser->getUsername(),
            'apm.result.found' => true,
        ]);
        $this->addSpanEvent('user.delete.start', [
            'user.id' => $id,
            'username' => $existingUser->getUsername(),
        ]);

        try {
            $deleted = $this->userRepository->delete($id);

            if (!$deleted) {
                $this->enrichActiveSpan([
                    'apm.error.type' => 'delete_failed',
                    'apm.result.deleted' => false,
                ]);
                $this->setSpanStatus('STATUS_ERROR', 'Delete failed');

                $payload = json_encode([
                    'success' => false,
                    'error' => 'Failed to delete user',
                ], JSON_PRETTY_PRINT);

                $response->getBody()->write($payload);
                return $response
                    ->withHeader('Content-Type', 'application/json')
                    ->withStatus(500);
            }

            $this->enrichActiveSpan([
                'apm.result.deleted' => true,
            ]);
            $this->setSpanStatus('STATUS_OK');
            $this->addSpanEvent('user.delete.success', [
                'user.id' => $id,
            ]);

            $payload = json_encode([
                'success' => true,
                'message' => 'User deleted successfully',
            ], JSON_PRETTY_PRINT);

            $response->getBody()->write($payload);
            return $response->withHeader('Content-Type', 'application/json');
        } catch (Exception $e) {
            $this->enrichActiveSpan([
                'apm.error.type' => 'database_error',
                'apm.error.message' => $e->getMessage(),
                'apm.result.deleted' => false,
            ]);
            $this->setSpanStatus('STATUS_ERROR', 'Database error');
            $this->addSpanEvent('user.delete.failed', [
                'error' => $e->getMessage(),
            ]);

            $payload = json_encode([
                'success' => false,
                'error' => 'Failed to delete user: ' . $e->getMessage(),
            ], JSON_PRETTY_PRINT);

            $response->getBody()->write($payload);
            return $response
                ->withHeader('Content-Type', 'application/json')
                ->withStatus(500);
        }
    }
}