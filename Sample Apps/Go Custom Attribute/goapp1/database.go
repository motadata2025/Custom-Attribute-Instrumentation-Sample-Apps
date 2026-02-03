package main

import (
	"context"
	"database/sql"
	"fmt"
	"log"

	"github.com/XSAM/otelsql"
	_ "github.com/lib/pq" // Underlying PostgreSQL driver
	semconv "go.opentelemetry.io/otel/semconv/v1.27.0"
)

// Database holds the database connection
type Database struct {
	DB *sql.DB
}

// NewDatabase creates a new database connection
func NewDatabase(host, port, user, password, dbname string) (*Database, error) {
	connStr := fmt.Sprintf("host=%s port=%s user=%s password=%s dbname=%s sslmode=disable",
		host, port, user, password, dbname)

	db, err := otelsql.Open("postgres", connStr,
		otelsql.WithAttributes(
			semconv.DBSystemPostgreSQL,
			semconv.DBNamespaceKey.String(dbname),
		),
	)
	if err != nil {
		return nil, fmt.Errorf("error opening database: %w", err)
	}

	if err := db.Ping(); err != nil {
		return nil, fmt.Errorf("error connecting to database: %w", err)
	}

	// Register DB stats metrics
	err = otelsql.RegisterDBStatsMetrics(db, otelsql.WithAttributes(
		semconv.DBSystemPostgreSQL,
		semconv.DBNamespaceKey.String(dbname),
	))
	if err != nil {
		log.Printf("Failed to register DB stats metrics: %v", err)
	}

	log.Println("Successfully connected to database")

	return &Database{DB: db}, nil
}

// InitSchema creates the table if it doesn't exist — no data is inserted
func (d *Database) InitSchema(ctx context.Context) error {
	query := `
	CREATE TABLE IF NOT EXISTS go_user_tbl2 (
		username  VARCHAR(50) PRIMARY KEY,
		name      VARCHAR(100) NOT NULL,
		email     VARCHAR(100) UNIQUE NOT NULL,
		age       INTEGER NOT NULL,
		created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
		updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
	);
	`

	_, err := d.DB.ExecContext(ctx, query)
	if err != nil {
		return fmt.Errorf("error creating schema: %w", err)
	}

	log.Println("Database schema initialized (persistent mode — no auto data insertion)")

	return nil
}

// Close closes the database connection
func (d *Database) Close() error {
	return d.DB.Close()
}
