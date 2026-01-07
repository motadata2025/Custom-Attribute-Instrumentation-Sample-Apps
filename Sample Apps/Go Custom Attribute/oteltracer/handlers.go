package main

import (
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"strings"

	"go.opentelemetry.io/otel/attribute"
	"go.opentelemetry.io/otel/trace"
)

// UserHandler handles HTTP requests for user operations
type UserHandler struct {
	repo *UserRepository
}

// NewUserHandler creates a new user handler
func NewUserHandler(repo *UserRepository) *UserHandler {
	return &UserHandler{repo: repo}
}

// GetUser handles GET /users/{username}
func (h *UserHandler) GetUser(w http.ResponseWriter, r *http.Request) {
	fmt.Println("GetUser")

	// CRITICAL: Extract span from context AFTER auto-instrumentation has created it
	// The auto-instrumentation middleware has already created the span and stored it in r.Context()
	span := trace.SpanFromContext(r.Context())

	// Check if we got a valid span
	if !span.IsRecording() {
		log.Printf("WARNING: Span is not recording, custom attributes won't be added")
	}

	// Debug logging
	sc := span.SpanContext()
	log.Printf("DEBUG: Span Context - TraceID: %s, SpanID: %s, IsSampled: %v, IsValid: %v",
		sc.TraceID(), sc.SpanID(), sc.IsSampled(), sc.IsValid())

	// NOW add custom attributes to the SAME span created by auto-instrumentation
	span.SetAttributes(
		attribute.String("apm.http.method", r.Method),
		attribute.String("apm.http.url", r.URL.String()),
		attribute.String("apm.operation", "get_user"),
	)

	if r.Method != http.MethodGet {
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		return
	}

	username, err := extractUsernameFromPath(r.URL.Path)
	if err != nil {
		http.Error(w, "Invalid username", http.StatusBadRequest)
		return
	}

	// Add more attributes as we process
	span.SetAttributes(attribute.String("apm.user.username", username))

	user, err := h.repo.GetUserByUsername(r.Context(), username)
	if err != nil {
		if err.Error() == "user not found" {
			http.Error(w, "User not found", http.StatusNotFound)
			return
		}
		log.Printf("Error getting user: %v", err)
		span.RecordError(err)
		http.Error(w, "Error getting user", http.StatusInternalServerError)
		return
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(user)
}

// CreateUser handles POST /users
func (h *UserHandler) CreateUser(w http.ResponseWriter, r *http.Request) {
	// Extract the auto-instrumented span
	span := trace.SpanFromContext(r.Context())

	// Enrich with custom attributes
	span.SetAttributes(
		attribute.String("apm.http.method", r.Method),
		attribute.String("apm.http.url", r.URL.String()),
		attribute.String("apm.operation", "create_user"),
	)

	if r.Method != http.MethodPost {
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		return
	}

	var req CreateUserRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		http.Error(w, "Invalid request body", http.StatusBadRequest)
		return
	}

	span.SetAttributes(
		attribute.String("apm.user.username", req.Username),
		attribute.String("apm.user.email", req.Email),
	)

	if req.Username == "" || req.Name == "" || req.Email == "" || req.Age <= 0 {
		http.Error(w, "Username, name, email, and age are required", http.StatusBadRequest)
		return
	}

	user, err := h.repo.CreateUser(r.Context(), req)
	if err != nil {
		log.Printf("Error creating user: %v", err)
		span.RecordError(err)
		http.Error(w, "Error creating user", http.StatusInternalServerError)
		return
	}

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusCreated)
	json.NewEncoder(w).Encode(user)
}

// GetAllUsers handles GET /users
func (h *UserHandler) GetAllUsers(w http.ResponseWriter, r *http.Request) {
	span := trace.SpanFromContext(r.Context())
	span.SetAttributes(
		attribute.String("apm.http.method", r.Method),
		attribute.String("apm.http.url", r.URL.String()),
		attribute.String("apm.operation", "get_all_users"),
	)

	if r.Method != http.MethodGet {
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		return
	}

	users, err := h.repo.GetAllUsers(r.Context())
	if err != nil {
		log.Printf("Error getting users: %v", err)
		span.RecordError(err)
		http.Error(w, "Error getting users", http.StatusInternalServerError)
		return
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(users)
}

// UpdateUser handles PUT /users/{username}
func (h *UserHandler) UpdateUser(w http.ResponseWriter, r *http.Request) {
	span := trace.SpanFromContext(r.Context())
	span.SetAttributes(
		attribute.String("apm.http.method", r.Method),
		attribute.String("apm.http.url", r.URL.String()),
		attribute.String("apm.operation", "update_user"),
	)

	if r.Method != http.MethodPut {
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		return
	}

	username, err := extractUsernameFromPath(r.URL.Path)
	if err != nil {
		http.Error(w, "Invalid username", http.StatusBadRequest)
		return
	}

	span.SetAttributes(attribute.String("apm.user.username", username))

	var req UpdateUserRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		http.Error(w, "Invalid request body", http.StatusBadRequest)
		return
	}

	if req.Name == "" || req.Email == "" || req.Age <= 0 {
		http.Error(w, "Name, email, and age are required", http.StatusBadRequest)
		return
	}

	user, err := h.repo.UpdateUser(r.Context(), username, req)
	if err != nil {
		if err.Error() == "user not found" {
			http.Error(w, "User not found", http.StatusNotFound)
			return
		}
		log.Printf("Error updating user: %v", err)
		span.RecordError(err)
		http.Error(w, "Error updating user", http.StatusInternalServerError)
		return
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(user)
}

// DeleteUser handles DELETE /users/{username}
func (h *UserHandler) DeleteUser(w http.ResponseWriter, r *http.Request) {
	span := trace.SpanFromContext(r.Context())
	span.SetAttributes(
		attribute.String("apm.http.method", r.Method),
		attribute.String("apm.http.url", r.URL.String()),
		attribute.String("apm.operation", "delete_user"),
	)

	if r.Method != http.MethodDelete {
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		return
	}

	username, err := extractUsernameFromPath(r.URL.Path)
	if err != nil {
		http.Error(w, "Invalid username", http.StatusBadRequest)
		return
	}

	span.SetAttributes(attribute.String("apm.user.username", username))

	err = h.repo.DeleteUser(r.Context(), username)
	if err != nil {
		if err.Error() == "user not found" {
			http.Error(w, "User not found", http.StatusNotFound)
			return
		}
		log.Printf("Error deleting user: %v", err)
		span.RecordError(err)
		http.Error(w, "Error deleting user", http.StatusInternalServerError)
		return
	}

	w.WriteHeader(http.StatusNoContent)
}

func extractUsernameFromPath(path string) (string, error) {
	parts := strings.Split(strings.Trim(path, "/"), "/")
	if len(parts) < 2 {
		return "", http.ErrNotSupported
	}

	username := parts[1]
	if username == "" {
		return "", http.ErrNotSupported
	}

	return username, nil
}
