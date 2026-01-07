# Node.js CRUD REST API

A RESTful API built with Node.js, Express.js, and PostgreSQL for user management.

## Features

- ✅ Full CRUD operations (Create, Read, Update, Delete)
- ✅ PostgreSQL database with `pg` package (no ORM)
- ✅ RESTful API design
- ✅ Swagger UI documentation
- ✅ CORS enabled
- ✅ Error handling with appropriate HTTP status codes
- ✅ Environment-based configuration

## Tech Stack

- **Runtime:** Node.js
- **Framework:** Express.js
- **Database:** PostgreSQL
- **Database Client:** pg (node-postgres)
- **Documentation:** Swagger UI

## Prerequisites

- Node.js (v14 or higher)
- PostgreSQL (v12 or higher)
- npm or yarn

## Installation

1. **Clone or navigate to the project directory:**
   ```bash
   cd oteltracer
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Set up environment variables:**
   - Copy `.env.example` to `.env`
   - Update the database credentials:
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` file:
   ```
   DB_HOST=localhost
   DB_PORT=5432
   DB_NAME=your_database_name
   DB_USER=your_database_user
   DB_PASSWORD=your_database_password
   PORT=8080
   ```

4. **Set up the database:**
   - Create a PostgreSQL database
   - Run the SQL script to create the table:
   ```bash
   psql -U your_database_user -d your_database_name -f db/init.sql
   ```

## Running the Application

**Development mode (with auto-reload):**
```bash
npm run dev
```

**Production mode:**
```bash
npm start
```

The server will start on `http://localhost:8080`

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/users` | Get all users |
| GET | `/users/:username` | Get user by username |
| POST | `/users` | Create new user |
| PUT | `/users/:username` | Update user |
| DELETE | `/users/:username` | Delete user |
| GET | `/health` | Health check endpoint |
| GET | `/swagger` | Swagger UI documentation |

## API Documentation

Access the interactive Swagger UI documentation at:
```
http://localhost:8080/swagger
```

## Example Requests

### Create a User
```bash
curl -X POST http://localhost:8080/users \
  -H "Content-Type: application/json" \
  -d '{
    "username": "johndoe",
    "email": "john@example.com",
    "full_name": "John Doe",
    "age": 30,
    "salary": 75000.50,
    "is_active": true,
    "tags": ["developer", "nodejs"]
  }'
```

### Get All Users
```bash
curl http://localhost:8080/users
```

### Get User by Username
```bash
curl http://localhost:8080/users/johndoe
```

### Update User
```bash
curl -X PUT http://localhost:8080/users/johndoe \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john.doe@example.com",
    "age": 31
  }'
```

### Delete User
```bash
curl -X DELETE http://localhost:8080/users/johndoe
```

## Project Structure

```
oteltracer/
├── config/
│   └── swagger.js          # Swagger configuration
├── controllers/
│   └── userController.js   # User controller logic
├── db/
│   ├── config.js           # Database connection
│   └── init.sql            # Database schema
├── docs/                   # OpenTelemetry documentation
│   ├── OPENTELEMETRY_CUSTOM_ATTRIBUTES.md
│   ├── QUICK_REFERENCE.md
│   └── README.md
├── models/
│   └── userModel.js        # User model with database queries
├── routes/
│   └── userRoutes.js       # User routes
├── .env.example            # Environment variables template
├── .gitignore              # Git ignore file
├── package.json            # Project dependencies
├── README.md               # Project documentation
└── server.js               # Main application file
```

## Error Handling

The API returns appropriate HTTP status codes:

- `200` - Success
- `201` - Created
- `400` - Bad Request
- `404` - Not Found
- `409` - Conflict (duplicate username)
- `500` - Internal Server Error

## License

ISC

