package main

import (
	"context"
	"database/sql"
	"fmt"
	"time"
)

// UserRepository handles database operations for users
type UserRepository struct {
	db *Database
}

// NewUserRepository creates a new user repository
func NewUserRepository(db *Database) *UserRepository {
	return &UserRepository{db: db}
}

// CreateUser creates a new user in the database
func (r *UserRepository) CreateUser(ctx context.Context, req CreateUserRequest) (*User, error) {
	query := `
		INSERT INTO go_user_tbl2 (username, name, email, age, created_at, updated_at)
		VALUES ($1, $2, $3, $4, $5, $6)
		RETURNING username, name, email, age, created_at, updated_at
	`

	now := time.Now()
	user := &User{}

	err := r.db.DB.QueryRowContext(ctx, query, req.Username, req.Name, req.Email, req.Age, now, now).Scan(
		&user.Username,
		&user.Name,
		&user.Email,
		&user.Age,
		&user.CreatedAt,
		&user.UpdatedAt,
	)

	if err != nil {
		return nil, fmt.Errorf("error creating user: %w", err)
	}

	return user, nil
}

// GetUserByUsername retrieves a user by username
func (r *UserRepository) GetUserByUsername(ctx context.Context, username string) (*User, error) {
	query := `
		SELECT username, name, email, age, created_at, updated_at
		FROM go_user_tbl2
		WHERE username = $1
	`

	user := &User{}
	err := r.db.DB.QueryRowContext(ctx, query, username).Scan(
		&user.Username,
		&user.Name,
		&user.Email,
		&user.Age,
		&user.CreatedAt,
		&user.UpdatedAt,
	)

	if err == sql.ErrNoRows {
		return nil, fmt.Errorf("user not found")
	}
	if err != nil {
		return nil, fmt.Errorf("error getting user: %w", err)
	}

	return user, nil
}

// GetAllUsers retrieves all users from the database
func (r *UserRepository) GetAllUsers(ctx context.Context) ([]User, error) {
	query := `
		SELECT username, name, email, age, created_at, updated_at
		FROM go_user_tbl2
		ORDER BY username
	`

	rows, err := r.db.DB.QueryContext(ctx, query)
	if err != nil {
		return nil, fmt.Errorf("error querying users: %w", err)
	}
	defer rows.Close()

	users := []User{}
	for rows.Next() {
		var user User
		err := rows.Scan(
			&user.Username,
			&user.Name,
			&user.Email,
			&user.Age,
			&user.CreatedAt,
			&user.UpdatedAt,
		)
		if err != nil {
			return nil, fmt.Errorf("error scanning user: %w", err)
		}
		users = append(users, user)
	}

	if err = rows.Err(); err != nil {
		return nil, fmt.Errorf("error iterating users: %w", err)
	}

	return users, nil
}

// UpdateUser updates an existing user
func (r *UserRepository) UpdateUser(ctx context.Context, username string, req UpdateUserRequest) (*User, error) {
	query := `
		UPDATE go_user_tbl2
		SET name = $1, email = $2, age = $3, updated_at = $4
		WHERE username = $5
		RETURNING username, name, email, age, created_at, updated_at
	`

	user := &User{}
	err := r.db.DB.QueryRowContext(ctx, query, req.Name, req.Email, req.Age, time.Now(), username).Scan(
		&user.Username,
		&user.Name,
		&user.Email,
		&user.Age,
		&user.CreatedAt,
		&user.UpdatedAt,
	)

	if err == sql.ErrNoRows {
		return nil, fmt.Errorf("user not found")
	}
	if err != nil {
		return nil, fmt.Errorf("error updating user: %w", err)
	}

	return user, nil
}

// DeleteUser deletes a user by username
func (r *UserRepository) DeleteUser(ctx context.Context, username string) error {
	query := `DELETE FROM go_user_tbl2 WHERE username = $1`

	result, err := r.db.DB.ExecContext(ctx, query, username)
	if err != nil {
		return fmt.Errorf("error deleting user: %w", err)
	}

	rowsAffected, err := result.RowsAffected()
	if err != nil {
		return fmt.Errorf("error checking rows affected: %w", err)
	}

	if rowsAffected == 0 {
		return fmt.Errorf("user not found")
	}

	return nil
}
