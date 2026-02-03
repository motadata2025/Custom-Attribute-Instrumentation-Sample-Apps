package main

import (
	"encoding/json"
	"fmt"
	"net/http"
	"strings"
)

// UserHandler handles HTTP requests for user operations
type UserHandler struct {
	repo *UserRepository
}

// NewUserHandler creates a new user handler
func NewUserHandler(repo *UserRepository) *UserHandler {
	return &UserHandler{repo: repo}
}

func (h *UserHandler) ServeHTTP(w http.ResponseWriter, r *http.Request) {
	path := strings.TrimPrefix(r.URL.Path, "/users")
	if path == "" || path == "/" {
		switch r.Method {
		case http.MethodGet:
			h.GetAllUsers(w, r)
		case http.MethodPost:
			h.CreateUser(w, r)
		default:
			http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		}
		return
	}

	// /users/{username}
	_, err := extractUsernameFromPath(r.URL.Path)
	if err != nil {
		http.Error(w, "Invalid path", http.StatusBadRequest)
		return
	}

	switch r.Method {
	case http.MethodGet:
		h.GetUser(w, r)
	case http.MethodPut:
		h.UpdateUser(w, r)
	case http.MethodDelete:
		h.DeleteUser(w, r)
	default:
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
	}
}

// GetUser godoc
// @Summary Get a user by username
// @Description Get details of a user by their username
// @Tags users
// @Accept json
// @Produce json
// @Param username path string true "Username of the user to get"
// @Success 200 {object} User
// @Failure 400 {string} string "Invalid path"
// @Failure 404 {string} string "User not found"
// @Failure 500 {string} string "Internal error"
// @Router /users/{username} [get]
func (h *UserHandler) GetUser(w http.ResponseWriter, r *http.Request) {
	username, _ := extractUsernameFromPath(r.URL.Path)

	user, err := h.repo.GetUserByUsername(r.Context(), username)
	if err != nil {
		if err.Error() == "user not found" {
			http.Error(w, "User not found", http.StatusNotFound)
			return
		}
		http.Error(w, "Internal error", http.StatusInternalServerError)
		return
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(user)
}

// CreateUser godoc
// @Summary Create a new user
// @Description Create a new user with the provided details
// @Tags users
// @Accept json
// @Produce json
// @Param user body CreateUserRequest true "User creation request"
// @Success 201 {object} User
// @Failure 400 {string} string "Invalid request body"
// @Failure 500 {string} string "Error creating user"
// @Router /users [post]
func (h *UserHandler) CreateUser(w http.ResponseWriter, r *http.Request) {
	var req CreateUserRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		http.Error(w, "Invalid request body", http.StatusBadRequest)
		return
	}

	user, err := h.repo.CreateUser(r.Context(), req)
	if err != nil {
		http.Error(w, "Error creating user (possibly duplicate username or email)", http.StatusInternalServerError)
		return
	}

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusCreated)
	json.NewEncoder(w).Encode(user)
}

// GetAllUsers godoc
// @Summary Get all users
// @Description Get a list of all registered users
// @Tags users
// @Accept json
// @Produce json
// @Success 200 {array} User
// @Failure 500 {string} string "Error getting users"
// @Router /users [get]
func (h *UserHandler) GetAllUsers(w http.ResponseWriter, r *http.Request) {
	users, err := h.repo.GetAllUsers(r.Context())
	if err != nil {
		http.Error(w, "Error getting users", http.StatusInternalServerError)
		return
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(users)
}

// UpdateUser godoc
// @Summary Update an existing user
// @Description Update details of an existing user by their username
// @Tags users
// @Accept json
// @Produce json
// @Param username path string true "Username of the user to update"
// @Param user body UpdateUserRequest true "User update request"
// @Success 200 {object} User
// @Failure 400 {string} string "Invalid request body or path"
// @Failure 404 {string} string "User not found"
// @Failure 500 {string} string "Error updating user"
// @Router /users/{username} [put]
func (h *UserHandler) UpdateUser(w http.ResponseWriter, r *http.Request) {
	username, _ := extractUsernameFromPath(r.URL.Path)

	var req UpdateUserRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		http.Error(w, "Invalid request body", http.StatusBadRequest)
		return
	}

	user, err := h.repo.UpdateUser(r.Context(), username, req)
	if err != nil {
		if err.Error() == "user not found" {
			http.Error(w, "User not found", http.StatusNotFound)
			return
		}
		http.Error(w, "Error updating user (possibly duplicate email)", http.StatusInternalServerError)
		return
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(user)
}

// DeleteUser godoc
// @Summary Delete a user
// @Description Delete a user by their username
// @Tags users
// @Accept json
// @Produce json
// @Param username path string true "Username of the user to delete"
// @Success 204 {string} string "No Content"
// @Failure 400 {string} string "Invalid path"
// @Failure 404 {string} string "User not found"
// @Failure 500 {string} string "Error deleting user"
// @Router /users/{username} [delete]
func (h *UserHandler) DeleteUser(w http.ResponseWriter, r *http.Request) {
	username, _ := extractUsernameFromPath(r.URL.Path)

	err := h.repo.DeleteUser(r.Context(), username)
	if err != nil {
		if err.Error() == "user not found" {
			http.Error(w, "User not found", http.StatusNotFound)
			return
		}
		http.Error(w, "Error deleting user", http.StatusInternalServerError)
		return
	}

	w.WriteHeader(http.StatusNoContent)
}

func extractUsernameFromPath(path string) (string, error) {
	parts := strings.Split(strings.Trim(path, "/"), "/")
	if len(parts) < 2 {
		return "", fmt.Errorf("invalid path")
	}
	username := parts[1]
	if username == "" {
		return "", fmt.Errorf("username is empty")
	}
	return username, nil
}
