package main

import (
	"database/sql"
	"fmt"
	"log"

	_ "github.com/lib/pq"
)

// Database holds the database connection
type Database struct {
	DB *sql.DB
}

// NewDatabase creates a new database connection
func NewDatabase(host, port, user, password, dbname string) (*Database, error) {
	connStr := fmt.Sprintf("host=%s port=%s user=%s password=%s dbname=%s sslmode=disable",
		host, port, user, password, dbname)

	db, err := sql.Open("postgres", connStr)
	if err != nil {
		return nil, fmt.Errorf("error opening database: %w", err)
	}

	if err := db.Ping(); err != nil {
		return nil, fmt.Errorf("error connecting to database: %w", err)
	}

	log.Println("Successfully connected to database")

	return &Database{DB: db}, nil
}

// InitSchema creates the go_user_tbl table if it doesn't exist
func (d *Database) InitSchema() error {
	query := `
	CREATE TABLE IF NOT EXISTS go_user_tbl (
		username VARCHAR(50) PRIMARY KEY,
		name VARCHAR(100) NOT NULL,
		email VARCHAR(100) UNIQUE NOT NULL,
		age INTEGER NOT NULL,
		created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
		updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
	);
	`

	_, err := d.DB.Exec(query)
	if err != nil {
		return fmt.Errorf("error creating schema: %w", err)
	}

	log.Println("Database schema initialized")

	// Insert dummy data
	if err := d.insertDummyData(); err != nil {
		return fmt.Errorf("error inserting dummy data: %w", err)
	}

	return nil
}

// insertDummyData inserts dummy users if the table is empty
func (d *Database) insertDummyData() error {
	// Check if table has data
	var count int
	err := d.DB.QueryRow("SELECT COUNT(*) FROM go_user_tbl").Scan(&count)
	if err != nil {
		return err
	}

	// Only insert if table is empty
	if count > 0 {
		log.Println("Dummy data already exists, skipping insertion")
		return nil
	}

	dummyUsers := []struct {
		username string
		name     string
		email    string
		age      int
	}{
		{"johndoe", "John Doe", "john.doe@example.com", 30},
		{"janedoe", "Jane Doe", "jane.doe@example.com", 28},
		{"bobsmith", "Bob Smith", "bob.smith@example.com", 35},
		{"alicejones", "Alice Jones", "alice.jones@example.com", 25},
		{"charliebrwn", "Charlie Brown", "charlie.brown@example.com", 32},
	}

	for _, user := range dummyUsers {
		query := `
			INSERT INTO go_user_tbl (username, name, email, age, created_at, updated_at)
			VALUES ($1, $2, $3, $4, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
		`
		_, err := d.DB.Exec(query, user.username, user.name, user.email, user.age)
		if err != nil {
			return fmt.Errorf("error inserting user %s: %w", user.username, err)
		}
	}

	log.Println("Dummy data inserted successfully")
	return nil
}

// Close closes the database connection
func (d *Database) Close() error {
	return d.DB.Close()
}

