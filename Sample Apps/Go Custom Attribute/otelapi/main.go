package main

import (
	"fmt"
	"log"
	"net/http"
	"os"
	"strings"

	_ "otelapi/docs" // Import the generated docs package
	httpSwagger "github.com/swaggo/http-swagger/v2"
)

// @title User Management API
// @version 1.0
// @description This is a simple user management API.
// @host localhost:8080
// @BasePath /
// @schemes http


func main() {
	// Get database configuration from environment variables
	dbHost := getEnv("DB_HOST", "localhost")
	dbPort := getEnv("DB_PORT", "5432")
	dbUser := getEnv("DB_USER", "postgres")
	dbPassword := getEnv("DB_PASSWORD", "postgres")
	dbName := getEnv("DB_NAME", "postgres")
	serverPort := getEnv("PORT", "8080")

	// Initialize database
	db, err := NewDatabase(dbHost, dbPort, dbUser, dbPassword, dbName)
	if err != nil {
		log.Fatalf("Failed to connect to database: %v", err)
	}
	defer db.Close()

	// Initialize schema
	if err := db.InitSchema(); err != nil {
		log.Fatalf("Failed to initialize schema: %v", err)
	}

	// Initialize repository and handler
	userRepo := NewUserRepository(db)
	userHandler := NewUserHandler(userRepo)

	// Setup routes
	mux := http.NewServeMux()
	
	// User routes
	mux.HandleFunc("/users/", func(w http.ResponseWriter, r *http.Request) {
		username := strings.TrimPrefix(r.URL.Path, "/users/")
		if username == "" {
			// /users endpoint
			switch r.Method {
			case http.MethodGet:
				userHandler.GetAllUsers(w, r)
			case http.MethodPost:
				userHandler.CreateUser(w, r)
			default:
				http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
			}
		} else {
			// /users/{username} endpoint
			r.SetPathValue("username", username)
			switch r.Method {
			case http.MethodGet:
				userHandler.GetUser(w, r)
			case http.MethodPut:
				userHandler.UpdateUser(w, r)
			case http.MethodDelete:
				userHandler.DeleteUser(w, r)
			default:
				http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
			}
		}
	})

	// Health check endpoint
	mux.HandleFunc("/health", func(w http.ResponseWriter, r *http.Request) {
		w.WriteHeader(http.StatusOK)
		w.Write([]byte("OK"))
	})

	// Start server
	log.Printf("Starting server on port %s", serverPort)
	log.Printf("Database: %s@%s:%s/%s", dbUser, dbHost, dbPort, dbName)
	log.Println("Available endpoints:")
	log.Println("  GET    /health")
	log.Println("  GET    /users")
	log.Println("  POST   /users")
	log.Println("  GET    /users/{username}")
	log.Println("  PUT    /users/{username}")
	log.Printf("  GET    http://localhost:%s/swagger/", serverPort)
	mux.HandleFunc("/swagger/", httpSwagger.Handler(
		httpSwagger.URL(fmt.Sprintf("http://localhost:%s/swagger/doc.json", serverPort)),
	))

	if err := http.ListenAndServe(":"+serverPort, mux); err != nil {
		log.Fatalf("Server failed to start: %v", err)
	}
}

// getEnv gets an environment variable or returns a default value
func getEnv(key, defaultValue string) string {
	value := os.Getenv(key)
	if strings.TrimSpace(value) == "" {
		return defaultValue
	}
	return value
}

