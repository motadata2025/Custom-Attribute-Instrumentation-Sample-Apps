const UserModel = require('../models/userModel');
const { trace } = require('@opentelemetry/api');

class UserController {
  // Get all users
  static async getAllUsers(req, res) {
    // Method 1: Active Span Enrichment - Add custom attributes to existing span
    const span = trace.getActiveSpan();
    if (span) {
      // Add APM custom attributes with apm.* prefix
      span.setAttribute('apm.operation', 'getAllUsers');
      span.setAttribute('apm.controller', 'UserController');
      span.setAttribute('apm.method', req.method);
      span.setAttribute('apm.endpoint', req.path);
    }

    try {
      const users = await UserModel.getAllUsers();

      // Add result attributes to span
      if (span) {
        span.setAttribute('apm.result.count', users.length);
        span.setAttribute('apm.result.success', true);
        span.setAttribute('apm.http.status_code', 200);
      }

      res.status(200).json({
        success: true,
        count: users.length,
        data: users
      });
    } catch (error) {
      console.error('Error in getAllUsers:', error);

      // Add error attributes to span
      if (span) {
        span.setAttribute('apm.result.success', false);
        span.setAttribute('apm.error.occurred', true);
        span.setAttribute('apm.error.message', error.message);
        span.setAttribute('apm.http.status_code', 500);
      }

      res.status(500).json({
        success: false,
        message: 'Error retrieving users',
        error: error.message
      });
    }
  }

  // Get user by username
  static async getUserByUsername(req, res) {
    // Method 1: Active Span Enrichment - Add custom attributes to existing span
    const span = trace.getActiveSpan();
    const { username } = req.params;

    if (span) {
      // Add APM custom attributes with apm.* prefix
      span.setAttribute('apm.operation', 'getUserByUsername');
      span.setAttribute('apm.controller', 'UserController');
      span.setAttribute('apm.method', req.method);
      span.setAttribute('apm.endpoint', req.path);
      span.setAttribute('apm.user.username', username);
    }

    try {
      const user = await UserModel.getUserByUsername(username);

      if (!user) {
        // Add not found attributes to span
        if (span) {
          span.setAttribute('apm.result.success', false);
          span.setAttribute('apm.result.found', false);
          span.setAttribute('apm.http.status_code', 404);
        }

        return res.status(404).json({
          success: false,
          message: `User with username '${username}' not found`
        });
      }

      // Add success attributes to span
      if (span) {
        span.setAttribute('apm.result.success', true);
        span.setAttribute('apm.result.found', true);
        span.setAttribute('apm.http.status_code', 200);
        span.setAttribute('apm.user.id', user.id);
        span.setAttribute('apm.user.email', user.email);
        if (user.is_active !== undefined) {
          span.setAttribute('apm.user.is_active', user.is_active);
        }
      }

      res.status(200).json({
        success: true,
        data: user
      });
    } catch (error) {
      console.error('Error in getUserByUsername:', error);

      // Add error attributes to span
      if (span) {
        span.setAttribute('apm.result.success', false);
        span.setAttribute('apm.error.occurred', true);
        span.setAttribute('apm.error.message', error.message);
        span.setAttribute('apm.http.status_code', 500);
      }

      res.status(500).json({
        success: false,
        message: 'Error retrieving user',
        error: error.message
      });
    }
  }

  // Create new user
  static async createUser(req, res) {
    // Method 1: Active Span Enrichment - Add custom attributes to existing span
    const span = trace.getActiveSpan();
    const { username, email, full_name, age, salary, is_active, tags } = req.body;

    if (span) {
      // Add APM custom attributes with apm.* prefix
      span.setAttribute('apm.operation', 'createUser');
      span.setAttribute('apm.controller', 'UserController');
      span.setAttribute('apm.method', req.method);
      span.setAttribute('apm.endpoint', req.path);
      span.setAttribute('apm.user.username', username || 'not_provided');
      span.setAttribute('apm.user.email', email || 'not_provided');
      if (age) span.setAttribute('apm.user.age', age);
      if (salary) span.setAttribute('apm.user.salary', salary);
      if (tags && Array.isArray(tags)) {
        span.setAttribute('apm.user.tags', tags);
        span.setAttribute('apm.user.tags_count', tags.length);
      }
    }

    try {
      // Validate required fields
      if (!username || !email) {
        // Add validation error attributes to span
        if (span) {
          span.setAttribute('apm.result.success', false);
          span.setAttribute('apm.validation.failed', true);
          span.setAttribute('apm.validation.error', 'Username and email are required');
          span.setAttribute('apm.http.status_code', 400);
        }

        return res.status(400).json({
          success: false,
          message: 'Username and email are required'
        });
      }

      // Check if username already exists
      const exists = await UserModel.usernameExists(username);
      if (exists) {
        // Add conflict attributes to span
        if (span) {
          span.setAttribute('apm.result.success', false);
          span.setAttribute('apm.conflict.occurred', true);
          span.setAttribute('apm.conflict.reason', 'Username already exists');
          span.setAttribute('apm.http.status_code', 409);
        }

        return res.status(409).json({
          success: false,
          message: `Username '${username}' already exists`
        });
      }

      const newUser = await UserModel.createUser(req.body);

      // Add success attributes to span
      if (span) {
        span.setAttribute('apm.result.success', true);
        span.setAttribute('apm.result.created', true);
        span.setAttribute('apm.http.status_code', 201);
        span.setAttribute('apm.user.id', newUser.id);
        span.setAttribute('apm.user.created_at', newUser.created_at);
      }

      res.status(201).json({
        success: true,
        message: 'User created successfully',
        data: newUser
      });
    } catch (error) {
      console.error('Error in createUser:', error);

      // Add error attributes to span
      if (span) {
        span.setAttribute('apm.result.success', false);
        span.setAttribute('apm.error.occurred', true);
        span.setAttribute('apm.error.message', error.message);
        if (error.code) {
          span.setAttribute('apm.error.code', error.code);
        }
      }

      // Handle unique constraint violation
      if (error.code === '23505') {
        if (span) {
          span.setAttribute('apm.conflict.occurred', true);
          span.setAttribute('apm.http.status_code', 409);
        }

        return res.status(409).json({
          success: false,
          message: 'Username already exists'
        });
      }

      if (span) {
        span.setAttribute('apm.http.status_code', 500);
      }

      res.status(500).json({
        success: false,
        message: 'Error creating user',
        error: error.message
      });
    }
  }

