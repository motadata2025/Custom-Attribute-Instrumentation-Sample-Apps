const UserModel = require('../models/userModel');
const tracerService = require('../services/tracerService');
const { SpanKind } = require('@opentelemetry/api');

class UserController {
  // Get all users
  static async getAllUsers(req, res) {
    // Method 2: Span Creation - Create a custom span for this operation
    return tracerService.executeInSpan(
      'UserController.getAllUsers',
      async (span) => {
        // Add APM custom attributes with apm.* prefix
        tracerService.addCommonAttributes(span, {
          operation: 'getAllUsers',
          controller: 'UserController',
          method: req.method,
          endpoint: req.path
        });

        // Add event for operation start
        span.addEvent('getAllUsers.started');

        try {
          // Create a nested span for database operation
          const users = await tracerService.executeInSpan(
            'UserController.getAllUsers.database',
            async (dbSpan) => {
              dbSpan.setAttribute('apm.db.operation', 'SELECT');
              dbSpan.setAttribute('apm.db.table', 'nodejs_user_tbl');

              const result = await UserModel.getAllUsers();

              dbSpan.setAttribute('apm.db.rows_returned', result.length);
              return result;
            },
            { kind: SpanKind.CLIENT }
          );

          // Add event for successful retrieval
          span.addEvent('getAllUsers.users_retrieved', {
            'user.count': users.length
          });

          // Add success attributes
          tracerService.addSuccessAttributes(span, 200, {
            'apm.result.count': users.length,
            'apm.result.has_data': users.length > 0
          });

          res.status(200).json({
            success: true,
            count: users.length,
            data: users
          });
        } catch (error) {
          console.error('Error in getAllUsers:', error);

          // Add error attributes
          tracerService.addErrorAttributes(span, error, 500);

          // Add error event
          span.addEvent('getAllUsers.error', {
            'error.message': error.message
          });

          res.status(500).json({
            success: false,
            message: 'Error retrieving users',
            error: error.message
          });
        }
      },
      { kind: SpanKind.INTERNAL }
    );
  }

  // Get user by username
  static async getUserByUsername(req, res) {
    const { username } = req.params;

    // Method 2: Span Creation - Create a custom span for this operation
    return tracerService.executeInSpan(
      'UserController.getUserByUsername',
      async (span) => {
        // Add APM custom attributes
        tracerService.addCommonAttributes(span, {
          operation: 'getUserByUsername',
          controller: 'UserController',
          method: req.method,
          endpoint: req.path,
          username: username
        });

        span.addEvent('getUserByUsername.started', {
          'user.username': username
        });

        try {
          // Create a nested span for database lookup
          const user = await tracerService.executeInSpan(
            'UserController.getUserByUsername.database',
            async (dbSpan) => {
              dbSpan.setAttribute('apm.db.operation', 'SELECT');
              dbSpan.setAttribute('apm.db.table', 'nodejs_user_tbl');
              dbSpan.setAttribute('apm.db.query.username', username);

              const result = await UserModel.getUserByUsername(username);

              dbSpan.setAttribute('apm.db.found', !!result);
              return result;
            },
            { kind: SpanKind.CLIENT }
          );

          if (!user) {
            // Add not found event
            span.addEvent('getUserByUsername.not_found', {
              'user.username': username
            });

            // Add not found attributes
            span.setAttribute('apm.result.success', false);
            span.setAttribute('apm.result.found', false);
            span.setAttribute('apm.http.status_code', 404);

            return res.status(404).json({
              success: false,
              message: `User with username '${username}' not found`
            });
          }

          // Add success event
          span.addEvent('getUserByUsername.found', {
            'user.id': user.id,
            'user.username': user.username
          });

          // Add success attributes
          tracerService.addSuccessAttributes(span, 200, {
            'apm.result.found': true,
            'apm.user.id': user.id,
            'apm.user.email': user.email,
            'apm.user.is_active': user.is_active || false
          });

          res.status(200).json({
            success: true,
            data: user
          });
        } catch (error) {
          console.error('Error in getUserByUsername:', error);

          tracerService.addErrorAttributes(span, error, 500);
          span.addEvent('getUserByUsername.error');

          res.status(500).json({
            success: false,
            message: 'Error retrieving user',
            error: error.message
          });
        }
      },
      { kind: SpanKind.INTERNAL }
    );
  }

