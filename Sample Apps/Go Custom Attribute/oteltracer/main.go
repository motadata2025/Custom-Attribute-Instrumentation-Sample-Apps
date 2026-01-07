package main

import (
	"bufio"
	"context"
	"fmt"
	"log"
	"net/http"
	"os"
	"strings"

	_ "oteltracer/docs" // Import the generated docs package

	httpSwagger "github.com/swaggo/http-swagger/v2"
)

// @title User Management API
// @version 1.0
// @description This is a simple user management API.
// @host localhost:8081
// @BasePath /
// @schemes http

func main() {
	// Load environment variables from .env file
	loadEnv()

	// The user's zero-code instrumentation will handle OTel setup.
	ctx := context.Background()

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
	if err := db.InitSchema(ctx); err != nil {
		log.Fatalf("Failed to initialize schema: %v", err)
	}

	// Initialize repository and handler
	userRepo := NewUserRepository(db)
	userHandler := NewUserHandler(userRepo)
	tracedUserHandler := NewTracedUserHandler(userHandler)

	// Setup routes
	mux := http.NewServeMux()

	// User routes
	mux.Handle("/users/", tracedUserHandler)

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

// loadEnv reads the .env file and sets environment variables
func loadEnv() {
	file, err := os.Open(".env")
	if err != nil {
		// .env file might not exist, which is fine if env vars are set otherwise
		return
	}
	defer file.Close()

	scanner := bufio.NewScanner(file)
	for scanner.Scan() {
		line := scanner.Text()
		// Skip empty lines and comments
		if strings.TrimSpace(line) == "" || strings.HasPrefix(strings.TrimSpace(line), "#") {
			continue
		}

		// Split by first equals sign
		parts := strings.SplitN(line, "=", 2)
		if len(parts) == 2 {
			key := strings.TrimSpace(parts[0])
			value := strings.TrimSpace(parts[1])
			// Only set if not already set (optional, but good practice)
			if os.Getenv(key) == "" {
				os.Setenv(key, value)
			}
		}
	}
}
