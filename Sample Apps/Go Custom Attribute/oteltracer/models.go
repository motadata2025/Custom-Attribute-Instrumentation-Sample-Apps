package main

import (
	"time"
)

// User represents a user in the system
type User struct {
	Username  string    `json:"username" example:"johndoe"`
	Name      string    `json:"name" example:"John Doe"`
	Email     string    `json:"email" example:"john.doe@example.com"`
	Age       int       `json:"age" example:30`
	CreatedAt time.Time `json:"created_at" example:"2023-10-27T10:00:00Z"`
	UpdatedAt time.Time `json:"updated_at" example:"2023-10-27T10:00:00Z"`
}

// CreateUserRequest represents the request body for creating a user
type CreateUserRequest struct {
	Username string `json:"username" example:"johndoe"`
	Name     string `json:"name" example:"John Doe"`
	Email    string `json:"email" example:"john.doe@example.com"`
	Age      int    `json:"age" example:30`
}

// UpdateUserRequest represents the request body for updating a user
type UpdateUserRequest struct {
	Name  string `json:"name" example:"John Doe Updated"`
	Email string `json:"email" example:"john.doe.updated@example.com"`
	Age   int    `json:"age" example:31`
}