  // Update user by username
  static async updateUser(req, res) {
    // Method 1: Active Span Enrichment - Add custom attributes to existing span
    const span = trace.getActiveSpan();
    const { username } = req.params;
    const { email, full_name, age, salary, is_active, tags } = req.body;

    if (span) {
      // Add APM custom attributes with apm.* prefix
      span.setAttribute('apm.operation', 'updateUser');
      span.setAttribute('apm.controller', 'UserController');
      span.setAttribute('apm.method', req.method);
      span.setAttribute('apm.endpoint', req.path);
      span.setAttribute('apm.user.username', username);

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
    }

    try {
      // Check if user exists
      const exists = await UserModel.usernameExists(username);
      if (!exists) {
        // Add not found attributes to span
        if (span) {
          span.setAttribute('apm.result.success', false);
          span.setAttribute('apm.result.found', false);
          span.setAttribute('apm.http.status_code', 404);
        }

        return res.status(404).json({
          success: false,
          message: `User with username '${username}' not found`
        });
      }

      const updatedUser = await UserModel.updateUser(username, req.body);

      // Add success attributes to span
      if (span) {
        span.setAttribute('apm.result.success', true);
        span.setAttribute('apm.result.updated', true);
        span.setAttribute('apm.http.status_code', 200);
        span.setAttribute('apm.user.id', updatedUser.id);
        span.setAttribute('apm.user.updated_at', updatedUser.updated_at);
      }

      res.status(200).json({
        success: true,
        message: 'User updated successfully',
        data: updatedUser
      });
    } catch (error) {
      console.error('Error in updateUser:', error);

      // Add error attributes to span
      if (span) {
        span.setAttribute('apm.result.success', false);
        span.setAttribute('apm.error.occurred', true);
        span.setAttribute('apm.error.message', error.message);
        span.setAttribute('apm.http.status_code', 500);
      }

      res.status(500).json({
        success: false,
        message: 'Error updating user',
        error: error.message
      });
    }
  }

  // Delete user by username
  static async deleteUser(req, res) {
    // Method 1: Active Span Enrichment - Add custom attributes to existing span
    const span = trace.getActiveSpan();
    const { username } = req.params;

    if (span) {
      // Add APM custom attributes with apm.* prefix
      span.setAttribute('apm.operation', 'deleteUser');
      span.setAttribute('apm.controller', 'UserController');
      span.setAttribute('apm.method', req.method);
      span.setAttribute('apm.endpoint', req.path);
      span.setAttribute('apm.user.username', username);
    }

    try {
      const deletedUser = await UserModel.deleteUser(username);

      if (!deletedUser) {
        // Add not found attributes to span
        if (span) {
          span.setAttribute('apm.result.success', false);
          span.setAttribute('apm.result.found', false);
          span.setAttribute('apm.http.status_code', 404);
        }

        return res.status(404).json({
          success: false,
          message: `User with username '${username}' not found`
        });
      }

      // Add success attributes to span
      if (span) {
        span.setAttribute('apm.result.success', true);
        span.setAttribute('apm.result.deleted', true);
        span.setAttribute('apm.http.status_code', 200);
        span.setAttribute('apm.user.id', deletedUser.id);
        span.setAttribute('apm.user.email', deletedUser.email);
      }

      res.status(200).json({
        success: true,
        message: 'User deleted successfully',
        data: deletedUser
      });
    } catch (error) {
      console.error('Error in deleteUser:', error);

      // Add error attributes to span
      if (span) {
        span.setAttribute('apm.result.success', false);
        span.setAttribute('apm.error.occurred', true);
        span.setAttribute('apm.error.message', error.message);
        span.setAttribute('apm.http.status_code', 500);
      }

      res.status(500).json({
        success: false,
        message: 'Error deleting user',
        error: error.message
      });
    }
  }
}

module.exports = UserController;

