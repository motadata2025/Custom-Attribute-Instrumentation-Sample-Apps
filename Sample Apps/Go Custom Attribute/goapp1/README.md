# User Management API (goapp1)

A simple User Management API written in Go, featuring persistent PostgreSQL storage and OpenTelemetry instrumentation for database operations.

## Features

*   **User Management**: Create, Read, Update, and Delete (CRUD) operations for users.
*   **PostgreSQL Integration**: Persistent storage using PostgreSQL.
*   **OpenTelemetry**: Database operations are instrumented using `otelsql`.
*   **Swagger UI**: Interactive API documentation.
*   **Health Check**: Endpoint to verify service status.

## Prerequisites

*   [Go](https://go.dev/) (version 1.24 or later)
*   [PostgreSQL](https://www.postgresql.org/)

## Configuration

The application is configured using environment variables. You can create a `.env` file in the root directory (or rely on the defaults).

| Variable | Description | Default |
| :--- | :--- | :--- |
| `DB_HOST` | Database host | `localhost` |
| `DB_PORT` | Database port | `5432` |
| `DB_USER` | Database user | `postgres` |
| `DB_PASSWORD` | Database password | `postgres` |
| `DB_NAME` | Database name | `postgres` |
| `PORT` | Server port | `8088` |

## Installation & Running

1.  **Navigate to the project directory**:
    ```bash
    cd goapp1
    ```

2.  **Install dependencies**:
    ```bash
    go mod download
    ```

3.  **Set up the database**:
    Ensure your PostgreSQL instance is running and the database specified in `DB_NAME` exists. The application will automatically create the `go_user_tbl2` table if it doesn't exist.

4.  **Run the application**:
    ```bash
    go run .
    ```

## API Endpoints

The server runs on `http://localhost:8088` by default.

*   **Health Check**: `GET /health`
*   **List Users**: `GET /users`
*   **Create User**: `POST /users`
*   **Get User**: `GET /users/{username}`
*   **Update User**: `PUT /users/{username}`
*   **Delete User**: `DELETE /users/{username}`

### Swagger Documentation

Interactive API documentation is available at:
`http://localhost:8088/swagger/`

## Project Structure

*   `main.go`: Entry point, server setup, and routing.
*   `database.go`: Database connection and schema initialization (using `otelsql`).
*   `handlers.go`: HTTP request handlers.
*   `models.go`: Data models.
*   `repository.go`: Database access logic.
*   `docs/`: Swagger documentation files.
