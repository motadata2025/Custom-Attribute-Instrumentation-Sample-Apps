const pool = require('../db/config');

class UserModel {
  // Get all users
  static async getAllUsers() {
    const query = 'SELECT * FROM nodejs_user_tbl ORDER BY created_at DESC';
    const result = await pool.query(query);
    return result.rows;
  }

  // Get user by username
  static async getUserByUsername(username) {
    const query = 'SELECT * FROM nodejs_user_tbl WHERE username = $1';
    const result = await pool.query(query, [username]);
    return result.rows[0];
  }

  // Create new user
  static async createUser(userData) {
    const { username, email, full_name, age, salary, is_active, tags } = userData;
    
    const query = `
      INSERT INTO nodejs_user_tbl 
      (username, email, full_name, age, salary, is_active, tags)
      VALUES ($1, $2, $3, $4, $5, $6, $7)
      RETURNING *
    `;
    
    const values = [
      username,
      email,
      full_name || null,
      age || null,
      salary || null,
      is_active !== undefined ? is_active : true,
      tags || null
    ];
    
    const result = await pool.query(query, values);
    return result.rows[0];
  }

  // Update user by username
  static async updateUser(username, userData) {
    const { email, full_name, age, salary, is_active, tags } = userData;
    
    const query = `
      UPDATE nodejs_user_tbl 
      SET 
        email = COALESCE($1, email),
        full_name = COALESCE($2, full_name),
        age = COALESCE($3, age),
        salary = COALESCE($4, salary),
        is_active = COALESCE($5, is_active),
        tags = COALESCE($6, tags)
      WHERE username = $7
      RETURNING *
    `;
    
    const values = [
      email || null,
      full_name || null,
      age || null,
      salary || null,
      is_active !== undefined ? is_active : null,
      tags || null,
      username
    ];
    
    const result = await pool.query(query, values);
    return result.rows[0];
  }

  // Delete user by username
  static async deleteUser(username) {
    const query = 'DELETE FROM nodejs_user_tbl WHERE username = $1 RETURNING *';
    const result = await pool.query(query, [username]);
    return result.rows[0];
  }

  // Check if username exists
  static async usernameExists(username) {
    const query = 'SELECT EXISTS(SELECT 1 FROM nodejs_user_tbl WHERE username = $1)';
    const result = await pool.query(query, [username]);
    return result.rows[0].exists;
  }
}

module.exports = UserModel;

