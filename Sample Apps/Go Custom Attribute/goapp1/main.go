package main

import (
	"bufio"
	"context"
	"fmt"
	"log"
	"net/http"
	"os"
	"strings"

	_ "goapp1/docs" // change "goapp1" to your actual module name if different

	httpSwagger "github.com/swaggo/http-swagger/v2"
)

// @title User Management API
// @version 1.0
// @description This is a simple user management API with persistent PostgreSQL storage.
// @host localhost:8088
// @BasePath /
// @schemes http

func main() {
	// Load environment variables from .env file
	loadEnv()

	ctx := context.Background()

	// Get configuration from environment variables
	dbHost := getEnv("DB_HOST", "localhost")
	dbPort := getEnv("DB_PORT", "5432")
	dbUser := getEnv("DB_USER", "postgres")
	dbPassword := getEnv("DB_PASSWORD", "postgres")
	dbName := getEnv("DB_NAME", "postgres")
	serverPort := getEnv("PORT", "8088")

	// Initialize database
	db, err := NewDatabase(dbHost, dbPort, dbUser, dbPassword, dbName)
	if err != nil {
		log.Fatalf("Failed to connect to database: %v", err)
	}
	defer db.Close()

	// Initialize schema (table only — no dummy data)
	if err := db.InitSchema(ctx); err != nil {
		log.Fatalf("Failed to initialize schema: %v", err)
	}

	// Initialize repository and handler
	userRepo := NewUserRepository(db)
	userHandler := NewUserHandler(userRepo)

	// Setup routes
	mux := http.NewServeMux()

	// User routes
	mux.Handle("/users", userHandler)
	mux.Handle("/users/", userHandler)

	// Health check
	mux.HandleFunc("/health", func(w http.ResponseWriter, r *http.Request) {
		w.WriteHeader(http.StatusOK)
		w.Write([]byte("OK"))
	})

	// Swagger UI
	mux.Handle("/swagger/", httpSwagger.Handler(
		httpSwagger.URL(fmt.Sprintf("http://localhost:%s/swagger/doc.json", serverPort)),
	))

	// Start server
	log.Printf("Starting server on :%s", serverPort)
	log.Printf("Database: %s@%s:%s/%s", dbUser, dbHost, dbPort, dbName)
	log.Println("Available endpoints:")
	log.Println("  GET     /health")
	log.Println("  GET     /users")
	log.Println("  POST    /users")
	log.Println("  GET     /users/{username}")
	log.Println("  PUT     /users/{username}")
	log.Println("  DELETE  /users/{username}")
	log.Printf("  Swagger: http://localhost:%s/swagger/", serverPort)

	if err := http.ListenAndServe(":"+serverPort, mux); err != nil {
		log.Fatalf("Server failed to start: %v", err)
	}
}

// getEnv helper
func getEnv(key, defaultValue string) string {
	value := os.Getenv(key)
	if strings.TrimSpace(value) == "" {
		return defaultValue
	}
	return value
}

// loadEnv from .env file
func loadEnv() {
	file, err := os.Open(".env")
	if err != nil {
		return
	}
	defer file.Close()

	scanner := bufio.NewScanner(file)
	for scanner.Scan() {
		line := scanner.Text()
		if strings.TrimSpace(line) == "" || strings.HasPrefix(strings.TrimSpace(line), "#") {
			continue
		}
		parts := strings.SplitN(line, "=", 2)
		if len(parts) == 2 {
			key := strings.TrimSpace(parts[0])
			value := strings.TrimSpace(parts[1])
			if os.Getenv(key) == "" {
				os.Setenv(key, value)
			}
		}
	}
}