  // Create new user
  static async createUser(req, res) {
    const { username, email, full_name, age, salary, is_active, tags } = req.body;

    // Method 2: Span Creation - Create a custom span for this operation
    return tracerService.executeInSpan(
      'UserController.createUser',
      async (span) => {
        // Add APM custom attributes
        tracerService.addCommonAttributes(span, {
          operation: 'createUser',
          controller: 'UserController',
          method: req.method,
          endpoint: req.path,
          username: username || 'not_provided'
        });

        // Add user data attributes
        if (email) span.setAttribute('apm.user.email', email);
        if (age) span.setAttribute('apm.user.age', age);
        if (salary) span.setAttribute('apm.user.salary', salary);
        if (tags && Array.isArray(tags)) {
          span.setAttribute('apm.user.tags', tags);
          span.setAttribute('apm.user.tags_count', tags.length);
        }

        span.addEvent('createUser.started');

        try {
          // Validation span
          await tracerService.executeInSpan(
            'UserController.createUser.validation',
            async (validationSpan) => {
              validationSpan.setAttribute('apm.validation.username_provided', !!username);
              validationSpan.setAttribute('apm.validation.email_provided', !!email);

              if (!username || !email) {
                validationSpan.setAttribute('apm.validation.failed', true);
                validationSpan.setAttribute('apm.validation.error', 'Username and email are required');

                throw new Error('VALIDATION_ERROR');
              }

              validationSpan.setAttribute('apm.validation.passed', true);
            },
            { kind: SpanKind.INTERNAL }
          );

          // Check if username exists span
          const exists = await tracerService.executeInSpan(
            'UserController.createUser.checkExists',
            async (checkSpan) => {
              checkSpan.setAttribute('apm.db.operation', 'SELECT');
              checkSpan.setAttribute('apm.db.table', 'nodejs_user_tbl');
              checkSpan.setAttribute('apm.check.username', username);

              const result = await UserModel.usernameExists(username);

              checkSpan.setAttribute('apm.check.exists', result);
              return result;
            },
            { kind: SpanKind.CLIENT }
          );

          if (exists) {
            span.addEvent('createUser.conflict', {
              'conflict.reason': 'Username already exists'
            });

            span.setAttribute('apm.result.success', false);
            span.setAttribute('apm.conflict.occurred', true);
            span.setAttribute('apm.conflict.reason', 'Username already exists');
            span.setAttribute('apm.http.status_code', 409);

            return res.status(409).json({
              success: false,
              message: `Username '${username}' already exists`
            });
          }

          // Create user span
          const newUser = await tracerService.executeInSpan(
            'UserController.createUser.database',
            async (dbSpan) => {
              dbSpan.setAttribute('apm.db.operation', 'INSERT');
              dbSpan.setAttribute('apm.db.table', 'nodejs_user_tbl');
              dbSpan.setAttribute('apm.db.username', username);

              const result = await UserModel.createUser(req.body);

              dbSpan.setAttribute('apm.db.created_id', result.id);
              return result;
            },
            { kind: SpanKind.CLIENT }
          );

          // Add success event
          span.addEvent('createUser.success', {
            'user.id': newUser.id,
            'user.username': newUser.username
          });

          // Add success attributes
          tracerService.addSuccessAttributes(span, 201, {
            'apm.result.created': true,
            'apm.user.id': newUser.id,
            'apm.user.created_at': newUser.created_at
          });

          res.status(201).json({
            success: true,
            message: 'User created successfully',
            data: newUser
          });
        } catch (error) {
          console.error('Error in createUser:', error);

          // Handle validation error
          if (error.message === 'VALIDATION_ERROR') {
            span.setAttribute('apm.result.success', false);
            span.setAttribute('apm.validation.failed', true);
            span.setAttribute('apm.http.status_code', 400);

            return res.status(400).json({
              success: false,
              message: 'Username and email are required'
            });
          }

          // Handle unique constraint violation
          if (error.code === '23505') {
            span.addEvent('createUser.conflict', {
              'conflict.reason': 'Database constraint violation'
            });

            span.setAttribute('apm.result.success', false);
            span.setAttribute('apm.conflict.occurred', true);
            span.setAttribute('apm.http.status_code', 409);

            return res.status(409).json({
              success: false,
              message: 'Username already exists'
            });
          }

          tracerService.addErrorAttributes(span, error, 500);
          span.addEvent('createUser.error');

          res.status(500).json({
            success: false,
            message: 'Error creating user',
            error: error.message
          });
        }
      },
      { kind: SpanKind.INTERNAL }
    );
  }

  // Update user by username
  static async updateUser(req, res) {
    const { username } = req.params;
    const { email, full_name, age, salary, is_active, tags } = req.body;

    // Method 2: Span Creation - Create a custom span for this operation
    return tracerService.executeInSpan(
      'UserController.updateUser',
      async (span) => {
        // Add APM custom attributes
        tracerService.addCommonAttributes(span, {
          operation: 'updateUser',
          controller: 'UserController',
          method: req.method,
          endpoint: req.path,
          username: username
        });

        // Track which fields are being updated
        const updatedFields = [];
        if (email) updatedFields.push('email');
        if (full_name) updatedFields.push('full_name');
        if (age !== undefined) updatedFields.push('age');
        if (salary !== undefined) updatedFields.push('salary');
        if (is_active !== undefined) updatedFields.push('is_active');
        if (tags) updatedFields.push('tags');

        if (updatedFields.length > 0) {
          span.setAttribute('apm.update.fields', updatedFields);
          span.setAttribute('apm.update.fields_count', updatedFields.length);
        }

        span.addEvent('updateUser.started', {
          'user.username': username,
          'update.fields_count': updatedFields.length
        });

        try {
          // Check if user exists span
          const exists = await tracerService.executeInSpan(
            'UserController.updateUser.checkExists',
            async (checkSpan) => {
              checkSpan.setAttribute('apm.db.operation', 'SELECT');
              checkSpan.setAttribute('apm.db.table', 'nodejs_user_tbl');
              checkSpan.setAttribute('apm.check.username', username);

              const result = await UserModel.usernameExists(username);

              checkSpan.setAttribute('apm.check.exists', result);
              return result;
            },
            { kind: SpanKind.CLIENT }
          );

          if (!exists) {
            span.addEvent('updateUser.not_found', {
              'user.username': username
            });

            span.setAttribute('apm.result.success', false);
            span.setAttribute('apm.result.found', false);
            span.setAttribute('apm.http.status_code', 404);

            return res.status(404).json({
              success: false,
              message: `User with username '${username}' not found`
            });
          }

          // Update user span
          const updatedUser = await tracerService.executeInSpan(
            'UserController.updateUser.database',
            async (dbSpan) => {
              dbSpan.setAttribute('apm.db.operation', 'UPDATE');
              dbSpan.setAttribute('apm.db.table', 'nodejs_user_tbl');
              dbSpan.setAttribute('apm.db.username', username);
              dbSpan.setAttribute('apm.db.update_fields', updatedFields);

              const result = await UserModel.updateUser(username, req.body);

              dbSpan.setAttribute('apm.db.updated_id', result.id);
              return result;
            },
            { kind: SpanKind.CLIENT }
          );

          // Add success event
          span.addEvent('updateUser.success', {
            'user.id': updatedUser.id,
            'user.username': updatedUser.username
          });

          // Add success attributes
          tracerService.addSuccessAttributes(span, 200, {
            'apm.result.updated': true,
            'apm.user.id': updatedUser.id,
            'apm.user.updated_at': updatedUser.updated_at
          });

          res.status(200).json({
            success: true,
            message: 'User updated successfully',
            data: updatedUser
          });
        } catch (error) {
          console.error('Error in updateUser:', error);

          tracerService.addErrorAttributes(span, error, 500);
          span.addEvent('updateUser.error');

          res.status(500).json({
            success: false,
            message: 'Error updating user',
            error: error.message
          });
        }
      },
      { kind: SpanKind.INTERNAL }
    );
  }

  // Delete user by username
  static async deleteUser(req, res) {
    const { username } = req.params;

    // Method 2: Span Creation - Create a custom span for this operation
    return tracerService.executeInSpan(
      'UserController.deleteUser',
      async (span) => {
        // Add APM custom attributes
        tracerService.addCommonAttributes(span, {
          operation: 'deleteUser',
          controller: 'UserController',
          method: req.method,
          endpoint: req.path,
          username: username
        });

        span.addEvent('deleteUser.started', {
          'user.username': username
        });

        try {
          // Delete user span
          const deletedUser = await tracerService.executeInSpan(
            'UserController.deleteUser.database',
            async (dbSpan) => {
              dbSpan.setAttribute('apm.db.operation', 'DELETE');
              dbSpan.setAttribute('apm.db.table', 'nodejs_user_tbl');
              dbSpan.setAttribute('apm.db.username', username);

              const result = await UserModel.deleteUser(username);

              dbSpan.setAttribute('apm.db.found', !!result);
              if (result) {
                dbSpan.setAttribute('apm.db.deleted_id', result.id);
              }
              return result;
            },
            { kind: SpanKind.CLIENT }
          );

          if (!deletedUser) {
            span.addEvent('deleteUser.not_found', {
              'user.username': username
            });

            span.setAttribute('apm.result.success', false);
            span.setAttribute('apm.result.found', false);
            span.setAttribute('apm.http.status_code', 404);

            return res.status(404).json({
              success: false,
              message: `User with username '${username}' not found`
            });
          }

          // Add success event
          span.addEvent('deleteUser.success', {
            'user.id': deletedUser.id,
            'user.username': deletedUser.username
          });

          // Add success attributes
          tracerService.addSuccessAttributes(span, 200, {
            'apm.result.deleted': true,
            'apm.user.id': deletedUser.id,
            'apm.user.email': deletedUser.email
          });

          res.status(200).json({
            success: true,
            message: 'User deleted successfully',
            data: deletedUser
          });
        } catch (error) {
          console.error('Error in deleteUser:', error);

          tracerService.addErrorAttributes(span, error, 500);
          span.addEvent('deleteUser.error');

          res.status(500).json({
            success: false,
            message: 'Error deleting user',
            error: error.message
          });
        }
      },
      { kind: SpanKind.INTERNAL }
    );
  }
}

module.exports = UserController;

